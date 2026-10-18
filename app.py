import streamlit as st
from google import genai
from PIL import Image
from gtts import gTTS
import io
import base64

# Configuración de la página
st.set_page_config(page_title="Ingeniera Electrónica SMD - Asistente de Reparación", page_icon="👩‍🔧")

st.title(" Electrónica SMD - Asistente de Reparación")
st.write("Tu experta personal en microelectrónica con guiado paso a paso y voz real.")

# Obtener clave API desde los Secrets de Streamlit
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("No se ha encontrado la clave 'GEMINI_API_KEY' en los Secrets de Streamlit. Por favor confígurala en Advanced Settings.")
    st.stop()

# Inicializar cliente de Gemini
client = genai.Client(api_key=api_key)

# Inicializar el historial de chat en la sesión
if "messages" not in st.session_state:
    st.session_state.messages = []

# PROMPT DE INGENIERA ELECTRÓNICA EXPERTA Y MÉTODO PASO A PASO
SYSTEM_INSTRUCTION = (
    "Eres una Ingeniera Electrónica Senior especializada en diagnóstico y reparación a nivel de componente en placas SMD. "
    "Tu enfoque es sumamente metódico, riguroso, analítico y práctico. "
    "REGLA DE ORO DE DIAGNÓSTICO PASO A PASO:\n"
    "- NUNCA des todas las soluciones de golpe ni un listado largo de posibles fallos de principio a fin.\n"
    "- Indica ÚNICAMENTE EL PRIMER PASO de comprobación o medición (por ejemplo: configurar multímetro en continuidad, dónde poner las puntas en un componente de referencia).\n"
    "- Exige al usuario que realice la medida y te devuelva el resultado exacto (ej. valor en ohmios, caída de tensión o si pita o no).\n"
    "- ESPÉRATE a que el usuario te dé el resultado de esa medida en el siguiente mensaje antes de indicarle el siguiente paso de la ruta de reparación.\n"
    "- Si el usuario sube una foto, analiza las serigrafías (ej. R12, C304, U2), identifica posibles cortos, componentes desoldados o pistas dañadas y plantea la primera prueba técnica."
)

# Función para generar audio en formato Base64 HTML (evita bloqueos en móviles)
def generar_html_audio(texto):
    texto_limpio = texto.replace('*', '').replace('#', '').replace('`', '').replace('\n', ' ')
    tts = gTTS(text=texto_limpio, lang='es', slow=False)
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    b64 = base64.b64encode(fp.read()).decode()
    return f'<audio controls autoplay style="width: 100%;"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'

# Mostrar el historial de mensajes
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and "audio_html" in message:
            st.markdown(message["audio_html"], unsafe_allow_html=True)

# Subida opcional de imagen
uploaded_file = st.file_uploader("📸 Sube una placa o componente", type=["jpg", "jpeg", "png"])

image = None
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Placa cargada para análisis", use_column_width=True)

# Entrada de texto del usuario
user_query = st.chat_input("Escribe o dicta tu respuesta / resultado...")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    contents = [SYSTEM_INSTRUCTION]
    if image is not None:
        contents.append(image)

    historial_conversacion = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
    contents.append(f"Historial de la reparación:\n{historial_conversacion}\n\nResponde como la Ingeniera Electrónica guiando el siguiente paso:")

    with st.chat_message("assistant"):
        with st.spinner("La ingeniera está analizando el circuito y calculando el siguiente paso..."):
            try:
                response = client.models.generate_content(
                    model='gemini-3.8-flash',
                    contents=contents
                )
                ai_response = response.text
                st.markdown(ai_response)
                
                # Generar el reproductor HTML seguro
                audio_html = generar_html_audio(ai_response)
                st.markdown(audio_html, unsafe_allow_html=True)
                
                # Guardar en el historial
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": ai_response,
                    "audio_html": audio_html
                })
                
            except Exception as e:
                st.error(f"Ha ocurrido un error al conectar con la IA: {e}")
