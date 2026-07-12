"""Interfaz de usuario con Streamlit para el agente RAG"""

import streamlit as st
import sys
from pathlib import Path
import time

# ============================================
# CONFIGURACIÓN DE IMPORTACIONES
# ============================================
# Agregar la raíz del proyecto al path de Python
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Ahora podemos importar correctamente
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
    initial_sidebar_state="expanded"
)

# ============================================
# CSS PERSONALIZADO
# ============================================
st.markdown("""
<style>
    /* Estilo principal */
    .main-header {
        background: linear-gradient(90deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        margin: 0;
        color: #e0e0e0;
    }
    
    .main-header p {
        font-size: 1rem;
        color: #aaa;
        margin: 0.5rem 0 0 0;
    }
    
    /* Chat messages */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 18px;
        border-radius: 18px 18px 4px 18px;
        margin: 8px 0;
        max-width: 80%;
        float: right;
        clear: both;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    .assistant-message {
        background: #f0f2f6;
        color: #1a1a2e;
        padding: 12px 18px;
        border-radius: 18px 18px 18px 4px;
        margin: 8px 0;
        max-width: 80%;
        float: left;
        clear: both;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        border-left: 4px solid #667eea;
    }
    
    .message-container {
        display: flow-root;
        margin-bottom: 10px;
    }
    
    /* Fuentes */
    .source-badge {
        background: #e8f0fe;
        color: #1a73e8;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        display: inline-block;
        margin: 2px 4px;
    }
    
    /* Sidebar */
    .sidebar-header {
        font-size: 1.2rem;
        font-weight: bold;
        color: #667eea;
        border-bottom: 2px solid #667eea;
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }
    
    .stats-card {
        background: #f8f9fa;
        padding: 10px 15px;
        border-radius: 8px;
        margin: 5px 0;
        border-left: 3px solid #667eea;
    }
    
    /* Input */
    .stTextInput > div > div > input {
        border-radius: 25px;
        border: 2px solid #667eea;
        padding: 10px 20px;
    }
    
    .stButton > button {
        border-radius: 25px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 10px 30px;
        font-weight: bold;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .user-message, .assistant-message {
            max-width: 95%;
        }
        .main-header h1 {
            font-size: 1.8rem;
        }
    }
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
    container = st.container()
    
    with container:
        if role == "user":
            st.markdown(f'<div class="message-container"><div class="user-message">{content}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="message-container"><div class="assistant-message">{content}</div></div>', unsafe_allow_html=True)
            
            # Mostrar fuentes si existen
            if sources:
                st.markdown("**📚 Fuentes:**")
                for source in sources[:3]:
                    st.markdown(f'<span class="source-badge">📄 {source}</span>', unsafe_allow_html=True)
                if len(sources) > 3:
                    st.caption(f"... y {len(sources) - 3} fuentes más")


def display_chat_history():
    """Muestra el historial de conversación"""
    if "messages" in st.session_state:
        for msg in st.session_state.messages:
            display_message(msg["role"], msg["content"], msg.get("sources"))


def get_welcome_message():
    """Mensaje de bienvenida"""
    return """
    👋 **¡Hola! Soy el asistente virtual de Santos Pegasus Soluciones.**

    Puedo ayudarte con preguntas sobre:
    - 📋 **Onboarding** - Manual de incorporación
    - 🔧 **Backend** - Guías de ingeniería
    - 🎨 **Frontend** - Estándares de desarrollo
    - 🚨 **Incidentes** - Protocolos de respuesta
    - 🏗️ **Arquitectura** - Microservicios

    **¿Qué necesitas saber?** 🤔
    """


# ============================================
# INICIALIZACIÓN DEL ESTADO
# ============================================

# Inicializar estado de la sesión
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": get_welcome_message(), "sources": []}
    ]

if "chat_service" not in st.session_state:
    st.session_state.chat_service = get_chat_service()

if "k_value" not in st.session_state:
    st.session_state.k_value = 5


# ============================================
# SIDEBAR - CONFIGURACIÓN
# ============================================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/artificial-intelligence.png", width=80)
    st.markdown('<div class="sidebar-header">🤖 Configuración</div>', unsafe_allow_html=True)
    
    # Modelo
    st.markdown("**🧠 Modelo LLM**")
    st.code(settings.OLLAMA_MODEL, language="bash")
    st.caption(f"Host: {settings.OLLAMA_HOST}")
    
    # Parámetros
    st.markdown("**⚙️ Parámetros de búsqueda**")
    st.session_state.k_value = st.slider(
        "Documentos recuperados (k)",
        min_value=1,
        max_value=10,
        value=st.session_state.k_value,
        help="Número de documentos a recuperar de la base vectorial"
    )
    
    st.caption(f"🌡️ Temperatura: {settings.OLLAMA_TEMPERATURE}")
    st.caption(f"📏 Contexto: {settings.OLLAMA_CONTEXT_WINDOW}")
    
    # Estadísticas
    st.markdown("---")
    st.markdown('<div class="sidebar-header">📊 Estadísticas</div>', unsafe_allow_html=True)
    
    if st.session_state.chat_service:
        try:
            stats = st.session_state.chat_service.get_stats()
            
            st.markdown(f"""
            <div class="stats-card">
                📚 <b>Documentos en store:</b> {stats.get('documents_in_store', 0)}
            </div>
            <div class="stats-card">
                💬 <b>Mensajes en historial:</b> {stats.get('history_length', 0)}
            </div>
            <div class="stats-card">
                🤖 <b>Modelo:</b> {stats.get('model', 'N/A')}
            </div>
            <div class="stats-card">
                📏 <b>Dimensión embeddings:</b> {stats.get('embedding_model', 'N/A')}
            </div>
            """, unsafe_allow_html=True)
        except Exception as e:
            st.warning(f"No se pudieron obtener estadísticas: {e}")
    
    # Acciones
    st.markdown("---")
    st.markdown("**🛠️ Acciones**")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧹 Limpiar historial", use_container_width=True):
            if st.session_state.chat_service:
                st.session_state.chat_service.clear_history()
                st.session_state.messages = [
                    {"role": "assistant", "content": get_welcome_message(), "sources": []}
                ]
                st.success("✅ Historial limpiado!")
                st.rerun()
    
    with col2:
        if st.button("🔄 Re-indexar", use_container_width=True):
            try:
                with st.spinner("🔄 Re-indexando documentos..."):
                    indexer = get_indexing_service()
                    result = indexer.reindex()
                    st.success(f"✅ Re-indexación completada! {result.get('total_added', 0)} chunks agregados")
                    st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {e}")
    
    # Información
    st.markdown("---")
    st.markdown("**ℹ️ Información**")
    st.caption(f"📌 Versión: {settings.APP_VERSION}")
    st.caption("🔒 100% Open Source - Ollama Local")


# ============================================
# CONTENIDO PRINCIPAL
# ============================================

# Header
st.markdown("""
<div class="main-header">
    <h1>🤖 Santos Pegasus - Agente IA RAG</h1>
    <p>Asistente virtual con Retrieval Augmented Generation (RAG)</p>
</div>
""", unsafe_allow_html=True)

# Verificar conexión con Ollama
if st.session_state.chat_service is None:
    st.error("""
    ❌ **No se pudo conectar con el servicio de chat.**
    
    Verifica que:
    1. Ollama esté ejecutándose (`ollama serve`)
    2. El modelo esté descargado (`ollama pull llama3.2:3b`)
    3. La configuración en `.env` sea correcta
    """)
    st.stop()


# ============================================
# CHAT
# ============================================

# Mostrar historial de mensajes
chat_container = st.container()

with chat_container:
    # Crear scrollable container
    chat_scroll = st.container(height=500)
    
    with chat_scroll:
        for msg in st.session_state.messages:
            display_message(msg["role"], msg["content"], msg.get("sources"))


# ============================================
# INPUT DE PREGUNTAS
# ============================================
col1, col2 = st.columns([5, 1])

with col1:
    question = st.chat_input("Escribe tu pregunta aquí...", key="chat_input")

with col2:
    st.write("")
    st.write("")
    if st.button("📤 Enviar", use_container_width=True):
        if question:
            # Forzar el envío
            pass

# Procesar pregunta
if question:
    # Agregar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": question})
    
    # Mostrar mensaje del usuario
    display_message("user", question)
    
    # Generar respuesta
    try:
        with st.spinner("🤔 Pensando..."):
            response = st.session_state.chat_service.ask(
                question=question,
                k=st.session_state.k_value,
                include_history=True
            )
        
        # Agregar respuesta al historial
        st.session_state.messages.append({
            "role": "assistant",
            "content": response.answer,
            "sources": response.sources
        })
        
        # Mostrar respuesta
        display_message("assistant", response.answer, response.sources)
        
        # Scroll automático al final
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Error generando respuesta: {e}")
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"Lo siento, ocurrió un error: {str(e)}",
            "sources": []
        })


# ============================================
# FOOTER
# ============================================
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.caption(f"⚡ Modelo: {settings.OLLAMA_MODEL}")
with col2:
    st.caption(f"📚 Chunks recuperados: {st.session_state.k_value}")
with col3:
    st.caption("💡 Powered by LangChain + FAISS + Ollama")