"""
Aplicación Streamlit - Interfaz del agente
Diseño premium, moderno e inmersivo para Santos Pegasus Soluciones
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
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# CSS PERSONALIZADO - DISEÑO PREMIUM
# ============================================================
st.markdown("""
<style>
    /* ===== FUENTES Y RESET ===== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        box-sizing: border-box;
    }
    
    /* ===== FONDO CON EFECTO ===== */
    .stApp {
        background: #0a0e1a;
        position: relative;
    }
    
    .stApp::before {
        content: '';
        position: fixed;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: 
            radial-gradient(ellipse at 20% 50%, rgba(99, 102, 241, 0.08) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 50%, rgba(56, 189, 248, 0.06) 0%, transparent 50%),
            radial-gradient(ellipse at 50% 100%, rgba(139, 92, 246, 0.05) 0%, transparent 40%);
        z-index: 0;
        pointer-events: none;
    }
    
    /* ===== CONTENEDOR PRINCIPAL ===== */
    .main-wrapper {
        position: relative;
        z-index: 1;
        max-width: 1200px;
        margin: 0 auto;
        padding: 1.5rem 2rem 2rem;
    }
    
    /* ===== HEADER PREMIUM ===== */
    .header-premium {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 27, 75, 0.95) 100%);
        backdrop-filter: blur(20px);
        border-radius: 2rem;
        padding: 2.5rem 3rem;
        margin-bottom: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.06);
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
        position: relative;
        overflow: hidden;
    }
    
    .header-premium::before {
        content: '';
        position: absolute;
        top: -60%;
        right: -20%;
        width: 500px;
        height: 500px;
        background: radial-gradient(circle, rgba(99, 102, 241, 0.20) 0%, transparent 70%);
        border-radius: 50%;
        animation: float-glow 8s ease-in-out infinite;
    }
    
    .header-premium::after {
        content: '';
        position: absolute;
        bottom: -40%;
        left: -10%;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(56, 189, 248, 0.12) 0%, transparent 70%);
        border-radius: 50%;
        animation: float-glow 10s ease-in-out infinite reverse;
    }
    
    @keyframes float-glow {
        0%, 100% { transform: translate(0, 0) scale(1); }
        50% { transform: translate(30px, -20px) scale(1.1); }
    }
    
    .header-content {
        position: relative;
        z-index: 2;
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        flex-wrap: wrap;
        gap: 1.5rem;
    }
    
    .header-left {
        flex: 1;
        min-width: 250px;
    }
    
    .badge-status {
        display: inline-flex;
        align-items: center;
        gap: 0.6rem;
        background: rgba(52, 211, 153, 0.12);
        padding: 0.4rem 1.2rem 0.4rem 0.8rem;
        border-radius: 2rem;
        border: 1px solid rgba(52, 211, 153, 0.15);
        margin-bottom: 1rem;
        font-size: 0.7rem;
        font-weight: 500;
        color: #34d399;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    
    .badge-status .dot {
        width: 7px;
        height: 7px;
        background: #34d399;
        border-radius: 50%;
        display: inline-block;
        animation: pulse-dot 1.5s ease-in-out infinite;
        box-shadow: 0 0 12px rgba(52, 211, 153, 0.4);
    }
    
    @keyframes pulse-dot {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.5; transform: scale(0.7); }
    }
    
    .brand-title {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin: 0 0 0.3rem 0;
    }
    
    .brand-icon {
        font-size: 2.8rem;
        filter: drop-shadow(0 0 20px rgba(99, 102, 241, 0.3));
        animation: float-icon 4s ease-in-out infinite;
    }
    
    @keyframes float-icon {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-6px); }
    }
    
    .brand-name {
        font-size: 2.6rem;
        font-weight: 900;
        color: #ffffff;
        letter-spacing: -1px;
        background: linear-gradient(135deg, #ffffff 0%, #a5b4fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .brand-subtitle {
        font-size: 1.1rem;
        font-weight: 400;
        color: #94a3b8;
        margin: 0.2rem 0 0 0;
        letter-spacing: 0.2px;
    }
    
    .brand-subtitle .highlight {
        color: #818cf8;
        font-weight: 500;
    }
    
    .header-right {
        display: flex;
        gap: 1.2rem;
        flex-wrap: wrap;
        align-items: center;
        padding-top: 0.5rem;
    }
    
    .stat-card {
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(10px);
        padding: 0.6rem 1.2rem;
        border-radius: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.05);
        text-align: center;
        min-width: 80px;
        transition: all 0.3s ease;
    }
    
    .stat-card:hover {
        background: rgba(255, 255, 255, 0.08);
        transform: translateY(-2px);
    }
    
    .stat-number {
        font-size: 1.3rem;
        font-weight: 700;
        color: #ffffff;
        display: block;
    }
    
    .stat-label {
        font-size: 0.6rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 500;
    }
    
    /* ===== CHAT CONTAINER ===== */
    .chat-wrapper {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        border-radius: 2rem;
        padding: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.05);
        min-height: 500px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    }
    
    /* ===== MENSAJES ===== */
    .stChatMessage {
        background: transparent !important;
        padding: 0.8rem 0 !important;
        border: none !important;
    }
    
    /* Mensaje del usuario */
    .stChatMessage [data-testid="stChatMessageContent"] {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.20) 0%, rgba(139, 92, 246, 0.15) 100%) !important;
        color: #e2e8f0 !important;
        border-radius: 1.2rem 1.2rem 0.3rem 1.2rem !important;
        padding: 0.9rem 1.3rem !important;
        max-width: 80% !important;
        margin-left: auto !important;
        border: 1px solid rgba(99, 102, 241, 0.15) !important;
        backdrop-filter: blur(10px) !important;
        box-shadow: 0 4px 16px rgba(99, 102, 241, 0.08) !important;
    }
    
    /* Mensaje del asistente */
    .stChatMessage [data-testid="stChatMessageContent"]:has(.assistant-message) {
        background: rgba(255, 255, 255, 0.05) !important;
        color: #e2e8f0 !important;
        border-radius: 1.2rem 1.2rem 1.2rem 0.3rem !important;
        padding: 0.9rem 1.3rem !important;
        max-width: 80% !important;
        margin-right: auto !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        backdrop-filter: blur(10px) !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1) !important;
    }
    
    .assistant-message {
        color: #e2e8f0;
        line-height: 1.6;
    }
    
    .assistant-message strong {
        color: #a5b4fc;
    }
    
    /* Avatar del asistente */
    .stChatMessage .avatar {
        background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
        border-radius: 50% !important;
        width: 40px !important;
        height: 40px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 1.2rem !important;
        box-shadow: 0 4px 16px rgba(99, 102, 241, 0.3) !important;
    }
    
    /* ===== INPUT ===== */
    .stChatInputContainer {
        padding-top: 1.2rem !important;
        border-top: 1px solid rgba(255, 255, 255, 0.06) !important;
        margin-top: 0.5rem !important;
    }
    
    .stChatInputContainer textarea {
        border-radius: 1.2rem !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        padding: 0.9rem 1.5rem !important;
        font-size: 0.95rem !important;
        background: rgba(255, 255, 255, 0.04) !important;
        color: #e2e8f0 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1) !important;
    }
    
    .stChatInputContainer textarea::placeholder {
        color: #64748b !important;
    }
    
    .stChatInputContainer textarea:focus {
        border-color: #818cf8 !important;
        box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.12) !important;
        outline: none !important;
        background: rgba(255, 255, 255, 0.06) !important;
    }
    
    .stChatInputContainer button {
        background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
        border: none !important;
        border-radius: 1rem !important;
        padding: 0.6rem 1.5rem !important;
        color: white !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 16px rgba(99, 102, 241, 0.25) !important;
    }
    
    .stChatInputContainer button:hover {
        transform: scale(1.03) !important;
        box-shadow: 0 6px 24px rgba(99, 102, 241, 0.4) !important;
    }
    
    .stChatInputContainer button:active {
        transform: scale(0.97) !important;
    }
    
    /* ===== SPINNER ===== */
    .stSpinner > div {
        border-color: #818cf8 !important;
        border-top-color: transparent !important;
        border-width: 3px !important;
    }
    
    /* ===== STATUS ===== */
    .stStatus {
        background: rgba(255, 255, 255, 0.03) !important;
        border-radius: 1.2rem !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        padding: 1.5rem !important;
        backdrop-filter: blur(10px) !important;
    }
    
    .stStatus .stMarkdown {
        color: #e2e8f0 !important;
    }
    
    /* ===== EXPANDER ===== */
    .streamlit-expanderHeader {
        background: transparent !important;
        color: #94a3b8 !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        padding: 0.5rem 0 !important;
        border: none !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.04) !important;
    }
    
    .streamlit-expanderContent {
        background: rgba(255, 255, 255, 0.03) !important;
        border-radius: 0.8rem !important;
        padding: 0.8rem 1rem !important;
        font-size: 0.8rem !important;
        color: #94a3b8 !important;
        border: 1px solid rgba(255, 255, 255, 0.04) !important;
        margin-top: 0.5rem !important;
    }
    
    /* ===== FOOTER ===== */
    .footer-premium {
        text-align: center;
        padding: 1.5rem 0 0.5rem;
        color: #475569;
        font-size: 0.7rem;
        letter-spacing: 0.5px;
        border-top: 1px solid rgba(255, 255, 255, 0.04);
        margin-top: 2rem;
    }
    
    .footer-premium .heart {
        color: #ef4444;
        display: inline-block;
        animation: heart-pulse 1.5s ease-in-out infinite;
    }
    
    @keyframes heart-pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.2); }
    }
    
    /* ===== SCROLLBAR ===== */
    ::-webkit-scrollbar {
        width: 5px;
    }
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.02);
    }
    ::-webkit-scrollbar-thumb {
        background: #4f46e5;
        border-radius: 2rem;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #7c3aed;
    }
    
    /* ===== RESPONSIVE ===== */
    @media (max-width: 768px) {
        .main-wrapper {
            padding: 0.8rem 1rem;
        }
        .header-premium {
            padding: 1.5rem 1.5rem;
        }
        .header-content {
            flex-direction: column;
        }
        .brand-name {
            font-size: 1.8rem;
        }
        .brand-icon {
            font-size: 2rem;
        }
        .brand-subtitle {
            font-size: 0.9rem;
        }
        .header-right {
            width: 100%;
            justify-content: flex-start;
        }
        .stat-card {
            min-width: 60px;
            padding: 0.4rem 0.8rem;
        }
        .stat-number {
            font-size: 1rem;
        }
        .chat-wrapper {
            padding: 1.2rem;
        }
        .stChatMessage [data-testid="stChatMessageContent"] {
            max-width: 92% !important;
        }
        .stChatInputContainer textarea {
            font-size: 0.85rem !important;
            padding: 0.7rem 1rem !important;
        }
    }
    
    @media (max-width: 480px) {
        .brand-name {
            font-size: 1.4rem;
        }
        .header-premium {
            padding: 1rem 1rem;
        }
        .stat-card {
            min-width: 50px;
            padding: 0.3rem 0.6rem;
        }
        .stat-number {
            font-size: 0.8rem;
        }
        .stat-label {
            font-size: 0.5rem;
        }
        .chat-wrapper {
            padding: 0.8rem;
        }
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

# ============================================================
# CONTENIDO PRINCIPAL
# ============================================================

st.markdown('<div class="main-wrapper">', unsafe_allow_html=True)

# --- HEADER PREMIUM ---
st.markdown("""
<div class="header-premium">
    <div class="header-content">
        <div class="header-left">
            <div class="badge-status">
                <span class="dot"></span>
                Sistema en línea · IA Activa
            </div>
            <div class="brand-title">
                <span class="brand-icon">🚀</span>
                <span class="brand-name">Santos Pegasus</span>
            </div>
            <p class="brand-subtitle">
                Agente de IA para <span class="highlight">Documentación Interna</span>
                <br><span style="font-size:0.85rem; color:#64748b;">
                    Consulta manuales, guías y protocolos en lenguaje natural
                </span>
            </p>
        </div>
        <div class="header-right">
            <div class="stat-card">
                <span class="stat-number">5</span>
                <span class="stat-label">Documentos</span>
            </div>
            <div class="stat-card">
                <span class="stat-number">375</span>
                <span class="stat-label">Chunks</span>
            </div>
            <div class="stat-card">
                <span class="stat-number">⚡</span>
                <span class="stat-label">Cohere AI</span>
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

# --- CHAT WRAPPER ---
st.markdown('<div class="chat-wrapper">', unsafe_allow_html=True)

# Estado de la conversación
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 ¡Hola! Soy el agente de IA de **Santos Pegasus Soluciones**. Puedes preguntarme sobre nuestros manuales, guías y protocolos internos. ¿En qué puedo ayudarte?"}
    ]

# Mostrar mensajes existentes
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant":
            st.markdown(f'<div class="assistant-message">{message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(message["content"])
        
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

# --- FOOTER PREMIUM ---
st.markdown("""
<div class="footer-premium">
    🚀 Santos Pegasus Soluciones &bull; Agente IA v1.0 &bull; 
    Documentación interna &bull; Hecho con <span class="heart">❤</span> para el equipo
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)