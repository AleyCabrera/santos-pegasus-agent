"""Pruebas para el sistema de embeddings"""

import pytest
import numpy as np
from app.embeddings.embedding_manager import EmbeddingManager
from app.vector_store.faiss_store import FAISSVectorStore


class TestEmbeddingManager:
    """Pruebas para EmbeddingManager"""
    
    @pytest.fixture
    def manager(self):
        """Crea un gestor de embeddings para pruebas"""
        return EmbeddingManager()
    
    def test_initialization(self, manager):
        """Prueba inicialización del gestor"""
        assert manager.model is not None
        assert manager.model_name == 'all-MiniLM-L6-v2'
        assert manager.model.get_sentence_embedding_dimension() == 384
    
    def test_get_embedding(self, manager):
        """Prueba generación de embedding individual"""
        text = "Este es un texto de prueba para embeddings"
        embedding = manager.get_embedding(text)
        
        assert isinstance(embedding, np.ndarray)
        assert embedding.shape == (384,)
        assert not np.all(embedding == 0)  # No es un vector cero
    
    def test_get_embeddings_batch(self, manager):
        """Prueba generación de embeddings en batch"""
        texts = ["Texto 1", "Texto 2", "Texto 3"]
        embeddings = manager.get_embeddings(texts)
        
        assert len(embeddings) == 3
        assert all(isinstance(emb, np.ndarray) for emb in embeddings)
        assert all(emb.shape == (384,) for emb in embeddings)
    
    def test_cache_functionality(self, manager):
        """Prueba funcionamiento del cache"""
        text = "Texto para probar cache"
        
        # Primera llamada (cache miss)
        emb1 = manager.get_embedding(text)
        assert manager.cache_misses == 1
        
        # Segunda llamada (cache hit)
        emb2 = manager.get_embedding(text)
        assert manager.cache_hits == 1
        
        # Los embeddings deben ser iguales
        assert np.allclose(emb1, emb2)
    
    def test_empty_text(self, manager):
        """Prueba con texto vacío"""
        embedding = manager.get_embedding("")
        assert np.all(embedding == 0)
    
    def test_cache_stats(self, manager):
        """Prueba estadísticas del cache"""
        manager.get_embedding("Texto 1")
        manager.get_embedding("Texto 1")  # Cache hit
        manager.get_embedding("Texto 2")
        
        stats = manager.get_cache_stats()
        assert stats['cache_hits'] == 1
        assert stats['cache_misses'] == 2
        assert stats['cache_size'] > 0


class TestFAISSVectorStore:
    """Pruebas para FAISSVectorStore"""
    
    @pytest.fixture
    def vector_store(self):
        """Crea un vector store para pruebas"""
        embedding_manager = EmbeddingManager()
        store = FAISSVectorStore(embedding_manager)
        embedding_dim = embedding_manager.model.get_sentence_embedding_dimension()
        store.create_index(embedding_dim)
        return store
    
    @pytest.fixture
    def sample_documents(self):
        """Documentos de ejemplo"""
        return [
            {
                'content': 'Los perros son animales domésticos muy leales.',
                'metadata': {'type': 'animal', 'id': 1}
            },
            {
                'content': 'Los gatos son independientes y cazadores por naturaleza.',
                'metadata': {'type': 'animal', 'id': 2}
            },
            {
                'content': 'Los pájaros pueden volar y migrar en invierno.',
                'metadata': {'type': 'animal', 'id': 3}
            }
        ]
    
    def test_create_index(self, vector_store):
        """Prueba creación de índice"""
        assert vector_store.index is not None
        assert vector_store.is_loaded
        assert vector_store.index.d == 384
    
    def test_add_documents(self, vector_store, sample_documents):
        """Prueba agregar documentos"""
        count = vector_store.add_documents(sample_documents)
        assert count == 3
        assert vector_store.index.ntotal == 3
        assert len(vector_store.metadata_store) == 3
        assert len(vector_store.chunks_store) == 3
    
    def test_search(self, vector_store, sample_documents):
        """Prueba búsqueda"""
        vector_store.add_documents(sample_documents)
        
        # Buscar perros
        results = vector_store.search("perros", k=2)
        assert len(results) > 0
        assert results[0]['similarity'] >= 0.0
        
        # Buscar gatos
        results = vector_store.search("gatos", k=2)
        assert len(results) > 0
        assert 'gatos' in results[0]['content'].lower() or 'gatos' in results[0]['metadata'].get('id', '')
    
    def test_save_and_load(self, vector_store, sample_documents, tmp_path):
        """Prueba guardar y cargar vector store"""
        vector_store.add_documents(sample_documents)
        vector_store.save(tmp_path)
        
        # Crear nuevo vector store y cargar
        new_store = FAISSVectorStore(vector_store.embedding_manager)
        assert new_store.load(tmp_path)
        
        assert new_store.index.ntotal == 3
        assert len(new_store.metadata_store) == 3
        assert len(new_store.chunks_store) == 3
    
    def test_threshold_filtering(self, vector_store, sample_documents):
        """Prueba filtrado por umbral de similitud"""
        vector_store.add_documents(sample_documents)
        
        # Buscar con umbral alto (puede no encontrar)
        results = vector_store.search("perros", k=3, threshold=0.9)
        
        # Verificar que todos los resultados cumplen el umbral
        for result in results:
            assert result['similarity'] >= 0.9
    
    def test_empty_store_search(self, vector_store):
        """Prueba búsqueda en store vacío"""
        results = vector_store.search("cualquier consulta")
        assert results == []  # Debe retornar lista vacía
    
    def test_clear(self, vector_store, sample_documents):
        """Prueba limpiar vector store"""
        vector_store.add_documents(sample_documents)
        assert vector_store.index.ntotal == 3
        
        vector_store.clear()
        assert vector_store.index is None
        assert not vector_store.is_loaded
        assert len(vector_store.metadata_store) == 0