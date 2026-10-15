import streamlit as st
from google import genai
from PIL import Image

# Configuración de la página para que se vea bien en el móvil
st.set_page_config(page_title="Asistente SMD Electrónica", page_icon="⚡", layout="centered")

st.title("⚡ Asistente de Reparación SMD")
st.write("Sube una foto clara de la placa y consulta tus dudas de electrónica.")

# Campo para introducir la API Key de forma segura
api_key = st.text_input("Introduce tu Clave de API de Gemini", type="password")

if not api_key:
    st.warning("Por favor, introduce tu clave de API para continuar.")
else:
    # Inicializar el cliente de Google GenAI
    client = genai.Client(api_key=api_key)

    # Subida de imagen de la placa SMD
    uploaded_file = st.file_uploader("Haz o sube una foto de la placa/componente SMD", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        # Mostramos la imagen adaptada al ancho de pantalla
        st.image(image, caption="Placa o componente a analizar", use_container_width=True)

    # Pregunta o síntoma del fallo
    user_query = st.text_area("¿Qué le pasa a la placa o qué componente quieres identificar?")

    if st.button("Consultar al Técnico IA", type="primary"):
        if not user_query and not uploaded_file:
            st.error("Por favor, añade al menos una foto o escribe una pregunta.")
        else:
            with st.spinner("Analizando componentes y trazas..."):
                try:
                    # Definimos el rol experto en electrónica SMD (System Prompt)
                    system_instruction = (
                        "Eres un técnico superior en electrónica experto en reparación de placas a nivel "
                        "de componentes SMD. Ayudas a identificar códigos de marcado superficial, interpretar "
                        "etapas de circuitos, calcular caídas de tensión y guiar paso a paso en el diagnóstico "
                        "de forma segura y técnica."
                    )

                    # Preparamos los contenidos para la IA
                    contents = []
                    if uploaded_file is not None:
                        contents.append(image)
                    
                    prompt_completo = f"{system_instruction}\n\nPregunta del técnico: {user_query}"
                    contents.append(prompt_completo)

                    # Llamada al modelo Gemini 2.5 Flash (rápido y multimodal)
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=contents
                    )

                    st.subheader("Respuesta del Asistente:")
                    st.write(response.text)

                except Exception as e:
                    st.error(f"Ha ocurrido un error al conectar con la IA: {e}")