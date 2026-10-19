
import base64
import hashlib
import hmac
import json
import secrets
from datetime import date
from email.utils import parseaddr

import streamlit as st
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


st.set_page_config(
    page_title="InteresU Agent",
    page_icon="🎓",
    layout="wide",
)

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


# ---------------- CONFIGURACION ----------------

if "intereses" not in st.session_state:
    st.session_state.intereses = [
        "inglés",
        "tenis",
        "música",
        "tecnología",
    ]

if "profesores" not in st.session_state:
    st.session_state.profesores = []

if "correos" not in st.session_state:
    st.session_state.correos = [
        {
            "remitente": "Profesora Ana",
            "email": "ana@universidad.edu",
            "asunto": "Entrega del proyecto de inglés",
            "mensaje": "Entregar la actividad de inglés antes del viernes.",
            "fecha": str(date.today()),
        },
        {
            "remitente": "Bienestar Universitario",
            "email": "bienestar@universidad.edu",
            "asunto": "Inscripciones al torneo de tenis",
            "mensaje": "Participa en el torneo de tenis de la universidad.",
            "fecha": str(date.today()),
        },
        {
            "remitente": "Comunicaciones Institucionales",
            "email": "comunicaciones@universidad.edu",
            "asunto": "Boletín informativo semanal",
            "mensaje": "Noticias generales y eventos de la institución.",
            "fecha": str(date.today()),
        },
    ]

if "fuente_correos" not in st.session_state:
    st.session_state.fuente_correos = "demo"


# ---------------- CONEXION CON GOOGLE ----------------

def crear_flujo(state=None):
    config = st.secrets["gmail"]

    client_config = {
        "web": {
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [config["redirect_uri"]],
        }
    }

    flujo = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        state=state,
    )

    flujo.redirect_uri = config["redirect_uri"]

    return flujo


