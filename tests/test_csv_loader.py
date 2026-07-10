"""Pruebas para el cargador CSV"""

import pytest
import pandas as pd
from pathlib import Path
from app.loaders.csv_loader import CSVLoader


class TestCSVLoader:
    """Test suite para CSVLoader"""
    
    @pytest.fixture
    def sample_csv_path(self, tmp_path):
        """Crea un CSV de prueba temporal"""
        csv_path = tmp_path / "test.csv"
        
        data = {
            'Nombre': ['Juan', 'Maria', 'Carlos'],
            'Edad': [30, 25, 35],
            'Ciudad': ['Madrid', 'Barcelona', 'Valencia']
        }
        df = pd.DataFrame(data)
        df.to_csv(csv_path, index=False)
        
        return csv_path
    
    def test_init_valid_csv(self, sample_csv_path):
        """Prueba inicialización con CSV válido"""
        loader = CSVLoader(sample_csv_path)
        assert loader.source_path == sample_csv_path
        assert loader.validate_path()
    
    def test_init_invalid_extension(self, tmp_path):
        """Prueba inicialización con archivo no CSV"""
        invalid_path = tmp_path / "test.txt"
        invalid_path.touch()
        
        with pytest.raises(ValueError, match="no es un CSV"):
            CSVLoader(invalid_path)
    
    def test_load_returns_documents(self, sample_csv_path):
        """Prueba que la carga devuelve documentos"""
        loader = CSVLoader(sample_csv_path)
        documents = loader.load()
        
        assert len(documents) == 3  # Tres filas
        assert 'content' in documents[0]
        assert 'metadata' in documents[0]
        assert documents[0]['metadata']['filename'] == 'test.csv'
        assert documents[0]['metadata']['type'] == 'csv'
        assert documents[0]['metadata']['columns'] == ['Nombre', 'Edad', 'Ciudad']
    
    def test_load_as_dataframe(self, sample_csv_path):
        """Prueba carga como DataFrame"""
        loader = CSVLoader(sample_csv_path)
        df = loader.load_as_dataframe()
        
        assert len(df) == 3
        assert list(df.columns) == ['Nombre', 'Edad', 'Ciudad']
        assert df.iloc[0]['Nombre'] == 'Juan'
    
    def test_get_summary(self, sample_csv_path):
        """Prueba obtención de resumen"""
        loader = CSVLoader(sample_csv_path)
        summary = loader.get_summary()
        
        assert summary['filename'] == 'test.csv'
        assert summary['rows'] == 3
        assert summary['columns'] == ['Nombre', 'Edad', 'Ciudad']
        assert 'size_bytes' in summary