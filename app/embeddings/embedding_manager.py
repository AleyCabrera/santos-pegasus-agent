"""Módulo para gestión de embeddings con Sentence-Transformers"""

import numpy as np
from typing import List, Dict, Any, Optional
from pathlib import Path
from sentence_transformers import SentenceTransformer
from app.config import settings
from app.utils.logger import logger
import time
import hashlib


class EmbeddingManager:
    """
    Gestor de embeddings usando Sentence-Transformers
    Optimizado para memoria con 7GB RAM
    """
    
    def __init__(
        self,
        model_name: Optional[str] = None,
        device: str = 'cpu'
    ):
        """
        Inicializa el gestor de embeddings
        
        Args:
            model_name: Nombre del modelo (default: de settings)
            device: 'cpu' o 'cuda' (default: 'cpu' para evitar uso de GPU)
        """
        self.model_name = model_name or settings.EMBEDDING_MODEL
        self.device = device
        self.logger = logger
        
        # Cache de embeddings para evitar recomputar
        self.embedding_cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Cargar modelo (con optimizaciones para memoria)
        self._load_model()
    
    def _load_model(self):
        """Carga el modelo de embeddings con optimizaciones"""
        try:
            self.logger.info(f"🔧 Cargando modelo de embeddings: {self.model_name}")
            
            # Cargar modelo con optimizaciones
            self.model = SentenceTransformer(
                self.model_name,
                device=self.device
            )
            
            # Configurar para usar menos memoria
            self.model.max_seq_length = 512  # Limitar secuencia
            
            self.logger.info(f"✅ Modelo cargado: {self.model_name}")
            self.logger.info(f"   📏 Dimensiones del embedding: {self.model.get_sentence_embedding_dimension()}")
            
        except Exception as e:
            self.logger.error(f"❌ Error cargando modelo: {e}")
            raise
    
    def get_embedding(self, text: str) -> np.ndarray:
        """
        Genera embedding para un texto
        
        Args:
            text: Texto a embedder
            
        Returns:
            Vector de embedding (numpy array)
        """
        if not text or not text.strip():
            self.logger.warning("Texto vacío, retornando embedding zero")
            return np.zeros(self.model.get_sentence_embedding_dimension())
        
        # Verificar cache
        text_hash = self._get_text_hash(text)
        if text_hash in self.embedding_cache:
            self.cache_hits += 1
            return self.embedding_cache[text_hash].copy()
        
        self.cache_misses += 1
        
        # Generar embedding
        try:
            # Encode con batch_size=1 para ahorrar memoria
            embedding = self.model.encode(
                text,
                convert_to_numpy=True,
                normalize_embeddings=True,  # Normalizar para mejor similitud
                show_progress_bar=False
            )
            
            # Guardar en cache (solo para textos cortos para no gastar memoria)
            if len(text) < 1000:  # No cachear textos muy largos
                self.embedding_cache[text_hash] = embedding.copy()
                
                # Limitar tamaño del cache (LRU simple)
                if len(self.embedding_cache) > 1000:
                    # Remover el primer elemento (más antiguo)
                    first_key = next(iter(self.embedding_cache))
                    del self.embedding_cache[first_key]
            
            return embedding
            
        except Exception as e:
            self.logger.error(f"Error generando embedding: {e}")
            return np.zeros(self.model.get_sentence_embedding_dimension())
    
    def get_embeddings(self, texts: List[str], batch_size: int = 32) -> List[np.ndarray]:
        """
        Genera embeddings para múltiples textos en batches
        
        Args:
            texts: Lista de textos
            batch_size: Tamaño del batch (ajustar según memoria)
            
        Returns:
            Lista de vectores de embedding
        """
        if not texts:
            return []
        
        self.logger.info(f"📊 Generando embeddings para {len(texts)} textos (batch_size={batch_size})")
        
        embeddings = []
        total_batches = (len(texts) + batch_size - 1) // batch_size
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_num = i // batch_size + 1
            
            try:
                # Generar embeddings para el batch
                batch_embeddings = self.model.encode(
                    batch,
                    convert_to_numpy=True,
                    normalize_embeddings=True,
                    show_progress_bar=False
                )
                
                embeddings.extend(batch_embeddings)
                
                self.logger.info(f"   ✅ Batch {batch_num}/{total_batches} completado")
                
            except Exception as e:
                self.logger.error(f"Error en batch {batch_num}: {e}")
                # Generar embeddings individuales si falla el batch
                for text in batch:
                    embeddings.append(self.get_embedding(text))
        
        self.logger.info(f"✅ Generados {len(embeddings)} embeddings")
        self.logger.info(f"   📊 Cache: {self.cache_hits} hits, {self.cache_misses} misses")
        
        return embeddings
    
    def _get_text_hash(self, text: str) -> str:
        """Genera hash del texto para cache"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()[:16]
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del cache"""
        total = self.cache_hits + self.cache_misses
        hit_rate = self.cache_hits / total if total > 0 else 0
        
        return {
            'cache_size': len(self.embedding_cache),
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'hit_rate': f"{hit_rate:.2%}",
            'model_name': self.model_name,
            'embedding_dim': self.model.get_sentence_embedding_dimension()
        }
    
    def clear_cache(self):
        """Limpia el cache de embeddings"""
        self.embedding_cache.clear()
        self.cache_hits = 0
        self.cache_misses = 0
        self.logger.info("🧹 Cache de embeddings limpiado")