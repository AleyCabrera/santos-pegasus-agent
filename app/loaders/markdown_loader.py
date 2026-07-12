"""Cargador de documentos Markdown"""
from pathlib import Path
from typing import List, Dict, Any
from app.loaders.base_loader import BaseLoader
from app.utils.logger import logger


class MarkdownLoader(BaseLoader):
    """Cargador de documentos Markdown"""
    
    def __init__(self, source_path: Path):
        super().__init__(source_path)
        if not source_path.suffix.lower() in ['.md', '.markdown']:
            raise ValueError(f"El archivo {source_path} no es un Markdown")
    
    def load(self) -> List[Dict[str, Any]]:
        """Carga y extrae texto del Markdown"""
        if not self.validate_path():
            return []
        
        documents = []
        
        try:
            self.logger.info(f"Cargando Markdown: {self.source_path.name}")
            
            with open(self.source_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Crear documento con metadata
            document = {
                'content': content,
                'metadata': {
                    'source': str(self.source_path),
                    'filename': self.source_path.name,
                    'type': 'markdown',
                    'file_size': self.get_file_size()
                }
            }
            documents.append(document)
            
            self.logger.info(f"✅ Markdown cargado: {len(content)} caracteres")
            
        except Exception as e:
            self.logger.error(f"Error al cargar Markdown: {e}")
            raise
        
        return documents