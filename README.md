# 🎓 InteresU Agent

**Asistente universitario para organizar y clasificar correos electrónicos según los intereses y las necesidades del estudiante.**

🌐 **Aplicación desplegada:** https://interesu-agent.streamlit.app/  
💻 **Repositorio:** https://github.com/Stiven89/InteresU-Agent

---

## 📌 1. Descripción del proyecto

InteresU Agent es una aplicación web desarrollada en Python que busca facilitar la organización de los correos electrónicos que recibe un estudiante universitario.

La idea surgió de una situación cotidiana: recibir muchos correos de profesores, actividades académicas, avisos institucionales y otros temas puede dificultar la identificación de los mensajes importantes.

Por eso, la aplicación permite clasificar correos utilizando información del remitente, palabras clave y los intereses registrados por el usuario. También cuenta con una interfaz para probar correos, consultar estadísticas y visualizar posibles entregas o actividades.

El objetivo es seguir mejorando el proyecto hasta convertirlo en un asistente universitario más completo, capaz de ayudar a priorizar la información académica.

## 🎯 2. Objetivos

### Objetivo general

Desarrollar una aplicación web que facilite la organización y clasificación de correos universitarios, ayudando al estudiante a identificar información relevante de manera sencilla.

### Objetivos específicos

- Crear una interfaz web sencilla e intuitiva.
- Permitir que el usuario registre sus intereses personales y académicos.
- Registrar profesores para reconocer los correos provenientes de ellos.
- Clasificar mensajes según reglas y palabras clave.
- Mostrar estadísticas y posibles actividades académicas.
- Explorar la integración con Gmail mediante su API oficial.
- Publicar la aplicación en una plataforma accesible desde internet.

## 🛠️ 3. Tecnologías utilizadas

| Tecnología | Uso en el proyecto |
|---|---|
| Python | Lenguaje principal de programación. |
| Streamlit | Desarrollo de la interfaz web. |
| Google Gmail API | Consulta de correos mediante la API oficial. |
| Google OAuth 2.0 | Autorización de acceso a la cuenta de Google. |
| Google Auth | Gestión de credenciales y autorización. |
| Git y GitHub | Control de versiones y almacenamiento del código. |
| Streamlit Community Cloud | Despliegue y publicación de la aplicación. |

## ✨ 4. Funcionalidades desarrolladas

### 📬 Bandeja de correos

Permite visualizar mensajes de demostración y consultar la clasificación asignada a cada correo.

### 🎯 Clasificación por intereses

El usuario puede registrar intereses como programación, inglés, música o deportes. La aplicación busca coincidencias entre esos intereses y el asunto o contenido del mensaje.

### 👩‍🏫 Registro de profesores

Permite registrar el nombre y correo electrónico de profesores. Cuando un mensaje coincide con uno de esos remitentes, se clasifica como importante por proceder de un profesor registrado.

### 🧪 Prueba manual de correos

Incluye un formulario para ingresar el remitente, el asunto y el contenido de un correo. Después, la aplicación muestra la categoría y la explicación de la clasificación.

### 📊 Estadísticas y resumen

Presenta indicadores sobre los correos analizados, los mensajes de profesores, las coincidencias con intereses y los mensajes sin coincidencias.

También busca palabras relacionadas con entregas, tareas, exámenes y actividades para mostrar posibles pendientes académicos.

### ☁️ Publicación en internet

La aplicación está desplegada en Streamlit Community Cloud y el código fuente se encuentra alojado en GitHub.

## 🧠 5. ¿Cómo funciona la clasificación?

La versión actual utiliza un sistema de reglas y coincidencias de texto.

El proceso general es el siguiente:

1. La aplicación recibe o consulta un correo.
2. Obtiene el remitente, el asunto y el contenido.
3. Compara el correo del remitente con los profesores registrados.
4. Busca palabras relacionadas con los intereses del usuario.
5. Revisa algunas expresiones asociadas con avisos institucionales.
6. Asigna una categoría y muestra una explicación.

Las categorías principales son:

- **Importante: profesor.** El remitente está registrado como profesor.
- **Relacionado con mis intereses.** El mensaje contiene palabras relacionadas con los intereses registrados.
- **Aviso institucional.** Se detectan expresiones asociadas con comunicaciones generales.
- **Informativo.** No se encuentran coincidencias con las reglas anteriores.

La clasificación tiene un enfoque inicial y puede mejorarse para reconocer el contexto de los mensajes con mayor precisión.

## 📧 6. Integración con Gmail

Se trabajó en la integración con la API oficial de Gmail para permitir que el usuario autorice su cuenta de Google y consulte sus mensajes.

La configuración contempla los siguientes elementos:

- Activación de Gmail API en Google Cloud.
- Creación de un cliente OAuth para una aplicación web.
- Configuración de la URL de redirección.
- Registro de las credenciales en los Secrets de Streamlit Cloud.
- Solicitud de acceso de solo lectura a Gmail.

El alcance solicitado para la API utiliza el permiso:

`https://www.googleapis.com/auth/gmail.readonly`

Este permiso permite consultar mensajes sin solicitar permisos para enviar, modificar o eliminar correos.

### Estado actual de la integración

