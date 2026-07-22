"""
Aplicación Streamlit - Interfaz del agente
Diseño moderno, profesional y accesible para Santos Pegasus Soluciones
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

# Configuración de la página
st.set_page_config(
    page_title="Santos Pegasus - Agente IA",
    page_icon="🚀",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ============================================================
# CSS PERSONALIZADO - Diseño moderno y profesional
# ============================================================
st.markdown("""
<style>
    /* ===== FUENTES Y RESET ===== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* ===== FONDO Y CONTENEDOR PRINCIPAL ===== */
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #eef2f7 100%);
    }
    
    .main-container {
        max-width: 900px;
        margin: 0 auto;
        padding: 1rem 1.5rem 2rem;
    }
    
    /* ===== HEADER ===== */
    .header-wrapper {
        background: linear-gradient(135deg, #0f1724 0%, #1a2a3a 100%);
        border-radius: 1.5rem;
        padding: 2rem 2.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(15, 23, 36, 0.25);
        position: relative;
        overflow: hidden;
    }
    
    .header-wrapper::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(99, 102, 241, 0.15) 0%, transparent 70%);
        border-radius: 50%;
    }
    
    .header-wrapper::after {
        content: '';
        position: absolute;
        bottom: -40%;
        left: -10%;
        width: 200px;
        height: 200px;
        background: radial-gradient(circle, rgba(56, 189, 248, 0.10) 0%, transparent 70%);
        border-radius: 50%;
    }
    
    .header-content {
        position: relative;
        z-index: 1;
    }
    
    .logo-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: rgba(255, 255, 255, 0.10);
        backdrop-filter: blur(10px);
        padding: 0.3rem 0.9rem 0.3rem 0.6rem;
        border-radius: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 1rem;
        font-size: 0.75rem;
        color: #94a3b8;
        letter-spacing: 0.5px;
    }
    
    .logo-badge .dot {
        width: 6px;
        height: 6px;
        background: #34d399;
        border-radius: 50%;
        display: inline-block;
        animation: pulse-dot 2s ease-in-out infinite;
    }
    
    @keyframes pulse-dot {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.5; transform: scale(0.8); }
    }
    
    .main-title {
        color: #ffffff;
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0 0 0.3rem 0;
        letter-spacing: -0.5px;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .main-title .icon {
        font-size: 2rem;
    }
    
    .main-subtitle {
        color: #94a3b8;
        font-size: 1.05rem;
        font-weight: 400;
        margin: 0;
        letter-spacing: 0.2px;
    }
    
    .main-subtitle span.highlight {
        color: #60a5fa;
        font-weight: 500;
    }
    
    /* ===== STATS BADGE ===== */
    .stats-row {
        display: flex;
        gap: 1.5rem;
        margin-top: 1.2rem;
        flex-wrap: wrap;
    }
    
    .stat-item {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        color: #94a3b8;
        font-size: 0.8rem;
        background: rgba(255, 255, 255, 0.05);
        padding: 0.3rem 0.8rem;
        border-radius: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .stat-item .num {
        color: #e2e8f0;
        font-weight: 600;
    }
    
    /* ===== CHAT CONTAINER ===== */
    .chat-container {
        background: rgba(255, 255, 255, 0.75);
        backdrop-filter: blur(20px);
        border-radius: 1.5rem;
        padding: 1.5rem;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.8);
        min-height: 400px;
    }
    
    /* ===== MENSAJES ===== */
    .stChatMessage {
        background: transparent !important;
        padding: 0.5rem 0 !important;
    }
    
    /* Mensaje del usuario */
    .stChatMessage [data-testid="stChatMessageContent"] {
        background: #eef2f7 !important;
        color: #1e293b !important;
        border-radius: 1rem 1rem 0.25rem 1rem !important;
        padding: 0.75rem 1rem !important;
        max-width: 85% !important;
        margin-left: auto !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.6) !important;
    }
    
    /* Mensaje del asistente */
    .stChatMessage [data-testid="stChatMessageContent"]:has(.assistant-message) {
        background: #ffffff !important;
        color: #1e293b !important;
        border-radius: 1rem 1rem 1rem 0.25rem !important;
        padding: 0.75rem 1rem !important;
        max-width: 85% !important;
        margin-right: auto !important;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06) !important;
        border: 1px solid rgba(255, 255, 255, 0.8) !important;
    }
    
    /* Avatar del asistente */
    .stChatMessage .avatar {
        background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
        color: white !important;
        border-radius: 50% !important;
        width: 36px !important;
        height: 36px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 1rem !important;
    }
    
    /* ===== INPUT ===== */
    .stChatInputContainer {
        padding-top: 1rem !important;
        border-top: 1px solid rgba(0, 0, 0, 0.04) !important;
        margin-top: 0.5rem !important;
    }
    
    .stChatInputContainer textarea {
        border-radius: 1rem !important;
        border: 1px solid #e2e8f0 !important;
        padding: 0.75rem 1.2rem !important;
        font-size: 0.95rem !important;
        background: #ffffff !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02) !important;
    }
    
    .stChatInputContainer textarea:focus {
        border-color: #818cf8 !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.12) !important;
        outline: none !important;
    }
    
    .stChatInputContainer button {
        background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
        border: none !important;
        border-radius: 0.75rem !important;
        padding: 0.5rem 1.2rem !important;
        color: white !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }
    
    .stChatInputContainer button:hover {
        transform: scale(1.02) !important;
        box-shadow: 0 4px 16px rgba(79, 70, 229, 0.35) !important;
    }
    
    /* ===== SPINNER ===== */
    .stSpinner > div {
        border-color: #4f46e5 !important;
        border-top-color: transparent !important;
    }
    
    /* ===== FOOTER ===== */
    .footer-wrapper {
        text-align: center;
        padding: 1.5rem 0 0.5rem;
        color: #94a3b8;
        font-size: 0.75rem;
        letter-spacing: 0.3px;
        border-top: 1px solid rgba(0, 0, 0, 0.04);
        margin-top: 1.5rem;
    }
    
    .footer-wrapper .heart {
        color: #ef4444;
    }
    
    /* ===== EXPANDER (fuentes) ===== */
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
        border-radius: 0.75rem !important;
        padding: 0.75rem 1rem !important;
        font-size: 0.8rem !important;
        color: #475569 !important;
        border: 1px solid #e2e8f0 !important;
    }
    
    /* ===== RESPONSIVE ===== */
    @media (max-width: 640px) {
        .header-wrapper {
            padding: 1.5rem 1.2rem;
        }
        .main-title {
            font-size: 1.5rem;
        }
        .main-subtitle {
            font-size: 0.9rem;
        }
        .stats-row {
            gap: 0.8rem;
        }
        .stat-item {
            font-size: 0.7rem;
            padding: 0.2rem 0.6rem;
        }
        .chat-container {
            padding: 1rem;
        }
        .stChatMessage [data-testid="stChatMessageContent"] {
            max-width: 95% !important;
        }
    }
    
    /* ===== SCROLLBAR ===== */
    ::-webkit-scrollbar {
        width: 4px;
    }
    ::-webkit-scrollbar-track {
        background: transparent;
    }
    ::-webkit-scrollbar-thumb {
        background: #cbd5e1;
        border-radius: 2rem;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #94a3b8;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# FUNCIÓN DE INICIALIZACIÓN AUTOMÁTICA
# ============================================================

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
        with st.status("📚 Inicializando el agente por primera vez...", expanded=True) as status:
            st.write("🔍 Procesando documentos...")
            
            # 2. Procesar documentos
            chunks = process_documents()
            
            if not chunks:
                status.update(label="❌ Error: No se encontraron documentos", state="error")
                st.error("⚠️ No se encontraron documentos para procesar.")
                st.info("💡 Asegúrate de tener archivos PDF en la carpeta `data/documentos/`")
                return None
            
            st.write(f"✅ {len(chunks)} chunks generados")
            
            # 3. Crear vector store
            st.write("🧠 Generando embeddings y creando índice...")
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

# ============================================================
# CONTENIDO PRINCIPAL
# ============================================================

# --- HEADER MEJORADO ---
st.markdown("""
<div class="header-wrapper">
    <div class="header-content">
        <div class="logo-badge">
            <span class="dot"></span>
            AGENTE IA · EN VIVO
        </div>
        <div class="main-title">
            <span class="icon">🚀</span>
            Santos Pegasus
        </div>
        <div class="main-subtitle">
            Agente de IA para <span class="highlight">Documentación Interna</span>
        </div>
        <div class="stats-row">
            <div class="stat-item">
                📄 <span class="num">5</span> documentos indexados
            </div>
            <div class="stat-item">
                📚 <span class="num">375</span> chunks disponibles
            </div>
            <div class="stat-item">
                ⚡ <span class="num">Cohere</span> · IA generativa
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- INICIALIZACIÓN DEL AGENTE (con caché) ---
@st.cache_resource
def get_agent():
    """Obtiene el agente inicializado (cacheado)"""
    return initialize_agent_auto()

# Inicializar el agente
rag_chain = get_agent()

# Verificar si el agente está disponible
if rag_chain is None:
    st.stop()

# --- CONTENEDOR DEL CHAT ---
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Estado de la conversación
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 ¡Hola! Soy el agente de IA de **Santos Pegasus Soluciones**. Puedes preguntarme sobre nuestros manuales, guías y protocolos internos. ¿En qué puedo ayudarte?"}
    ]

# Mostrar mensajes existentes
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        # Clase adicional para estilizar mensajes del asistente
        if message["role"] == "assistant":
            st.markdown(f'<div class="assistant-message">{message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(message["content"])
        
        # Mostrar fuentes si están disponibles
        if "sources" in message and message["sources"]:
            with st.expander("📚 Ver fuentes"):
                for source in message["sources"]:
                    st.markdown(f"- {source}")

# --- INPUT DEL USUARIO ---
if prompt := st.chat_input("💬 Escribe tu pregunta sobre los documentos internos..."):
    # Mostrar mensaje del usuario
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Generar respuesta
    with st.chat_message("assistant"):
        with st.spinner("🔍 Buscando en los documentos..."):
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
            
            st.markdown(f'<div class="assistant-message">{response}</div>', unsafe_allow_html=True)
            
            if sources:
                with st.expander("📚 Ver fuentes"):
                    for source in sources:
                        st.markdown(f"- {source}")
    
    st.session_state.messages.append({
        "role": "assistant",
        "content": response,
        "sources": sources
    })

st.markdown('</div>', unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("""
<div class="footer-wrapper">
    🚀 Santos Pegasus Soluciones &bull; Agente IA v1.0 &bull; 
    Documentación interna &bull; Hecho con <span class="heart">❤</span> para el equipo
</div>
""", unsafe_allow_html=True)