"""
Módulo de loaders para cargar diferentes tipos de documentos
"""

from app.loaders.pdf_loader import PDFLoader
from app.loaders.csv_loader import CSVLoader
from app.loaders.markdown_loader import MarkdownLoader
from app.loaders.base_loader import BaseLoader

__all__ = [
    'PDFLoader',
    'CSVLoader',
    'MarkdownLoader',
    'BaseLoader'
]