def crear_estado_oauth():
    """Genera un estado firmado para validar el regreso de Google."""
    config = st.secrets["gmail"]
    nonce = secrets.token_urlsafe(32)

    firma = hmac.new(
        config["client_secret"].encode("utf-8"),
        nonce.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    return f"{nonce}.{firma}"


def validar_estado_oauth(estado):
    """Verifica la firma del estado recibido desde Google."""
    if not estado or "." not in estado:
        return False

    try:
        nonce, firma_recibida = estado.rsplit(".", 1)
        config = st.secrets["gmail"]

        firma_esperada = hmac.new(
            config["client_secret"].encode("utf-8"),
            nonce.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(
            firma_recibida,
            firma_esperada,
        )

    except Exception:
        return False


def procesar_respuesta_google():
    parametros = st.query_params

    codigo = parametros.get("code")
    estado = parametros.get("state")
    error_google = parametros.get("error")

    if error_google:
        st.session_state.error_google = (
            f"Google no completó la autorización: {error_google}"
        )
        st.query_params.clear()
        return

    if not codigo:
        return

    if not validar_estado_oauth(estado):
        st.session_state.error_google = (
            "No se pudo validar el estado de autorización. "
            "Inicia una conexión nueva con Gmail."
        )
        st.query_params.clear()
        return

    try:
        flujo = crear_flujo(state=estado)

        # No se utiliza PKCE en este flujo web.
        flujo.fetch_token(code=codigo)

        st.session_state.gmail_token = (
            flujo.credentials.to_json()
        )

        st.session_state.pop("error_google", None)
        st.session_state.pop("oauth_url", None)

        st.query_params.clear()
        st.rerun()

    except Exception as error:
        st.session_state.error_google = (
            "No se pudo completar la conexión con Google. "
            f"Detalle: {type(error).__name__}: {error}"
        )
        st.query_params.clear()


def obtener_credenciales():
    token = st.session_state.get("gmail_token")

    if not token:
        return None

    try:
        credenciales = Credentials.from_authorized_user_info(
            json.loads(token),
            SCOPES,
        )

        if credenciales.expired and credenciales.refresh_token:
            credenciales.refresh(Request())
            st.session_state.gmail_token = (
                credenciales.to_json()
            )

        if not credenciales.valid:
            return None

        return credenciales

    except Exception:
        st.session_state.pop("gmail_token", None)
        return None


def extraer_texto(parte):
    mime = parte.get("mimeType", "")
    cuerpo = parte.get("body", {}).get("data")

    if mime == "text/plain" and cuerpo:
        datos = base64.urlsafe_b64decode(cuerpo)
        return datos.decode("utf-8", errors="replace")

    textos = []

    for subparte in parte.get("parts", []):
        textos.append(extraer_texto(subparte))

    return "\n".join(texto for texto in textos if texto)


def cargar_correos_gmail(credenciales, limite=25):
    servicio = build(
        "gmail",
        "v1",
        credentials=credenciales,
        cache_discovery=False,
    )

    respuesta = (
        servicio.users()
        .messages()
        .list(
            userId="me",
            maxResults=limite,
        )
        .execute()
    )

    correos = []

    for elemento in respuesta.get("messages", []):
        mensaje = (
            servicio.users()
            .messages()
            .get(
                userId="me",
                id=elemento["id"],
                format="full",
            )
            .execute()
        )

        encabezados_lista = (
            mensaje.get("payload", {}).get("headers", [])
        )

        encabezados = {
            encabezado["name"].lower(): encabezado["value"]
            for encabezado in encabezados_lista
        }

        nombre, email = parseaddr(
            encabezados.get("from", "")
        )

        cuerpo = extraer_texto(
            mensaje.get("payload", {})
        )

        if not cuerpo:
            cuerpo = mensaje.get("snippet", "")

        correos.append({
            "remitente": nombre or email or "Remitente desconocido",
            "email": email.lower(),
            "asunto": encabezados.get("subject", "(Sin asunto)"),
            "mensaje": cuerpo[:12000],
            "fecha": encabezados.get("date", "Fecha desconocida"),
        })

    return correos


# Procesar el regreso de Google antes de mostrar la interfaz.
try:
    procesar_respuesta_google()
except Exception as error:
    st.session_state.error_google = (
        "No se pudo procesar la respuesta de Google. "
        f"Detalle: {type(error).__name__}: {error}"
    )


# ---------------- CLASIFICADOR ----------------

def clasificar_correo(correo):
    texto = (
        correo["asunto"] + " " + correo["mensaje"]
    ).lower()

    email_remitente = correo["email"].strip().lower()

    es_profesor = any(
        profesor["email"] == email_remitente
        for profesor in st.session_state.profesores
    )

    coincidencias = [
        interes
        for interes in st.session_state.intereses
        if interes.lower() in texto
    ]

    palabras_masivo = [
        "boletín",
        "boletin",
        "comunicado general",
        "toda la comunidad",
        "noticias generales",
        "información general",
        "informacion general",
    ]

    es_masivo = any(
        palabra in texto for palabra in palabras_masivo
    )

    if es_profesor:
        categoria = "👩‍🏫 Importante: profesor"
        razon = "El remitente está registrado como profesor."

    elif coincidencias:
        categoria = "🎯 Relacionado con mis intereses"
        razon = "Coincide con tus intereses: " + ", ".join(
            coincidencias
        )

    elif es_masivo:
        categoria = "📢 Aviso institucional"
        razon = "El contenido parece ser un aviso general."

    else:
        categoria = "📬 Informativo"
        razon = "No se encontraron coincidencias con tus intereses."

    if coincidencias and es_profesor:
        razon += (
            " También coincide con tus intereses: "
            + ", ".join(coincidencias)
        )

    return categoria, razon, es_profesor, coincidencias


# ---------------- INTERFAZ ----------------

st.title("🎓 InteresU Agent")
st.caption(
    "Tu asistente universitario: identifica los correos "
    "que merecen tu atención."
)

if st.session_state.fuente_correos == "gmail":
    st.success(
        "Bandeja cargada desde Gmail. Modo de solo lectura."
    )
else:
    st.info("Estás viendo correos ficticios de demostración.")


with st.sidebar:
    st.header("📧 Conexión con Gmail")

    if "error_google" in st.session_state:
        st.error(st.session_state.error_google)

    credenciales = obtener_credenciales()

    if credenciales:
        st.success("Gmail conectado")

        if st.button("Actualizar correos de Gmail"):
            try:
                with st.spinner("Consultando tus correos..."):
                    st.session_state.correos = (
                        cargar_correos_gmail(credenciales)
                    )
                    st.session_state.fuente_correos = "gmail"

                st.success(
                    f"Se cargaron {len(st.session_state.correos)} correos."
                )
                st.rerun()

            except HttpError as error:
                st.error(
                    "Gmail rechazó la consulta. Revisa los permisos "
                    f"de la API. Detalle: {error}"
                )

            except Exception as error:
                st.error(
                    "No se pudieron cargar los correos. "
                    f"Detalle: {type(error).__name__}: {error}"
                )

        if st.button("Desconectar Gmail"):
            st.session_state.pop("gmail_token", None)
            st.session_state.pop("oauth_url", None)
            st.session_state.correos = []
            st.session_state.fuente_correos = "demo"
            st.rerun()

    else:
        st.caption(
            "Autoriza Google para consultar tus mensajes. "
            "La aplicación solicita permiso de solo lectura."
        )

        if "gmail" in st.secrets:
            try:
                flujo = crear_flujo()
                estado = crear_estado_oauth()

                url, _ = flujo.authorization_url(
                    state=estado,
                    access_type="offline",
                    include_granted_scopes="true",
                    prompt="consent select_account",
                )

                st.link_button(
                    "Conectar Gmail con Google",
                    url,
                    use_container_width=True,
                )

            except Exception as error:
                st.error(
                    "No se pudo preparar la conexión OAuth. "
                    f"Detalle: {type(error).__name__}: {error}"
                )

        else:
            st.warning("Falta la sección [gmail] en los Secrets.")

    st.divider()
    st.header("⚙️ Mi configuración")

    nuevo_interes = st.text_input(
        "Agregar un interés",
        placeholder="Ej. programación",
    )

    if st.button("Agregar interés"):
        interes = nuevo_interes.strip().lower()

        if interes and interes not in st.session_state.intereses:
            st.session_state.intereses.append(interes)
            st.rerun()

    for interes in st.session_state.intereses:
        col1, col2 = st.columns([4, 1])
        col1.write(f"• {interes}")

        if col2.button("✖", key=f"del_{interes}"):
            st.session_state.intereses.remove(interes)
            st.rerun()

    st.divider()
    st.subheader("👩‍🏫 Mis profesores")

    nombre = st.text_input("Nombre del profesor")
    correo_profesor = st.text_input(
        "Correo del profesor",
        placeholder="profesor@universidad.edu",
    )

    if st.button("Registrar profesor"):
        if nombre.strip() and "@" in correo_profesor:
            profesor = {
                "nombre": nombre.strip(),
                "email": correo_profesor.strip().lower(),
            }

            if not any(
                registrado["email"] == profesor["email"]
                for registrado in st.session_state.profesores
            ):
                st.session_state.profesores.append(profesor)
                st.success("Profesor registrado")
            else:
                st.warning("Ese correo ya está registrado")
        else:
            st.warning("Escribe un nombre y un correo válido")

    for profesor in st.session_state.profesores:
        st.caption(
            f'{profesor["nombre"]}: {profesor["email"]}'
        )


# ---------------- PESTAÑAS ----------------

tab1, tab2, tab3 = st.tabs([
    "📨 Bandeja de correos",
    "🧪 Probar un correo",
    "📊 Estadísticas y resumen",
])


# ---------------- BANDEJA DE CORREOS ----------------

with tab1:
    st.subheader("Bandeja de correos")

    if not st.session_state.correos:
        st.write("No hay correos cargados. Actualiza la bandeja.")

    else:
        for i, correo in enumerate(st.session_state.correos):
            categoria, razon, _, _ = clasificar_correo(correo)

            with st.expander(
                f'{categoria} | {correo["asunto"]}'
            ):
                st.write(f'**De:** {correo["remitente"]}')
                st.write(f'**Correo:** {correo["email"]}')
                st.write(f'**Fecha:** {correo["fecha"]}')
                st.write(f'**Mensaje:** {correo["mensaje"]}')
                st.write(f'**¿Por qué se clasificó así?** {razon}')

                if st.session_state.fuente_correos == "demo":
                    if st.button(
                        "Eliminar correo de prueba",
                        key=f"del_mail_{i}",
                    ):
                        st.session_state.correos.pop(i)
                        st.rerun()


# ---------------- PROBAR UN CORREO ----------------

with tab2:
    st.subheader("Probar un correo")

    with st.form("form_correo"):
        remitente = st.text_input("Nombre del remitente")
        email = st.text_input("Correo del remitente")
        asunto = st.text_input("Asunto del correo")
        mensaje = st.text_area("Contenido del correo")
        enviar = st.form_submit_button("Analizar correo")

    if enviar:
        if asunto.strip() and mensaje.strip() and "@" in email:
            correo = {
                "remitente": remitente.strip() or email.strip(),
                "email": email.strip().lower(),
                "asunto": asunto.strip(),
                "mensaje": mensaje.strip(),
                "fecha": str(date.today()),
            }

            categoria, razon, es_profesor, coincidencias = (
                clasificar_correo(correo)
            )

            st.success("Análisis completado")
            st.subheader(categoria)
            st.write("**Explicación:**", razon)

            if es_profesor:
                st.write("**Prioridad:** Alta, por remitente registrado.")
            elif coincidencias:
                st.write("**Prioridad:** Según tus intereses.")
            else:
                st.write("**Prioridad:** Normal.")

        else:
            st.warning(
                "Completa el asunto, el mensaje y un correo válido."
            )


# ---------------- ESTADISTICAS Y RESUMEN ----------------

with tab3:
    st.subheader("Resumen de actividad")

    resultados = [
        clasificar_correo(correo)
        for correo in st.session_state.correos
    ]

    total = len(resultados)
    profesores = sum(1 for resultado in resultados if resultado[2])
    intereses = sum(1 for resultado in resultados if resultado[3])
    informativos = sum(
        1 for resultado in resultados
        if not resultado[2] and not resultado[3]
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Correos analizados", total)
    c2.metric("De profesores", profesores)
    c3.metric("Con intereses", intereses)
    c4.metric("Sin coincidencias", informativos)

    st.divider()
    st.subheader("📅 Posibles fechas y entregas")

    palabras_fecha = [
        "entregar",
        "entrega",
        "fecha límite",
        "fecha limite",
        "examen",
        "parcial",
        "tarea",
        "actividad",
        "inscripción",
        "inscripcion",
        "viernes",
        "mañana",
        "manana",
    ]

    encontrados = 0

    for correo in st.session_state.correos:
        texto = (
            correo["asunto"] + " " + correo["mensaje"]
        ).lower()

        relevantes = [
            palabra
            for palabra in palabras_fecha
            if palabra in texto
        ]

        if relevantes:
            encontrados += 1
            st.write(f'**{correo["asunto"]}**')
            st.caption(
                f'Fecha del correo: {correo["fecha"]} · '
                f'Palabras detectadas: {", ".join(relevantes)}'
            )

    if encontrados == 0:
        st.write("No se detectaron posibles entregas o actividades.")

    st.caption(
        "La clasificación y el resumen utilizan reglas y palabras "
        "clave; todavía no son un modelo avanzado de IA."
    )
