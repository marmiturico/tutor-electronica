import streamlit as st
from google import genai
from PIL import Image

# Configuración de la página
st.set_page_config(page_title="Ingeniera Electrónica SMD - Tutor Experto", page_icon="👩‍🔧")

st.title("👩‍🔧 Ingeniera Electrónica SMD - Asistente de Reparación")
st.write("Tu experta personal en microelectrónica. Hablaremos paso a paso y esperaré tus mediciones.")

# Obtener clave API desde los Secrets de Streamlit
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("No se ha encontrado la clave 'GEMINI_API_KEY' en los Secrets de Streamlit. Por favor confígurala en Advanced Settings.")
    st.stop()

# Inicializar cliente de Gemini
client = genai.Client(api_key=api_key)

# 1. MEJORA DE VOZ: Añadir componente nativo de audio/voz de Streamlit si está disponible
st.info("💡 *Consejo de uso:* Puedes usar el micrófono integrado en el teclado de tu móvil para dictar tus respuestas y mediciones cómodamente.")

# Inicializar el historial de chat en la sesión para el flujo paso a paso
if "messages" not in st.session_state:
    st.session_state.messages = []

# 2. PROMPT DE INGENIERA ELECTRÓNICA EXPERTA Y MÉTODO PASO A PASO
SYSTEM_INSTRUCTION = (
    "Eres una Ingeniera Electrónica Senior especializada en diagnóstico y reparación a nivel de componente en placas SMD y todo tipo de electronica. "
    "Tu enfoque es sumamente metódico, riguroso, analítico y práctico. "
    "REGLA DE ORO DE DIAGNÓSTICO PASO A PASO:\n"
    "- NUNCA des todas las soluciones de golpe ni un listado largo de posibles fallos de principio a fin.\n"
    "- Indica ÚNICAMENTE EL PRIMER PASO de comprobación o medición (por ejemplo: configurar multímetro en continuidad, dónde poner las puntas en un componente de referencia).\n"
    "- Exige al usuario que realice la medida y te devuelva el resultado exacto (ej. valor en ohmios, caída de tensión o si pita o no).\n"
    "- ESPÉRATE a que el usuario te dé el resultado de esa medida en el siguiente mensaje antes de indicarle el siguiente paso de la ruta de reparación.\n"
    "- Si el usuario sube una foto, analiza las serigrafías (ej. R12, C304, U2), identifica posibles cortos, componentes desoldados o pistas dañadas y plantea la primera prueba técnica."
)

# Mostrar el historial de mensajes en pantalla
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Subida opcional de imagen en la barra lateral o en el panel principal
uploaded_file = st.file_uploader("📸 Sube una foto de la placa o componente (opcional para iniciar o cambiar de zona)", type=["jpg", "jpeg", "png"])

image = None
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Placa cargada para análisis", use_column_width=True)

# Entrada de texto del usuario (Chat interactivo)
user_query = st.chat_input("Escribe tu duda, describe el fallo o introduce el resultado de tu última medición...")

if user_query:
    # Añadir mensaje del usuario al historial
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    # Preparar el contenido para la IA incluyendo el historial de la conversación para mantener el hilo paso a paso
    contents = [SYSTEM_INSTRUCTION]
    
    # Si hay imagen nueva, la adjuntamos
    if image is not None:
        contents.append(image)

    # Construir el contexto histórico de la conversación para que la ingeniera recuerde por qué paso vamos
    historial_conversacion = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
    contents.append(f"Historial de la reparación:\n{historial_conversacion}\n\nResponde como la Ingeniera Electrónica guiando el siguiente paso:")

    # Generar respuesta de la IA
    with st.chat_message("assistant"):
        with st.spinner("La ingeniera está analizando el circuito y calculando el siguiente paso..."):
            try:
                response = client.models.generate_content(
                    model='gemini-3.8-flash',
                    contents=contents
                )
                ai_response = response.text
                st.markdown(ai_response)
                
                # Guardar la respuesta de la IA en el historial
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                
            except Exception as e:
                st.error(f"Ha ocurrido un error al conectar con la IA: {e}")
