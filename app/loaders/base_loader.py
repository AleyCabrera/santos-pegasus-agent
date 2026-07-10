"""Módulo base para cargadores de documentos"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from pathlib import Path
from app.utils.logger import logger


class BaseLoader(ABC):
    """Clase base abstracta para todos los cargadores de documentos"""
    
    def __init__(self, source_path: Path):
        """
        Inicializa el cargador
        
        Args:
            source_path: Ruta al archivo o directorio a cargar
        """
        self.source_path = source_path
        self.logger = logger
    
    @abstractmethod
    def load(self) -> List[Dict[str, Any]]:
        """
        Carga y procesa el documento
        
        Returns:
            Lista de diccionarios con el contenido y metadata
        """
        pass
    
    def validate_path(self) -> bool:
        """
        Valida que la ruta exista
        
        Returns:
            True si la ruta existe, False en caso contrario
        """
        exists = self.source_path.exists()
        if not exists:
            self.logger.error(f"Ruta no encontrada: {self.source_path}")
        return exists
    
    def get_file_size(self) -> int:
        """
        Obtiene el tamaño del archivo en bytes
        
        Returns:
            Tamaño del archivo
        """
        if self.source_path.is_file():
            return self.source_path.stat().st_size
        return 0