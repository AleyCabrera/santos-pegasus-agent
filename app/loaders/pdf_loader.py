"""Cargador de documentos PDF"""

import io
from pathlib import Path
from typing import List, Dict, Any
from PyPDF2 import PdfReader
from app.loaders.base_loader import BaseLoader
from app.utils.logger import logger


class PDFLoader(BaseLoader):
    """Cargador de documentos PDF usando PyPDF2"""
    
    def __init__(self, source_path: Path):
        """
        Inicializa el cargador PDF
        
        Args:
            source_path: Ruta al archivo PDF
        """
        super().__init__(source_path)
        
        # Verificar extensión
        if not source_path.suffix.lower() == '.pdf':
            raise ValueError(f"El archivo {source_path} no es un PDF")
    
    def load(self) -> List[Dict[str, Any]]:
        """
        Carga y extrae texto del PDF
        
        Returns:
            Lista de páginas con texto y metadata
        """
        if not self.validate_path():
            return []
        
        documents = []
        
        try:
            self.logger.info(f"Cargando PDF: {self.source_path.name}")
            
            # Abrir el PDF
            with open(self.source_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                total_pages = len(pdf_reader.pages)
                
                self.logger.info(f"PDF tiene {total_pages} páginas")
                
                # Extraer texto de cada página
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    try:
                        text = page.extract_text()
                        
                        # Limpiar texto (remover saltos de línea excesivos)
                        text = ' '.join(text.split())
                        
                        if text.strip():  # Solo agregar si hay contenido
                            document = {
                                'content': text,
                                'metadata': {
                                    'source': str(self.source_path),
                                    'filename': self.source_path.name,
                                    'page': page_num,
                                    'total_pages': total_pages,
                                    'file_size': self.get_file_size(),
                                    'type': 'pdf'
                                }
                            }
                            documents.append(document)
                    except Exception as e:
                        self.logger.warning(f"Error al extraer página {page_num}: {e}")
                        continue
            
            self.logger.info(f"✅ Extraídas {len(documents)} páginas del PDF")
            
        except Exception as e:
            self.logger.error(f"Error al cargar PDF: {e}")
            raise
        
        return documents
    
    def load_metadata(self) -> Dict[str, Any]:
        """
        Extrae metadatos del PDF
        
        Returns:
            Diccionario con metadatos del PDF
        """
        if not self.validate_path():
            return {}
        
        try:
            with open(self.source_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                metadata = pdf_reader.metadata or {}
                
                return {
                    'filename': self.source_path.name,
                    'pages': len(pdf_reader.pages),
                    'size_bytes': self.get_file_size(),
                    'author': metadata.get('/Author', 'Desconocido'),
                    'title': metadata.get('/Title', 'Sin título'),
                    'subject': metadata.get('/Subject', 'Sin asunto'),
                    'creator': metadata.get('/Creator', 'Desconocido'),
                    'producer': metadata.get('/Producer', 'Desconocido'),
                    'creation_date': metadata.get('/CreationDate', 'Desconocida'),
                }
        except Exception as e:
            self.logger.error(f"Error al extraer metadatos: {e}")
            return {}