import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

# Cargar variables de entorno
load_dotenv()

class Settings(BaseSettings):
    """Configuración centralizada de la aplicación"""
    
    # Model Configuration
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
    OLLAMA_TEMPERATURE: float = float(os.getenv("OLLAMA_TEMPERATURE", "0.7"))
    OLLAMA_CONTEXT_WINDOW: int = int(os.getenv("OLLAMA_CONTEXT_WINDOW", "2048"))
    
    # Embeddings
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    
    # Vector Store
    VECTOR_STORE_PATH: Path = Path(os.getenv("VECTOR_STORE_PATH", "./vectorstore/faiss_index"))
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "500"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "50"))
    
    # Paths
    DATA_PATH: Path = Path(os.getenv("DATA_PATH", "./data"))
    PDFS_PATH: Path = Path(os.getenv("PDFS_PATH", "./data/pdfs"))
    CSV_PATH: Path = Path(os.getenv("CSV_PATH", "./data/csv"))
    
    # App Config
    APP_NAME: str = os.getenv("APP_NAME", "Santos Pegasus Soluciones Agent")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

# Instancia global de configuración
settings = Settings()