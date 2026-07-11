"""
Módulo de loaders para cargar diferentes tipos de documentos
"""

from app.loaders.pdf_loader import PDFLoader
from app.loaders.csv_loader import CSVLoader
from app.loaders.base_loader import BaseLoader

__all__ = [
    'PDFLoader',
    'CSVLoader', 
    'BaseLoader'
]
