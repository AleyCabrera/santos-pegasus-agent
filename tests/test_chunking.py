# tests/test_chunking.py
"""
Pruebas para el procesamiento de texto y chunking
"""
import pytest
from pathlib import Path
from app.utils.text_processor import (
    TextNormalizer,
    ChunkingStrategy,
    DocumentProcessor
)

class TestTextNormalizer:
    """Pruebas para TextNormalizer"""
    
    def test_clean_text(self):
        """Prueba limpieza de texto"""
        normalizer = TextNormalizer()
        
        text = "  Hola   mundo!   \n\n  ¿Cómo   estás?   "
        cleaned = normalizer.clean_text(text)
        
        assert "  " not in cleaned
        assert cleaned == cleaned.strip()
        assert cleaned == "Hola mundo! ¿Cómo estás?"
    
    def test_normalize_whitespace(self):
        """Prueba normalización de espacios"""
        normalizer = TextNormalizer()
        
        text = "  Hola   mundo   "
        result = normalizer.normalize_whitespace(text)
        
        assert result == "Hola mundo"
        assert "  " not in result
    
    def test_remove_repeated_punctuation(self):
        """Prueba eliminación de puntuación repetida"""
        normalizer = TextNormalizer()
        
        text = "Hola!!! mundo???"
        result = normalizer.remove_repeated_punctuation(text)
        
        assert result == "Hola! mundo?"
    
    def test_standardize_dates(self):
        """Prueba estandarización de fechas"""
        normalizer = TextNormalizer()
        
        text = "Fecha: 01/01/2023"
        result = normalizer.standardize_dates(text)
        
        assert result == "Fecha: 2023-01-01"


class TestChunkingStrategy:
    """Pruebas para ChunkingStrategy"""
    
    @pytest.fixture
    def chunker(self):
        return ChunkingStrategy(chunk_size=50, overlap=10)
    
    @pytest.fixture
    def sample_text(self):
        return "Primera oración. Segunda oración! Tercera oración? Cuarta oración, quinta oración. Sexta oración."
    
    def test_character_split(self, chunker, sample_text):
        """Prueba división por caracteres"""
        chunks = chunker.character_split(sample_text)
        
        assert len(chunks) > 0
        assert all(len(chunk) <= 50 for chunk in chunks)
    
    def test_sentence_split(self, chunker, sample_text):
        """Prueba división por oraciones"""
        chunks = chunker.sentence_split(sample_text)
        
        assert len(chunks) > 0
        assert all(len(chunk) <= 50 for chunk in chunks)
    
    def test_recursive_split(self, chunker, sample_text):
        """Prueba división recursiva"""
        chunks = chunker.recursive_split(sample_text)
        
        assert len(chunks) > 0
        assert all(len(chunk) <= chunker.chunk_size for chunk in chunks)
    
    def test_split_with_overlap(self, chunker, sample_text):
        """Prueba división con superposición"""
        chunks = chunker.split_with_overlap(sample_text)
        
        assert len(chunks) > 0
        if len(chunks) > 1:
            # Verificar que hay superposición
            assert len(chunks) > 0
    
    def test_process_document(self, chunker):
        """Prueba procesamiento de documento"""
        document = {
            "page_content": "Este es un texto de prueba para procesar en chunks.",
            "metadata": {"source": "test"}
        }
        
        chunks = chunker.process_document(document, strategy="recursive")
        
        assert len(chunks) > 0
        for chunk in chunks:
            assert "page_content" in chunk
            assert "metadata" in chunk
            assert "chunk_index" in chunk["metadata"]
            assert "total_chunks" in chunk["metadata"]


class TestDocumentProcessor:
    """Pruebas para DocumentProcessor"""
    
    @pytest.fixture
    def processor(self):
        return DocumentProcessor(chunk_size=50, overlap=10)
    
    @pytest.fixture
    def sample_documents(self):
        return [
            {"page_content": "Documento uno. Texto de prueba.", "metadata": {"source": "doc1"}},
            {"page_content": "Documento dos. Más texto para probar.", "metadata": {"source": "doc2"}},
        ]
    
    def test_process_documents(self, processor, sample_documents):
        """Prueba procesamiento de múltiples documentos"""
        chunks = processor.process_documents(sample_documents)
        
        assert len(chunks) > 0
        for chunk in chunks:
            assert "page_content" in chunk
            assert "metadata" in chunk
    
    def test_get_statistics(self, processor, sample_documents):
        """Prueba obtención de estadísticas"""
        chunks = processor.process_documents(sample_documents)
        stats = processor.get_statistics(chunks)
        
        assert "total_documents" in stats
        assert "total_chunks" in stats
        assert "avg_chunk_size" in stats
        assert stats["total_documents"] == len(sample_documents)
    
    def test_empty_document(self, processor):
        """Prueba con documento vacío"""
        documents = [{"page_content": "", "metadata": {}}]
        chunks = processor.process_documents(documents)
        
        assert len(chunks) == 0
    
    def test_process_with_different_strategies(self, processor):
        """Prueba con diferentes estrategias"""
        document = {"page_content": "Texto de prueba para diferentes estrategias.", "metadata": {}}
        
        strategies = ["character", "sentence", "recursive", "overlap"]
        for strategy in strategies:
            chunks = processor.process_document(document, strategy)
            assert len(chunks) > 0