"""
Configuración centralizada del proyecto
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Directorios base
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DOCUMENTS_DIR = DATA_DIR / "documentos"
VECTOR_STORE_DIR = DATA_DIR / "vector_store"

# Crear directorios si no existen
DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)

# Configuración de API
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
if not COHERE_API_KEY:
    raise ValueError("COHERE_API_KEY no configurada en .env o secrets")

# Configuración de embeddings
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "cohere")

# Configuración de chunking
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 500))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 100))

# Configuración del agente
MAX_RETRIEVAL_DOCS = 4
TEMPERATURE = 0.3

# Configuración de Streamlit
if os.getenv("STREAMLIT_RUN"):
    # En Streamlit Cloud, usar st.secrets
    import streamlit as st
    COHERE_API_KEY = st.secrets.get("COHERE_API_KEY", COHERE_API_KEY)