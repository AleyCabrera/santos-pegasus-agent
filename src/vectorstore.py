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
from langchain.schema import Document

from src.config import VECTOR_STORE_DIR, COHERE_API_KEY, EMBEDDING_MODEL

logger = logging.getLogger(__name__)


def get_embeddings():
    """Obtiene el modelo de embeddings según configuración"""
    if EMBEDDING_MODEL == "cohere":
        logger.info("🔧 Usando Cohere Embeddings")
        return CohereEmbeddings(
            cohere_api_key=COHERE_API_KEY,
            model="embed-english-v3.0",
            user_agent="santos-pegasus-agent"
        )
    else:
        logger.info("🔧 Usando HuggingFace Embeddings (local)")
        return HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )


def create_vector_store(chunks: List[Dict[str, Any]], force_rebuild: bool = False):
    """
    Crea un índice FAISS a partir de los chunks de documentos.
    
    Args:
        chunks: Lista de chunks con 'content', 'source', 'metadata'
        force_rebuild: Si es True, fuerza la recreación del índice
        
    Returns:
        FAISS vector store o None si falla
    """
    index_path = VECTOR_STORE_DIR / "faiss_index"
    
    if index_path.exists() and not force_rebuild:
        logger.info(f"📂 Índice FAISS existente encontrado en {index_path}")
        return load_vector_store()
    
    if not chunks:
        logger.error("❌ No se proporcionaron chunks para crear el índice")
        return None
    
    logger.info(f"🔨 Creando nuevo índice FAISS con {len(chunks)} chunks...")
    
    try:
        documents = []
        for chunk in chunks:
            doc = Document(
                page_content=chunk["content"],
                metadata={
                    "source": chunk["source"],
                    "chunk_id": chunk.get("chunk_id", ""),
                    **chunk.get("metadata", {})
                }
            )
            documents.append(doc)
        
        embeddings = get_embeddings()
        vector_store = FAISS.from_documents(
            documents=documents,
            embedding=embeddings
        )
        
        logger.info(f"💾 Guardando índice en {index_path}")
        vector_store.save_local(str(index_path))
        
        logger.info(f"✅ Índice FAISS creado exitosamente con {len(documents)} documentos")
        return vector_store
        
    except Exception as e:
        logger.error(f"❌ Error al crear vector store: {e}")
        import traceback
        traceback.print_exc()
        return None


def load_vector_store():
    """
    Carga el índice FAISS desde el almacenamiento local.
    
    Returns:
        FAISS vector store o None si no existe
    """
    index_path = VECTOR_STORE_DIR / "faiss_index"
    
    if not index_path.exists():
        logger.warning(f"⚠️ No se encontró índice en {index_path}")
        return None
    
    try:
        embeddings = get_embeddings()
        vector_store = FAISS.load_local(
            str(index_path),
            embeddings=embeddings,
            allow_dangerous_deserialization=True
        )
        logger.info(f"✅ Índice FAISS cargado exitosamente desde {index_path}")
        return vector_store
    except Exception as e:
        logger.error(f"❌ Error al cargar vector store: {e}")
        return None


def search_documents(query: str, vector_store, k: int = 4) -> List[Document]:
    """
    Busca documentos relevantes usando búsqueda por similitud.
    CORREGIDO: Asegura que la query sea una lista de strings.
    """
    if vector_store is None:
        logger.error("❌ Vector store no disponible")
        return []
    
    try:
        # 🔥 CORRECCIÓN: Forzar query como string simple
        if not isinstance(query, str):
            query = str(query)
        
        results = vector_store.similarity_search(query, k=k)
        logger.info(f"🔍 Búsqueda: '{query[:50]}...' → {len(results)} resultados")
        return results
    except Exception as e:
        logger.error(f"❌ Error en búsqueda: {e}")
        return []


# Script independiente para pruebas
if __name__ == "__main__":
    import sys
    from src.ingest import process_documents
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    chunks = process_documents()
    
    if chunks:
        vector_store = create_vector_store(chunks)
        
        if vector_store:
            print("\n" + "="*50)
            print("🔍 Probando búsquedas:")
            print("="*50)
            
            test_queries = [
                "¿Cuál es la filosofía de Santos Pegasus Soluciones?",
                "¿Qué herramientas usamos para desarrollo backend?",
                "¿Cómo manejan los incidentes?"
            ]
            
            for query in test_queries:
                print(f"\n🔍 Consulta: {query}")
                results = search_documents(query, vector_store, k=2)
                
                for i, doc in enumerate(results, 1):
                    print(f"   Resultado {i}:")
                    print(f"   Fuente: {doc.metadata.get('source', 'Desconocida')}")
                    print(f"   Contenido: {doc.page_content[:150]}...")
                    print()
    else:
        print("❌ No hay chunks para crear el índice")