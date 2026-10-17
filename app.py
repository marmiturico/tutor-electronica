import streamlit as st
from google import genai
from PIL import Image
import os

# Configuración de la página
st.set_page_config(page_title="Tutor de Electrónica SMD", page_icon="🔬")

st.title("🔬 Tutor de Electrónica SMD")
st.write("Sube una foto de la placa o componente SMD y realiza tu consulta técnica.")

# Obtener clave API desde los Secrets de Streamlit
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("No se ha encontrado la clave 'GEMINI_API_KEY' en los Secrets de Streamlit. Por favor confígurala en Advanced Settings.")
    st.stop()

# Inicializar cliente de Gemini
client = genai.Client(api_key=api_key)

# Subida de imagen
uploaded_file = st.file_uploader("Cargar imagen de la placa o componente", type=["jpg", "jpeg", "png"])

image = None
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Imagen cargada", use_column_width=True)

# Entrada de texto del técnico
user_query = st.text_input("¿Qué necesitas comprobar o diagnosticar?", placeholder="Ej: ¿Cómo mido la resistencia R12?")

if st.button("Analizar"):
    if not user_query and uploaded_file is None:
        st.warning("Por favor, sube una foto o escribe una pregunta.")
    else:
        system_instruction = (
            "Eres un experto tutor en reparación de electrónica SMD. "
            "Analiza las imágenes de placas de circuito impreso o componentes que se te proporcionen. "
            "Responde con explicaciones claras, precisas y paso a paso. "
            "Si el usuario pregunta cómo medir un componente: "
            "1. Indica el modo en que se debe configurar el multímetro (Ohmios, Diodo, Continuidad, etc.). "
            "2. Indica el componente de referencia cercano. "
            "3. Especifica exactamente dónde colocar la punta roja y la negra del multímetro. "
            "4. Indica el valor esperado."
        )

        contents = []
        if image is not None:
            contents.append(image)

        prompt_completo = f"{system_instruction}\n\nPregunta del técnico: {user_query}"
        contents.append(prompt_completo)

        # Generar respuesta con la IA
        with st.chat_message("assistant"):
            with st.spinner("Analizando componentes y trazas..."):
                try:
                    response = client.models.generate_content(
                        model='gemini-3.8-flash',
                        contents=contents
                    )
                    st.write(response.text)
                except Exception as e:
                    st.error(f"Ha ocurrido un error al conectar con la IA: {e}")
