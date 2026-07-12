"""Módulo para gestión de Vector Store con FAISS"""

import numpy as np
import faiss
import pickle
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from app.config import settings
from app.utils.logger import logger
from app.embeddings.embedding_manager import EmbeddingManager


class FAISSVectorStore:
    """
    Vector Store usando FAISS (Facebook AI Similarity Search)
    Optimizado para memoria con 7GB RAM
    """
    
    def __init__(
        self,
        embedding_manager: Optional[EmbeddingManager] = None,
        store_path: Optional[Path] = None
    ):
        """
        Inicializa el vector store
        
        Args:
            embedding_manager: Gestor de embeddings (crea uno si no se proporciona)
            store_path: Ruta para persistir el índice FAISS
        """
        self.embedding_manager = embedding_manager or EmbeddingManager()
        self.store_path = store_path or settings.VECTOR_STORE_PATH
        
        # Crear directorio si no existe
        self.store_path.mkdir(parents=True, exist_ok=True)
        
        self.index = None
        self.metadata_store = []  # Lista de metadatos de cada chunk
        self.chunks_store = []    # Lista de textos de cada chunk
        self.is_loaded = False
        
        self.logger = logger
    
    def create_index(self, embedding_dim: int, index_type: str = 'flat'):
        """
        Crea un nuevo índice FAISS
        
        Args:
            embedding_dim: Dimensión de los embeddings
            index_type: Tipo de índice ('flat', 'ivf', 'pq')
        """
        self.logger.info(f"🔧 Creando índice FAISS (dim={embedding_dim}, type={index_type})")
        
        if index_type == 'flat':
            # Índice plano (exacto, usa más memoria pero mejor precisión)
            self.index = faiss.IndexFlatIP(embedding_dim)  # Inner Product (similaridad coseno)
        elif index_type == 'ivf':
            # IVF (Inverted File) - más eficiente en memoria
            nlist = 100  # Número de clusters
            quantizer = faiss.IndexFlatIP(embedding_dim)
            self.index = faiss.IndexIVFFlat(quantizer, embedding_dim, nlist, faiss.METRIC_INNER_PRODUCT)
            self.index.train = True  # Necesita entrenamiento
        elif index_type == 'pq':
            # Product Quantization - más compacto
            m = 8  # Número de sub-vectores
            self.index = faiss.IndexPQ(embedding_dim, m, 8, faiss.METRIC_INNER_PRODUCT)
        else:
            raise ValueError(f"Tipo de índice no soportado: {index_type}")
        
        # Resetear stores
        self.metadata_store = []
        self.chunks_store = []
        self.is_loaded = True
        
        self.logger.info(f"✅ Índice FAISS creado")
    
    def add_documents(
        self,
        documents: List[Dict[str, Any]],
        embeddings: Optional[List[np.ndarray]] = None
    ) -> int:
        """
        Agrega documentos al vector store
        
        Args:
            documents: Lista de documentos (con 'content' y 'metadata')
            embeddings: Embeddings pre-calculados (opcional)
            
        Returns:
            Número de documentos agregados
        """
        if not documents:
            self.logger.warning("No hay documentos para agregar")
            return 0
        
        if not self.is_loaded:
            self.logger.error("Vector store no inicializado")
            return 0
        
        self.logger.info(f"📥 Agregando {len(documents)} documentos al vector store")
        
        # Preparar documentos
        texts = [doc['content'] for doc in documents]
        metadatas = [doc.get('metadata', {}) for doc in documents]
        
        # Generar embeddings si no se proporcionaron
        if embeddings is None:
            self.logger.info("   Generando embeddings...")
            embeddings = self.embedding_manager.get_embeddings(texts)
        
        if not embeddings:
            self.logger.error("No se generaron embeddings")
            return 0
        
        # Convertir a numpy array
        embeddings_array = np.array(embeddings).astype('float32')
        
        # Agregar al índice
        if isinstance(self.index, faiss.IndexIVFFlat):
            # IVF necesita entrenamiento antes de agregar
            if not self.index.is_trained:
                self.logger.info("   Entrenando índice IVF...")
                self.index.train(embeddings_array)
        
        # Agregar al índice
        self.index.add(embeddings_array)
        
        # Almacenar metadatos y chunks
        for idx, (text, metadata) in enumerate(zip(texts, metadatas)):
            # Agregar información adicional a metadata
            metadata['vector_index'] = self.index.ntotal - len(texts) + idx
            
            self.chunks_store.append(text)
            self.metadata_store.append(metadata)
        
        self.logger.info(f"✅ Agregados {len(texts)} documentos al índice")
        self.logger.info(f"   Total documentos en índice: {self.index.ntotal}")
        
        return len(texts)
    
    def search(
        self,
        query: str,
        k: int = 5,
        threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Busca documentos similares a la consulta
        
        Args:
            query: Texto de consulta
            k: Número de resultados a retornar
            threshold: Umbral mínimo de similitud
            
        Returns:
            Lista de documentos con contenido, metadata y score
        """
        if not self.is_loaded or self.index is None:
            self.logger.warning("Vector store no inicializado o vacío")
            return []
        
        if self.index.ntotal == 0:
            self.logger.warning("Vector store vacío")
            return []
        
        if threshold is None:
            threshold = settings.SIMILARITY_THRESHOLD
        
        # Generar embedding de la consulta
        query_embedding = self.embedding_manager.get_embedding(query)
        query_embedding = query_embedding.astype('float32').reshape(1, -1)
        
        # Buscar en FAISS
        distances, indices = self.index.search(query_embedding, min(k, self.index.ntotal))
        
        # Procesar resultados
        results = []
        for distance, idx in zip(distances[0], indices[0]):
            if idx == -1:
                continue
            
            # Convertir distancia a similitud (normalizar)
            # FAISS con IP da coseno similaridad en [-1, 1]
            similarity = distance
            
            # Si usamos normalize_embeddings=True, el rango es [0, 1]
            # pero a veces puede ser ligeramente negativo
            if similarity < 0:
                similarity = max(0, similarity)  # Clamp a 0
            
            if similarity >= threshold and idx < len(self.metadata_store):
                result = {
                    'content': self.chunks_store[idx],
                    'metadata': self.metadata_store[idx].copy(),
                    'similarity': float(similarity),
                    'index': int(idx)
                }
                results.append(result)
        
        self.logger.info(f"🔍 Búsqueda: '{query[:50]}...' → {len(results)} resultados")
        
        return results
    
    def save(self, path: Optional[Path] = None):
        """
        Guarda el vector store en disco
        
        Args:
            path: Ruta donde guardar (usa self.store_path si no se especifica)
        """
        save_path = path or self.store_path
        save_path = Path(save_path)
        save_path.mkdir(parents=True, exist_ok=True)
        
        if self.index is None:
            self.logger.warning("No hay índice para guardar")
            return
        
        self.logger.info(f"💾 Guardando vector store en {save_path}")
        
        try:
            # Guardar índice FAISS
            faiss_path = save_path / "faiss.index"
            faiss.write_index(self.index, str(faiss_path))
            
            # Guardar metadatos
            metadata_path = save_path / "metadata.pkl"
            with open(metadata_path, 'wb') as f:
                pickle.dump({
                    'metadata': self.metadata_store,
                    'chunks': self.chunks_store,
                    'total_documents': self.index.ntotal,
                    'embedding_dim': self.index.d
                }, f)
            
            # Guardar configuración
            config_path = save_path / "config.json"
            with open(config_path, 'w') as f:
                json.dump({
                    'index_type': type(self.index).__name__,
                    'total_documents': self.index.ntotal,
                    'embedding_dim': self.index.d,
                    'model_name': self.embedding_manager.model_name,
                    'version': '1.0.0'
                }, f, indent=2)
            
            self.logger.info(f"✅ Vector store guardado exitosamente")
            
        except Exception as e:
            self.logger.error(f"❌ Error guardando vector store: {e}")
            raise
    
    def load(self, path: Optional[Path] = None):
        """
        Carga el vector store desde disco
        
        Args:
            path: Ruta desde donde cargar (usa self.store_path si no se especifica)
        """
        load_path = path or self.store_path
        load_path = Path(load_path)
        
        faiss_path = load_path / "faiss.index"
        metadata_path = load_path / "metadata.pkl"
        
        if not faiss_path.exists():
            self.logger.warning(f"No existe índice en {load_path}")
            return False
        
        self.logger.info(f"📂 Cargando vector store desde {load_path}")
        
        try:
            # Cargar índice FAISS
            self.index = faiss.read_index(str(faiss_path))
            
            # Cargar metadatos
            with open(metadata_path, 'rb') as f:
                data = pickle.load(f)
                self.metadata_store = data['metadata']
                self.chunks_store = data['chunks']
            
            self.is_loaded = True
            
            self.logger.info(f"✅ Vector store cargado: {self.index.ntotal} documentos")
            self.logger.info(f"   📏 Dimensión: {self.index.d}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error cargando vector store: {e}")
            return False
    
    def clear(self):
        """Limpia el vector store"""
        self.index = None
        self.metadata_store = []
        self.chunks_store = []
        self.is_loaded = False
        self.logger.info("🧹 Vector store limpiado")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas del vector store"""
        return {
            'total_documents': self.index.ntotal if self.index else 0,
            'embedding_dim': self.index.d if self.index else 0,
            'is_loaded': self.is_loaded,
            'is_trained': self.index.is_trained if hasattr(self.index, 'is_trained') else None,
            'metadata_count': len(self.metadata_store),
            'chunks_count': len(self.chunks_store),
            'store_path': str(self.store_path)
        }