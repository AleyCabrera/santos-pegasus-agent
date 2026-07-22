"""
Módulo de Vector Store (FAISS)
Gestión del índice de embeddings para búsqueda semántica
"""
import pickle
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_cohere import CohereEmbeddings

from src.config import VECTOR_STORE_DIR, COHERE_API_KEY, EMBEDDING_MODEL

logger = logging.getLogger(__name__)


def get_embeddings():
    """Obtiene el modelo de embeddings según configuración"""
    if EMBEDDING_MODEL == "cohere":
        return CohereEmbeddings(
            cohere_api_key=COHERE_API_KEY,
            model="embed-english-v3.0",
            user_agent="santos-pegasus-agent"
        )
    else:
        # Fallback local - sin API key
        return HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )