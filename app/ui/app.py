"""Interfaz de usuario con Streamlit para el agente RAG - Versión Mejorada y Corregida"""

import streamlit as st
import sys
from pathlib import Path

# ============================================
# CONFIGURACIÓN DE IMPORTACIONES
# ============================================
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.services.chat_service import ChatService
from app.services.indexing_service import IndexingService
from app.config import settings
from app.utils.logger import logger


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
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 16px 20px;
        border-radius: 20px 20px 4px 20px;
        margin: 12px 0;
        max-width: 80%;
        float: right;
        clear: both;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        line-height: 1.6;
        font-size: 0.95rem;
    }
    
    .assistant-message {
        background: #f8fafc;
        color: #1e293b;
        padding: 16px 20px;
        border-radius: 20px 20px 20px 4px;
        margin: 12px 0;
        max-width: 80%;
        float: left;
        clear: both;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 4px solid #667eea;
        line-height: 1.6;
        font-size: 0.95rem;
    }
    
    .message-container {
        display: flow-root;
        margin-bottom: 16px;
        animation: fadeIn 0.3s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .source-badge {
        background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
        color: #4f46e5;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
        display: inline-block;
        margin: 4px 6px 4px 0;
        border: 1px solid rgba(79, 70, 229, 0.2);
        transition: all 0.2s;
    }
    
    .source-badge:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(79, 70, 229, 0.2);
    }
    
    .sidebar-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: #667eea;
        border-bottom: 2px solid #667eea;
        padding-bottom: 0.75rem;
        margin-bottom: 1.5rem;
        margin-top: 1rem;
    }
    
    .stats-card {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        color: #1e293b;
        padding: 12px 16px;
        border-radius: 12px;
        margin: 8px 0;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: all 0.2s;
    }
    
    .stats-card:hover {
        transform: translateX(4px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .stats-card b {
        color: #1e293b;
        font-weight: 600;
    }
    
    .stTextInput > div > div > input {
        border-radius: 12px;
        border: 2px solid #e2e8f0;
        padding: 12px 20px;
        font-size: 0.95rem;
        transition: all 0.3s;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    .stButton > button {
        border-radius: 12px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.3s;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    .chat-container {
        background: #f8fafc;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        border: 1px solid #e2e8f0;
    }
    
    .footer {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin-top: 2rem;
        border: 1px solid #e2e8f0;
    }
    
    .stAlert {
        border-radius: 12px;
        border: none;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    @media (max-width: 768px) {
        .user-message, .assistant-message { max-width: 95%; }
        .main-header h1 { font-size: 1.8rem; }
        .main-header { padding: 1.5rem; }
    }
    
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: #f1f5f9; border-radius: 4px; }
    ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
</style>
""", unsafe_allow_html=True)


# ============================================
# FUNCIONES DE UTILIDAD
# ============================================

@st.cache_resource
def get_chat_service():
    """Obtiene el servicio de chat (cacheado)"""
    try:
        return ChatService()
    except Exception as e:
        st.error(f"❌ Error inicializando el servicio de chat: {e}")
        return None


@st.cache_resource
def get_indexing_service():
    """Obtiene el servicio de indexación (cacheado)"""
    try:
        return IndexingService()
    except Exception as e:
        st.error(f"❌ Error inicializando el servicio de indexación: {e}")
        return None


def display_message(role: str, content: str, sources: list = None):
    """Muestra un mensaje en el chat"""
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
    """Mensaje de bienvenida"""
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

if "chat_service" not in st.session_state:
    st.session_state.chat_service = get_chat_service()

if "k_value" not in st.session_state:
    st.session_state.k_value = 5


# ============================================
# SIDEBAR - CONFIGURACIÓN MEJORADA
# ============================================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <div style="font-size: 3rem; margin-bottom: 0.5rem;">🤖</div>
        <h2 style="color: #667eea; margin: 0; font-size: 1.5rem;">Santos Pegasus</h2>
        <p style="color: #94a3b8; font-size: 0.85rem; margin: 0.25rem 0 0 0;">Agente IA RAG</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="sidebar-header">⚙️ Configuración</div>', unsafe_allow_html=True)
    
    # Modelo dinámico
    st.markdown("**🧠 Modelo LLM**")
    llm_provider = getattr(settings, 'LLM_PROVIDER', 'ollama').lower()

    if llm_provider == "ollama":
        model_name = getattr(settings, 'OLLAMA_MODEL', 'llama3.2:3b')
        st.code(model_name, language="bash")
        st.caption("Proveedor: Ollama (Local)")
    elif llm_provider == "huggingface":
        model_name = getattr(settings, 'HF_MODEL', 'mistralai/Mistral-7B-Instruct-v0.2')
        st.code(model_name, language="bash")
        st.caption("Proveedor: Hugging Face")
    elif llm_provider == "groq":
        model_name = getattr(settings, 'GROQ_MODEL', 'llama3-8b-8192')
        st.code(model_name, language="bash")
        st.caption("Proveedor: Groq Cloud")
    else:
        model_name = getattr(settings, 'OLLAMA_MODEL', 'llama3.2:3b')
        st.code(model_name, language="bash")
        st.caption(f"Proveedor: {llm_provider.title()} (Default: Ollama)")

    # Parámetros
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
        st.caption(f"🌡️ Temp: {getattr(settings, 'OLLAMA_TEMPERATURE', 0.7)}")
    with col2:
        st.caption(f"📏 Contexto: {getattr(settings, 'OLLAMA_CONTEXT_WINDOW', 2048)}")
    
    # Estadísticas
    st.markdown("---")
    st.markdown('<div class="sidebar-header">📊 Estadísticas</div>', unsafe_allow_html=True)
    
    if st.session_state.chat_service:
        try:
            stats = st.session_state.chat_service.get_stats()
            st.markdown(f"""
            <div class="stats-card">📚 <b>Documentos:</b> {stats.get('documents_in_store', 0)}</div>
            <div class="stats-card">💬 <b>Mensajes:</b> {stats.get('history_length', 0)}</div>
            <div class="stats-card">🤖 <b>Modelo:</b> {stats.get('model', 'N/A')[:20]}</div>
            <div class="stats-card">🧠 <b>Embeddings:</b> {stats.get('embedding_model', 'N/A')[:20]}</div>
            """, unsafe_allow_html=True)
        except Exception:
            st.warning("No se pudieron obtener estadísticas")
    
    # Acciones
    st.markdown("---")
    st.markdown('<div class="sidebar-header">🛠️ Acciones</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧹 Limpiar", use_container_width=True, help="Limpiar historial"):
            if st.session_state.chat_service:
                st.session_state.chat_service.clear_history()
                st.session_state.messages = [
                    {"role": "assistant", "content": get_welcome_message(), "sources": []}
                ]
                st.success("✅ Historial limpiado")
                st.rerun()
    
    with col2:
        if st.button("🔄 Re-indexar", use_container_width=True, help="Re-indexar documentos"):
            try:
                with st.spinner("Re-indexando..."):
                    indexer = get_indexing_service()
                    result = indexer.reindex()
                    st.success(f"✅ {result.get('total_added', 0)} chunks")
                    st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
    
    # Información dinámica
    st.markdown("---")
    st.markdown('<div class="sidebar-header">ℹ️ Información</div>', unsafe_allow_html=True)
    st.caption(f"📌 Versión: {settings.APP_VERSION}")
    st.caption("🔒 100% Open Source")
    
    provider_display = "Ollama Local" if llm_provider == "ollama" else f"{llm_provider.title()} Cloud"
    st.caption(f"🤖 {provider_display}")


# ============================================
# CONTENIDO PRINCIPAL
# ============================================

st.markdown("""
<div class="main-header">
    <h1>🤖 Santos Pegasus - Agente IA RAG</h1>
    <p>Asistente virtual con Retrieval Augmented Generation</p>
</div>
""", unsafe_allow_html=True)

# Verificar conexión
if st.session_state.chat_service is None:
    st.error("""
    ❌ **No se pudo conectar con el servicio de chat.**
    Verifica que:
    1. Las variables de entorno (Secrets) estén configuradas correctamente en Streamlit Cloud.
    2. El token de API (HF_TOKEN o GROQ_API_KEY) sea válido y tenga permisos.
    3. Si estás ejecutando localmente con Ollama, que esté corriendo (`ollama serve`).
    """)
    st.stop()


# ============================================
# CHAT MEJORADO
# ============================================

st.markdown('<div class="chat-container">', unsafe_allow_html=True)

for msg in st.session_state.messages:
    display_message(msg["role"], msg["content"], msg.get("sources"))

st.markdown('</div>', unsafe_allow_html=True)


# ============================================
# INPUT DE PREGUNTAS
# ============================================

question = st.chat_input("Escribe tu pregunta aquí...", key="chat_input")

if question:
    # 1. Agregar y mostrar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": question})
    display_message("user", question)
    
    # 2. Generar respuesta
    try:
        with st.spinner("🤔 Pensando..."):
            response = st.session_state.chat_service.ask(
                question=question,
                k=st.session_state.k_value,
                include_history=True
            )
        
        # 3. Agregar y mostrar respuesta del asistente
        st.session_state.messages.append({
            "role": "assistant",
            "content": response.answer,
            "sources": response.sources
        })
        display_message("assistant", response.answer, response.sources)
        
        # Nota: st.rerun() se eliminó porque Streamlit ya rerunea automáticamente 
        # después de st.chat_input, y llamamos a display_message manualmente arriba.
        
    except Exception as e:
        st.error(f"❌ Error generando respuesta: {e}")
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"Lo siento, ocurrió un error: {str(e)}",
            "sources": []
        })
        display_message("assistant", f"Lo siento, ocurrió un error: {str(e)}", [])


# ============================================
# FOOTER MEJORADO
# ============================================
st.markdown(f"""
<div class="footer">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
        <div style="color: #64748b; font-size: 0.9rem;">
            <span style="margin-right: 1.5rem;">⚡ {model_name}</span>
            <span style="margin-right: 1.5rem;">📚 k={st.session_state.k_value}</span>
            <span>💡 LangChain + FAISS + {llm_provider.title()}</span>
        </div>
        <div style="color: #94a3b8; font-size: 0.85rem; margin-top: 0.5rem;">
            v{settings.APP_VERSION}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)