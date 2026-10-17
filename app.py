import streamlit as st
from google import genai
from PIL import Image

st.set_page_config(page_title="Asistente SMD Electrónica", layout="wide")

st.title("Asistente de Electrónica SMD")
st.write("Sube una foto de tu placa y mantén una conversación fluida con el técnico de IA.")

# 1. Configurar el cliente de Gemini
import os

api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)
# 2. Inicializar el historial de chat en la sesión si no existe
if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. Mostrar los mensajes anteriores del chat en pantalla
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "image" in message and message["image"]:
            st.image(message["image"], width=300)

# 4. Zona para subir la foto y escribir la consulta abajo
uploaded_file = st.file_uploader("Sube una placa o componente a analizar", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Imagen cargada", width=300)

# 5. Cuadro de texto del chat (para escribir las órdenes una detrás de otra)
if user_query := st.chat_input("¿Qué le pasa a la placa o dónde quieres medir?"):
    
    # Guardar y mostrar el mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": user_query, "image": uploaded_file})
    with st.chat_message("user"):
        st.markdown(user_query)
        if uploaded_file:
            st.image(image, width=300)

    # Definir el rol experto en electrónica SMD
    system_instruction = (
        "Eres un técnico superior en electrónica experto en reparación SMD. "
        "Al indicar dónde medir, NUNCA dibujes mapas, esquemas conceptuales ni diagramas ascii. "
        "Guiarás al usuario usando EXCLUSIVAMENTE referencias visuales sobre la propia foto subida. "
        "Estructura tus indicaciones paso a paso:\n"
        "1. Identifica la zona o cuadrante de la imagen.\n"
        "2. Indica el componente de referencia cercano.\n"
        "3. Especifica exactamente dónde colocar la punta roja y la negra del multímetro.\n"
        "4. Indica el valor esperado."
    )

    contents = []
    if uploaded_file is not None:
        contents.append(image)
    
    prompt_completo = f"{system_instruction}\n\nPregunta del técnico: {user_query}"
    contents.append(prompt_completo)

    # Generar respuesta con la IA
    with st.chat_message("assistant"):
        with st.spinner("Analizando componentes y trazas..."):
            try:
                response = client.models.generate_content(
                    model='gemini-flash-latest',
                    contents=contents
                )
                respuesta_texto = response.text
            except Exception as e:
                st.error(f"Ha ocurrido un error al conectar con la IA: {e}")