La configuración inicial de Google Cloud y la URL de redirección se realizaron. Sin embargo, durante las pruebas de autorización se presentó un problema con el parámetro `code_verifier` del flujo OAuth.

Por esta razón, **la conexión completa con Gmail todavía está pendiente de corrección y validación**. La publicación de la aplicación no significa que esta integración ya funcione correctamente.

Mientras se completa esa parte, se puede continuar trabajando con los correos de demostración y las funcionalidades disponibles en la interfaz.

## 🚀 7. Despliegue de la aplicación

El proyecto se publicó utilizando Streamlit Community Cloud y se vinculó con el repositorio de GitHub.

Dirección pública:

https://interesu-agent.streamlit.app/

El proceso general de despliegue es:

1. Crear el proyecto y organizar el código en GitHub.
2. Incluir el archivo `app.py` con la aplicación.
3. Crear el archivo `requirements.txt` con las dependencias.
4. Vincular el repositorio desde Streamlit Community Cloud.
5. Configurar los Secrets necesarios para las integraciones.
6. Publicar la aplicación y comprobar su funcionamiento.

Cuando se realizan cambios en el repositorio, Streamlit Cloud puede detectar las actualizaciones y ejecutar un nuevo despliegue.

## 💻 8. Instalación local

### Requisitos previos

- Python instalado.
- Git instalado.
- Acceso al repositorio del proyecto.

### Clonar el repositorio

```bash
git clone https://github.com/Stiven89/InteresU-Agent.git
cd InteresU-Agent
```

### Crear un entorno virtual

En Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Instalar las dependencias

El archivo `requirements.txt` contiene las librerías principales:

```text
streamlit
google-api-python-client
google-auth
google-auth-httplib2
google-auth-oauthlib
```

Instalarlas con:

```bash
pip install -r requirements.txt
```

### Ejecutar la aplicación

```bash
streamlit run app.py
```

Streamlit mostrará la dirección local desde la cual se puede abrir la aplicación en el navegador.

Para probar las funcionalidades básicas no es necesario conectar Gmail. La integración requiere una configuración OAuth válida.

## 🔐 9. Configuración y seguridad

Las credenciales de Google no deben guardarse directamente en el código fuente ni publicarse en GitHub.

En Streamlit Community Cloud se utiliza la sección **Settings → Secrets** para configurar los datos de OAuth.

La estructura esperada es:

```toml
[gmail]
client_id = "TU_CLIENT_ID"
client_secret = "TU_CLIENT_SECRET"
redirect_uri = "https://interesu-agent.streamlit.app/"
```

Los valores deben reemplazarse por las credenciales reales de la aplicación.

**Importante:** nunca publicar el `client_secret`, tokens de acceso, tokens de actualización ni archivos que contengan credenciales personales.

La integración con Gmail debe probarse con una cuenta autorizada y los permisos mínimos necesarios.

## 🧪 10. Pruebas y validación

Durante el desarrollo se han realizado comprobaciones y ajustes sobre la interfaz, la clasificación y el despliegue.

| Prueba | Estado |
|---|---|
| Apertura de la aplicación web publicada | Disponible |
| Visualización de correos de demostración | Implementada |
| Registro de intereses | Implementado |
| Registro de profesores | Implementado |
| Clasificación mediante reglas | Implementada |
| Análisis manual de un correo | Implementado |
| Visualización de estadísticas | Implementada |
| Detección de palabras relacionadas con actividades | Implementada |
| Configuración inicial de Google Cloud OAuth | Realizada |
| Conexión completa y lectura de Gmail | Pendiente de corregir y validar |

Los resultados de las pruebas deben actualizarse a medida que se comprueben nuevas versiones de la aplicación.

## ⚠️ 11. Limitaciones actuales

- La clasificación se basa en reglas y coincidencias de palabras, no en un modelo avanzado de inteligencia artificial.
- La detección de posibles fechas y entregas es aproximada y no garantiza identificar todos los compromisos académicos.
- La conexión con Gmail presenta un inconveniente pendiente en el flujo de autorización OAuth.
- En esta versión no existe una base de datos persistente para almacenar la configuración del usuario.
- Las funcionalidades de demostración permiten probar la interfaz, pero no representan mensajes reales de una cuenta de Gmail.

## 🔮 12. Mejoras futuras

- Corregir y validar completamente la autorización OAuth de Gmail.
- Incorporar almacenamiento persistente para los intereses, profesores y preferencias.
- Mejorar la clasificación mediante técnicas de procesamiento de lenguaje natural.
- Detectar fechas límite con mayor precisión.
- Permitir filtrar los correos por prioridad, categoría y fecha.
- Incorporar notificaciones para actividades académicas importantes.
- Mejorar la experiencia en dispositivos móviles.
- Añadir pruebas automatizadas y validaciones de seguridad.

## 👨‍💻 13. Estado del proyecto

**InteresU Agent se encuentra en una etapa inicial de desarrollo funcional.**

La aplicación cuenta con una interfaz publicada, clasificación básica de correos, configuración de intereses, registro de profesores y estadísticas. La integración con Gmail continúa en proceso de ajuste.

El proyecto permite aplicar conocimientos de Python, desarrollo web, consumo de APIs, autenticación, control de versiones y despliegue de aplicaciones.

---

**Desarrollado como proyecto de aprendizaje en desarrollo de software.**
