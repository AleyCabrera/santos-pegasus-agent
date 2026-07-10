"""Pruebas para el cargador PDF"""

import pytest
from pathlib import Path
from app.loaders.pdf_loader import PDFLoader


class TestPDFLoader:
    """Test suite para PDFLoader"""
    
    @pytest.fixture
    def sample_pdf_path(self, tmp_path):
        """Crea un PDF de prueba temporal"""
        # Como no podemos crear PDFs fácilmente en tests, usamos un archivo existente
        # o creamos uno usando reportlab
        from reportlab.pdfgen import canvas
        
        pdf_path = tmp_path / "test.pdf"
        c = canvas.Canvas(str(pdf_path))
        c.drawString(100, 750, "Test PDF Content")
        c.drawString(100, 700, "Line 2 of test content")
        c.save()
        
        return pdf_path
    
    def test_init_valid_pdf(self, sample_pdf_path):
        """Prueba inicialización con PDF válido"""
        loader = PDFLoader(sample_pdf_path)
        assert loader.source_path == sample_pdf_path
        assert loader.validate_path()
    
    def test_init_invalid_extension(self, tmp_path):
        """Prueba inicialización con archivo no PDF"""
        invalid_path = tmp_path / "test.txt"
        invalid_path.touch()
        
        with pytest.raises(ValueError, match="no es un PDF"):
            PDFLoader(invalid_path)
    
    def test_load_returns_documents(self, sample_pdf_path):
        """Prueba que la carga devuelve documentos"""
        loader = PDFLoader(sample_pdf_path)
        documents = loader.load()
        
        assert len(documents) > 0
        assert 'content' in documents[0]
        assert 'metadata' in documents[0]
        assert documents[0]['metadata']['filename'] == 'test.pdf'
        assert documents[0]['metadata']['type'] == 'pdf'
    
    def test_load_metadata(self, sample_pdf_path):
        """Prueba extracción de metadatos"""
        loader = PDFLoader(sample_pdf_path)
        metadata = loader.load_metadata()
        
        assert metadata['filename'] == 'test.pdf'
        assert 'pages' in metadata
        assert 'size_bytes' in metadata
    
    def test_load_nonexistent_file(self):
        """Prueba carga de archivo inexistente"""
        path = Path("nonexistent.pdf")
        loader = PDFLoader(path)
        documents = loader.load()
        assert documents == []  # Debe retornar lista vacía