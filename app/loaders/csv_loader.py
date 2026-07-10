"""Cargador de documentos CSV"""

import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional
from app.loaders.base_loader import BaseLoader
from app.utils.logger import logger


class CSVLoader(BaseLoader):
    """Cargador de documentos CSV usando Pandas"""
    
    def __init__(self, source_path: Path, encoding: str = 'utf-8'):
        """
        Inicializa el cargador CSV
        
        Args:
            source_path: Ruta al archivo CSV
            encoding: Codificación del archivo (default: utf-8)
        """
        super().__init__(source_path)
        self.encoding = encoding
        
        if not source_path.suffix.lower() == '.csv':
            raise ValueError(f"El archivo {source_path} no es un CSV")
    
    def load(self) -> List[Dict[str, Any]]:
        """
        Carga y procesa el archivo CSV
        
        Returns:
            Lista de filas del CSV como diccionarios
        """
        if not self.validate_path():
            return []
        
        documents = []
        
        try:
            self.logger.info(f"Cargando CSV: {self.source_path.name}")
            
            # Leer CSV con Pandas
            df = pd.read_csv(self.source_path, encoding=self.encoding)
            
            self.logger.info(f"CSV tiene {len(df)} filas y {len(df.columns)} columnas")
            
            # Convertir cada fila a un documento
            for idx, row in df.iterrows():
                # Convertir la fila a texto
                row_text = self._row_to_text(row, df.columns)
                
                document = {
                    'content': row_text,
                    'metadata': {
                        'source': str(self.source_path),
                        'filename': self.source_path.name,
                        'row_index': idx,
                        'total_rows': len(df),
                        'columns': list(df.columns),
                        'type': 'csv',
                        'file_size': self.get_file_size()
                    }
                }
                documents.append(document)
            
            self.logger.info(f"✅ Procesadas {len(documents)} filas del CSV")
            
        except Exception as e:
            self.logger.error(f"Error al cargar CSV: {e}")
            raise
        
        return documents
    
    def _row_to_text(self, row: pd.Series, columns: List[str]) -> str:
        """
        Convierte una fila del DataFrame a texto legible
        
        Args:
            row: Fila del DataFrame
            columns: Lista de nombres de columnas
            
        Returns:
            String con el contenido de la fila en formato texto
        """
        parts = []
        
        for col in columns:
            value = row[col]
            
            # Manejar valores nulos
            if pd.isna(value):
                value = 'No especificado'
            else:
                value = str(value)
            
            parts.append(f"{col}: {value}")
        
        return ' | '.join(parts)
    
    def load_as_dataframe(self) -> pd.DataFrame:
        """
        Carga el CSV directamente como DataFrame para análisis avanzado
        
        Returns:
            DataFrame de Pandas
        """
        if not self.validate_path():
            return pd.DataFrame()
        
        try:
            return pd.read_csv(self.source_path, encoding=self.encoding)
        except Exception as e:
            self.logger.error(f"Error al cargar DataFrame: {e}")
            return pd.DataFrame()
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Obtiene un resumen del contenido del CSV
        
        Returns:
            Diccionario con estadísticas del CSV
        """
        df = self.load_as_dataframe()
        if df.empty:
            return {}
        
        return {
            'filename': self.source_path.name,
            'rows': len(df),
            'columns': list(df.columns),
            'size_bytes': self.get_file_size(),
            'column_types': df.dtypes.to_dict(),
            'null_counts': df.isnull().sum().to_dict(),
            'memory_usage': df.memory_usage(deep=True).sum() / 1024,  # KB
        }