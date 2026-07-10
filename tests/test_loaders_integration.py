"""Pruebas de integración para los loaders"""

import pytest
from pathlib import Path
from app.loaders.pdf_loader import PDFLoader
from app.loaders.csv_loader import CSVLoader
from app.utils.logger import logger


class TestLoadersIntegration:
    """Pruebas de integración con archivos reales"""
    
    @pytest.fixture
    def data_dir(self):
        """Ruta al directorio de datos de prueba"""
        base_dir = Path(__file__).parent.parent
        data_dir = base_dir / "data" / "pdfs"
        
        # Crear directorio si no existe
        data_dir.mkdir(parents=True, exist_ok=True)
        
        return data_dir
    
    def test_load_pdf_documents(self, data_dir):
        """Prueba carga de documentos PDF reales"""
        pdf_files = list(data_dir.glob("*.pdf"))
        
        if not pdf_files:
            logger.warning("No hay PDFs para probar, saltando test")
            return
        
        for pdf_file in pdf_files:
            loader = PDFLoader(pdf_file)
            documents = loader.load()
            
            assert len(documents) > 0
            assert all('content' in doc for doc in documents)
            assert all('metadata' in doc for doc in documents)
            
            logger.info(f"✅ PDF {pdf_file.name}: {len(documents)} páginas")
    
    def test_load_csv_documents(self):
        """Prueba carga de documentos CSV reales"""
        csv_dir = Path("data") / "csv"
        csv_files = list(csv_dir.glob("*.csv"))
        
        if not csv_files:
            logger.warning("No hay CSVs para probar, saltando test")
            return
        
        for csv_file in csv_files:
            loader = CSVLoader(csv_file)
            documents = loader.load()
            
            assert len(documents) > 0
            assert all('content' in doc for doc in documents)
            assert all('metadata' in doc for doc in documents)
            
            logger.info(f"✅ CSV {csv_file.name}: {len(documents)} filas")