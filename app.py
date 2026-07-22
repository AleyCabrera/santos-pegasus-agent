"""
Aplicación Streamlit - Santos Pegasus Agente IA
Diseño moderno con sidebar, estadísticas y experiencia mejorada
"""
import streamlit as st
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importar módulos del agente
from src.agent import create_rag_chain, ask_question
from src.vectorstore import load_vector_store
from src.ingest import process_documents
from src.vectorstore import create_vector_store

# ============================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================
st.set_page_config(
    page_title="Santos Pegasus - Agente IA",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "Santos Pegasus Soluciones - Agente IA RAG v1.0.0"
    }
)

# ============================================
# CSS PERSONALIZADO MEJORADO
# ============================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    :root {
        --primary-color: #667eea;
        --secondary-color: #764ba2;
        --background-dark: #0f172a;
        --surface-dark: #1e293b;
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --error-color: #ef4444;
    }
    
    * { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }
    
    /* Fondo principal */
    .stApp {
        background: #f8fafc;
    }
    
    /* Ocultar elementos innecesarios */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    header {background: transparent !important;}
    
    /* Header principal */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        color: white;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        letter-spacing: -0.5px;
    }
    
    .main-header p {
        font-size: 1.1rem;
        color: rgba(255, 255, 255, 0.9);
        margin: 0.5rem 0 0 0;
        font-weight: 400;
    }
    
    /* Mensajes del usuario */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 14px 18px;
        border-radius: 18px 18px 4px 18px;
        margin: 8px 0;
        max-width: 80%;
        float: right;
        clear: both;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.25);
        line-height: 1.6;
        font-size: 0.95rem;
    }
    
    /* Mensajes del asistente */
    .assistant-message {
        background: #ffffff;
        color: #1e293b;
        padding: 14px 18px;
        border-radius: 18px 18px 18px 4px;
        margin: 8px 0;
        max-width: 80%;
        float: left;
        clear: both;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border-left: 4px solid #667eea;
        line-height: 1.6;
        font-size: 0.95rem;
    }
    
    .assistant-message strong {
        color: #4f46e5;
    }
    
    .message-container {
        display: flow-root;
        margin-bottom: 8px;
        animation: fadeIn 0.3s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Badges de fuentes */
    .source-badge {
        background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
        color: #4f46e5;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 500;
        display: inline-block;
        margin: 3px 5px 3px 0;
        border: 1px solid rgba(79, 70, 229, 0.15);
        transition: all 0.2s;
    }
    
    .source-badge:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(79, 70, 229, 0.15);
    }
    
    /* Sidebar */
    .sidebar-header {
        font-size: 0.9rem;
        font-weight: 600;
        color: #667eea;
        border-bottom: 2px solid #667eea;
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
        margin-top: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stats-card {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        color: #1e293b;
        padding: 10px 14px;
        border-radius: 10px;
        margin: 6px 0;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
        transition: all 0.2s;
        font-size: 0.9rem;
    }
    
    .stats-card:hover {
        transform: translateX(4px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.08);
    }
    
    .stats-card b {
        color: #1e293b;
        font-weight: 600;
    }
    
    .stats-card .value {
        color: #4f46e5;
        font-weight: 700;
        float: right;
    }
    
    /* Chat container */
    .chat-wrapper {
        background: rgba(255,255,255,0.6);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid #e2e8f0;
        min-height: 10px;
        box-shadow: 0 1px 10px rgba(0,0,0,0.04);
    }
    
    /* Input */
    .stChatInputContainer {
        padding-top: 1rem !important;
        border-top: 1px solid #e2e8f0 !important;
        margin-top: 0.5rem !important;
        background: transparent !important;
    }
    
    .stChatInputContainer textarea {
        border-radius: 12px !important;
        border: 2px solid #e2e8f0 !important;
        padding: 0.8rem 1.2rem !important;
        font-size: 0.95rem !important;
        background: #ffffff !important;
        color: #1e293b !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important;
    }
    
    .stChatInputContainer textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
        outline: none !important;
    }
    
    .stChatInputContainer textarea::placeholder {
        color: #94a3b8 !important;
    }
    
    .stChatInputContainer button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.6rem 1.5rem !important;
        color: white !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3) !important;
    }
    
    .stChatInputContainer button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
    }
    
    .stChatInputContainer button:active {
        transform: scale(0.97) !important;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-color: #667eea !important;
        border-top-color: transparent !important;
        border-width: 3px !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: transparent !important;
        color: #64748b !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        padding: 0.3rem 0 !important;
        border: none !important;
    }
    
    .streamlit-expanderContent {
        background: #f8fafc !important;
        border-radius: 8px !important;
        padding: 0.8rem !important;
        font-size: 0.8rem !important;
        color: #475569 !important;
        border: 1px solid #e2e8f0 !important;
    }
    
    /* Alertas */
    .stAlert {
        border-radius: 12px !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.06) !important;
    }
    
    /* Footer */
    .footer {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin-top: 1.5rem;
        border: 1px solid #e2e8f0;
    }
    
    .footer .footer-text {
        color: #64748b;
        font-size: 0.85rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 0.5rem;
    }
    
    .footer .highlight-text {
        color: #4f46e5;
        font-weight: 500;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #f1f5f9; border-radius: 4px; }
    ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
    
    /* Responsive */
    @media (max-width: 768px) {
        .user-message, .assistant-message { max-width: 95%; }
        .main-header h1 { font-size: 1.8rem; }
        .main-header { padding: 1.5rem; }
        .main-header p { font-size: 0.95rem; }
        .chat-wrapper { padding: 1rem; }
        .footer .footer-text { font-size: 0.75rem; flex-direction: column; text-align: center; }
    }
    
    @media (max-width: 480px) {
        .main-header h1 { font-size: 1.4rem; }
        .main-header { padding: 1rem; }
        .user-message, .assistant-message { 
            padding: 10px 14px;
            font-size: 0.85rem;
        }
        .chat-wrapper { padding: 0.8rem; }
        .stats-card { font-size: 0.8rem; padding: 8px 12px; }
        .sidebar-header { font-size: 0.8rem; }
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# FUNCIÓN DE INICIALIZACIÓN AUTOMÁTICA
# ============================================

def initialize_agent_auto():
    """
    Inicializa el agente RAG automáticamente.
    Si no existe vector store, lo crea desde los documentos.
    """
    logger.info("🔄 Inicializando agente RAG...")
    
    # 1. Verificar si existe el vector store
    vector_store = load_vector_store()
    
    if vector_store is None:
        logger.info("📂 No se encontró índice FAISS. Creando uno nuevo...")
        
        # Mostrar progreso al usuario
        with st.status("🚀 Inicializando el agente por primera vez...", expanded=True) as status:
            st.markdown("📄 **Procesando documentos internos...**")
            
            # 2. Procesar documentos
            chunks = process_documents()
            
            if not chunks:
                status.update(label="❌ Error: No se encontraron documentos", state="error")
                st.error("⚠️ No se encontraron documentos para procesar.")
                st.info("💡 Asegúrate de tener archivos PDF en la carpeta `data/documentos/`")
                return None
            
            st.markdown(f"✅ **{len(chunks)} chunks** generados correctamente")
            
            # 3. Crear vector store
            st.markdown("🧠 **Generando embeddings y creando índice de búsqueda...**")
            vector_store = create_vector_store(chunks, force_rebuild=True)
            
            if vector_store is None:
                status.update(label="❌ Error al crear el vector store", state="error")
                st.error("❌ Error al crear el índice de búsqueda.")
                return None
            
            status.update(label="✅ Agente inicializado correctamente", state="complete")
            st.success("🎉 ¡El agente está listo para usar!")
    
    # 4. Crear RAG chain
    chain = create_rag_chain()
    if chain is None:
        st.error("❌ Error al crear el agente RAG.")
        return None
    
    logger.info("✅ Agente inicializado correctamente")
    return chain

# ============================================
# FUNCIONES DE UTILIDAD
# ============================================

def display_message(role: str, content: str, sources: list = None):
    """Muestra un mensaje en el chat con formato mejorado"""
    if role == "user":
        st.markdown(f'''
        <div class="message-container">
            <div class="user-message">{content}</div>
        </div>
        ''', unsafe_allow_html=True)
    else:
        st.markdown(f'''
        <div class="message-container">
            <div class="assistant-message">{content}</div>
        </div>
        ''', unsafe_allow_html=True)
        
        if sources:
            st.markdown("**📚 Fuentes consultadas:**")
            sources_html = ""
            for source in sources[:3]:
                sources_html += f'<span class="source-badge">📄 {source}</span>'
            st.markdown(sources_html, unsafe_allow_html=True)
            if len(sources) > 3:
                st.caption(f"... y {len(sources) - 3} fuentes más")


def get_welcome_message():
    """Mensaje de bienvenida mejorado"""
    return """
    👋 **¡Hola! Soy el asistente virtual de Santos Pegasus Soluciones.**

    Puedo ayudarte con preguntas sobre:
    - 📋 **Onboarding** - Manual de incorporación
    - ⚙️ **Backend** - Guías de ingeniería
    - 🎨 **Frontend** - Estándares de desarrollo
    - 🚨 **Incidentes** - Protocolos de respuesta
    - 🏗️ **Arquitectura** - Microservicios

    **¿En qué puedo ayudarte hoy?** 🤔
    """

# ============================================
# INICIALIZACIÓN DEL ESTADO
# ============================================

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": get_welcome_message(), "sources": []}
    ]

if "k_value" not in st.session_state:
    st.session_state.k_value = 5

# ============================================
# SIDEBAR - CONFIGURACIÓN MEJORADA
# ============================================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; margin-bottom: 1.5rem;">
        <div style="font-size: 3rem; margin-bottom: 0.5rem;">🤖</div>
        <h2 style="color: #667eea; margin: 0; font-size: 1.3rem;">Santos Pegasus</h2>
        <p style="color: #94a3b8; font-size: 0.8rem; margin: 0.25rem 0 0 0;">Agente IA RAG</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="sidebar-header">⚙️ Configuración</div>', unsafe_allow_html=True)
    
    # Modelo LLM
    st.markdown("**🧠 Modelo LLM**")
    st.code("command-a-03-2025", language="bash")
    st.caption("Proveedor: Cohere Cloud")
    
    # Parámetros de búsqueda
    st.markdown("**📊 Parámetros de búsqueda**")
    st.session_state.k_value = st.slider(
        "Documentos recuperados (k)",
        min_value=1,
        max_value=10,
        value=st.session_state.k_value,
        help="Número de documentos a recuperar de la base vectorial"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        st.caption("🌡️ Temp: 0.3")
    with col2:
        st.caption("📏 Contexto: 128k")
    
    # Estadísticas
    st.markdown("---")
    st.markdown('<div class="sidebar-header">📊 Estadísticas</div>', unsafe_allow_html=True)
    
    # Contar documentos y chunks
    try:
        from src.config import DOCUMENTS_DIR
        doc_count = len(list(DOCUMENTS_DIR.glob("*.pdf")))
        msg_count = len(st.session_state.messages)
        
        st.markdown(f"""
        <div class="stats-card">📚 <b>Documentos:</b> <span class="value">{doc_count}</span></div>
        <div class="stats-card">💬 <b>Mensajes:</b> <span class="value">{msg_count}</span></div>
        <div class="stats-card">🧠 <b>Embeddings:</b> <span class="value">Cohere</span></div>
        """, unsafe_allow_html=True)
    except Exception as e:
        st.warning("No se pudieron obtener estadísticas completas")
    
    # Acciones
    st.markdown("---")
    st.markdown('<div class="sidebar-header">🛠️ Acciones</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧹 Limpiar chat", use_container_width=True):
            st.session_state.messages = [
                {"role": "assistant", "content": get_welcome_message(), "sources": []}
            ]
            st.success("✅ Historial limpiado")
            st.rerun()
    
    with col2:
        if st.button("🔄 Re-indexar", use_container_width=True):
            with st.spinner("🔄 Re-indexando documentos..."):
                try:
                    chunks = process_documents()
                    if chunks:
                        vector_store = create_vector_store(chunks, force_rebuild=True)
                        if vector_store:
                            st.success("✅ Re-indexación completada")
                            st.rerun()
                        else:
                            st.error("❌ Error en re-indexación")
                    else:
                        st.warning("⚠️ No se encontraron documentos")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
    
    # Información
    st.markdown("---")
    st.markdown('<div class="sidebar-header">ℹ️ Información</div>', unsafe_allow_html=True)
    st.caption("📌 Versión: 1.0.0")
    st.caption("🔒 100% Open Source")
    st.caption("🤖 Cohere Cloud")

# ============================================
# CONTENIDO PRINCIPAL
# ============================================

# --- HEADER ---
st.markdown("""
<div class="main-header">
    <h1>🤖 Santos Pegasus - Agente IA RAG</h1>
    <p>Asistente virtual con Retrieval Augmented Generation</p>
</div>
""", unsafe_allow_html=True)

# --- INICIALIZACIÓN DEL AGENTE ---
@st.cache_resource
def get_agent():
    """Obtiene el agente inicializado (cacheado)"""
    return initialize_agent_auto()

rag_chain = get_agent()

if rag_chain is None:
    st.error("""
    ❌ **No se pudo conectar con el servicio de chat.**
    
    Posibles causas:
    1. **Cohere**: La API Key no está configurada en los Secrets de Streamlit.
    2. **Vector Store**: No se pudo crear el índice FAISS.
    
    **Solución**: Revisa la configuración en `.streamlit/secrets.toml` y asegúrate de que la clave API sea correcta.
    """)
    st.stop()

# --- CHAT ---
st.markdown('<div class="chat-wrapper">', unsafe_allow_html=True)

# Mostrar mensajes existentes
for msg in st.session_state.messages:
    display_message(msg["role"], msg["content"], msg.get("sources", []))

st.markdown('</div>', unsafe_allow_html=True)

# --- INPUT ---
if prompt := st.chat_input("💬 Escribe tu pregunta sobre los documentos internos..."):
    # Mostrar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generar respuesta
    with st.chat_message("assistant"):
        with st.spinner("🤔 Pensando..."):
            if rag_chain:
                result = ask_question(rag_chain, prompt)
                
                if result["success"]:
                    response = result["answer"]
                    sources = []
                else:
                    response = result["answer"]
                    sources = []
            else:
                response = "❌ El agente no está disponible. Verifica la configuración."
                sources = []
            
            st.markdown(response)
            
            if sources:
                with st.expander("📚 Ver fuentes"):
                    for source in sources:
                        st.markdown(f"- {source}")
    
    st.session_state.messages.append({
        "role": "assistant",
        "content": response,
        "sources": sources
    })
    
    st.rerun()

# --- FOOTER ---
st.markdown(f"""
<div class="footer">
    <div class="footer-text">
        <span>
            <span class="highlight-text">⚡</span> command-a-03-2025
            <span style="margin-left: 1rem;" class="highlight-text">📚</span> k={st.session_state.k_value}
            <span style="margin-left: 1rem;" class="highlight-text">💡</span> LangChain + FAISS + Cohere
        </span>
        <span>v1.0.0</span>
    </div>
</div>
""", unsafe_allow_html=True)