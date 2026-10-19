
import streamlit as st
from datetime import date

st.set_page_config(
    page_title="InteresU Agent",
    page_icon="🎓",
    layout="wide"
)

# Configuración inicial
if "intereses" not in st.session_state:
    st.session_state.intereses = [
        "inglés", "tenis", "música", "tecnología"
    ]

if "profesores" not in st.session_state:
    st.session_state.profesores = []

if "correos" not in st.session_state:
    st.session_state.correos = [
        {
            "remitente": "Profesora Ana",
            "email": "ana@universidad.edu",
            "asunto": "Entrega del proyecto de inglés",
            "mensaje": "Recuerden entregar la actividad de inglés "
                       "antes del viernes.",
            "fecha": str(date.today()),
        },
        {
            "remitente": "Bienestar Universitario",
            "email": "bienestar@universidad.edu",
            "asunto": "Inscripciones al torneo de tenis",
            "mensaje": "Participa en el torneo de tenis de la universidad. "
                       "Inscripciones abiertas.",
            "fecha": str(date.today()),
        },
        {
            "remitente": "Comunicaciones Institucionales",
            "email": "comunicaciones@universidad.edu",
            "asunto": "Boletín informativo semanal",
            "mensaje": "Conoce las novedades, eventos y noticias "
                       "generales de nuestra institución.",
            "fecha": str(date.today()),
        },
    ]

st.title("🎓 InteresU Agent")
st.caption(
    "Tu asistente universitario: identifica los correos "
    "que merecen tu atención."
)

st.info(
    "Prototipo académico. Utiliza correos ficticios y reglas "
    "de clasificación. No accede a cuentas reales ni modifica correos."
)

# Barra lateral
with st.sidebar:
    st.header("⚙️ Mi configuración")

    nuevo_interes = st.text_input(
        "Agregar un interés",
        placeholder="Ej. programación"
    )

    if st.button("Agregar interés"):
        interes = nuevo_interes.strip().lower()
        if interes and interes not in st.session_state.intereses:
            st.session_state.intereses.append(interes)
            st.rerun()

    st.write("**Mis intereses:**")

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
        placeholder="profesor@universidad.edu"
    )

    if st.button("Registrar profesor"):
        if nombre.strip() and "@" in correo_profesor:
            profesor = {
                "nombre": nombre.strip(),
                "email": correo_profesor.strip().lower()
            }

            if not any(
                p["email"] == profesor["email"]
                for p in st.session_state.profesores
            ):
                st.session_state.profesores.append(profesor)
                st.success("Profesor registrado")
            else:
                st.warning("Ese correo ya está registrado")
        else:
            st.warning("Escribe un nombre y un correo válido")

    for profesor in st.session_state.profesores:
        st.caption(f'{profesor["nombre"]}: {profesor["email"]}')


# Clasificador por reglas
def clasificar_correo(correo):
    texto = (
        correo["asunto"] + " " + correo["mensaje"]
    ).lower()

    email_remitente = correo["email"].strip().lower()

    es_profesor = any(
        p["email"] == email_remitente
        for p in st.session_state.profesores
    )

    coincidencias = [
        interes for interes in st.session_state.intereses
        if interes.lower() in texto
    ]

    palabras_masivo = [
        "boletín", "boletin", "comunicado general",
        "toda la comunidad", "noticias generales",
        "información general", "informacion general"
    ]

    es_masivo = any(p in texto for p in palabras_masivo)

    if es_profesor:
        categoria = "👩‍🏫 Importante: profesor"
        razon = "El remitente está registrado como profesor."
    elif coincidencias:
        categoria = "🎯 Relacionado con mis intereses"
        razon = "Coincide con tus intereses: " + ", ".join(coincidencias)
    elif es_masivo:
        categoria = "📢 Aviso institucional"
        razon = "El contenido parece ser un aviso general."
    else:
        categoria = "📬 Informativo"
        razon = "No se encontraron coincidencias con tus intereses."

    if coincidencias and es_profesor:
        razon += " También coincide con tus intereses: " + ", ".join(
            coincidencias
        )

    return categoria, razon, es_profesor, coincidencias


# Pestañas principales
tab1, tab2, tab3 = st.tabs([
    "📨 Bandeja de prueba",
    "🧪 Probar un correo",
    "📊 Estadísticas y resumen"
])

with tab1:
    st.subheader("Bandeja de correos")

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

            if st.button("Eliminar correo de prueba", key=f"del_mail_{i}"):
                st.session_state.correos.pop(i)
                st.rerun()

with tab2:
    st.subheader("Prueba tu propio correo ficticio")

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

            st.session_state.correos.append(correo)
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

            st.caption(
                "La clasificación utiliza reglas y palabras clave, "
                "no un modelo avanzado de inteligencia artificial."
            )
        else:
            st.warning(
                "Completa el asunto, el mensaje y un correo válido."
            )

with tab3:
    st.subheader("Resumen de actividad")

    resultados = [
        clasificar_correo(c) for c in st.session_state.correos
    ]

    total = len(resultados)
    profesores = sum(1 for r in resultados if r[2])
    intereses = sum(1 for r in resultados if r[3])
    informativos = sum(
        1 for r in resultados
        if not r[2] and not r[3]
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Correos analizados", total)
    c2.metric("De profesores", profesores)
    c3.metric("Con intereses", intereses)
    c4.metric("Sin coincidencias", informativos)

    st.divider()
    st.subheader("📅 Resumen de fechas y entregas")

    palabras_fecha = [
        "entregar", "entrega", "fecha límite", "fecha limite",
        "examen", "parcial", "tarea", "actividad", "inscripción",
        "inscripcion", "viernes", "mañana", "manana"
    ]

    encontrados = 0

    for correo in st.session_state.correos:
        texto = (
            correo["asunto"] + " " + correo["mensaje"]
        ).lower()

        relevantes = [
            palabra for palabra in palabras_fecha
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
        "Este resumen detecta palabras relacionadas con actividades. "
        "Todavía no interpreta fechas límite complejas ni genera "
        "un resumen semanal mediante IA."
    )
