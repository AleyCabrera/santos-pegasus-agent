"""
Aplicación Streamlit - Interfaz del agente
"""
import streamlit as st
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Santos Pegasus - Agente IA",
    page_icon="🚀",
    layout="centered"
)

# Título principal
st.title("🚀 Santos Pegasus Soluciones")
st.subheader("Agente de IA para Documentación Interna")

# Mensaje de bienvenida
st.markdown("""
Bienvenido al agente conversacional de Santos Pegasus Soluciones.
Pregunta sobre nuestros manuales, guías y protocolos internos.
""")

# Estado inicial
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar historial
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input del usuario
if prompt := st.chat_input("Pregunta sobre los documentos internos..."):
    # Mostrar mensaje del usuario
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # TODO: Integrar con el agente (Fase 2)
    with st.chat_message("assistant"):
        with st.spinner("Consultando documentos..."):
            # Respuesta temporal
            response = "Funcionalidad en desarrollo. El agente responderá aquí."
            st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})