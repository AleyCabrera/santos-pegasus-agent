"""Pruebas para el cargador CSV"""

import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional
from app.loaders.base_loader import BaseLoader
from app.utils.logger import logger


class CSVLoader(BaseLoader):
    def __init__(self, source_path: Path, encoding: str = 'utf-8', delimiter: Optional[str] = None):
        self.source_path = Path(source_path)
        self.encoding = encoding
        self.delimiter = delimiter
        self._auto_detect_delimiter()
    
    def _auto_detect_delimiter(self):
        """Auto-detecta el delimitador del CSV"""
        if self.delimiter is None:
            try:
                with open(self.source_path, 'r', encoding=self.encoding) as f:
                    first_line = f.readline()
                    # Detecta posibles delimitadores
                    delimiters = [',', ';', '\t', '|']
                    for delim in delimiters:
                        if delim in first_line:
                            self.delimiter = delim
                            break
                    if self.delimiter is None:
                        self.delimiter = ','  # Default
                    logger.debug(f"Delimitador auto-detectado: '{self.delimiter}'")
            except Exception as e:
                logger.warning(f"Error detectando delimitador: {e}, usando coma por defecto")
                self.delimiter = ','
    
    def load(self) -> List[Dict[str, Any]]:
        """Carga el CSV y devuelve lista de documentos"""
        try:
            logger.info(f"Cargando CSV: {self.source_path.name}")
            
            # Intenta cargar con diferentes configuraciones
            try:
                df = pd.read_csv(
                    self.source_path, 
                    encoding=self.encoding,
                    delimiter=self.delimiter,
                    on_bad_lines='warn'  # En lugar de error
                )
            except pd.errors.ParserError:
                # Si falla, intenta con diferentes parámetros
                df = pd.read_csv(
                    self.source_path,
                    encoding=self.encoding,
                    delimiter=self.delimiter,
                    engine='python',  # Más tolerante
                    on_bad_lines='skip'  # Salta líneas problemáticas
                )
            
            logger.info(f"CSV tiene {len(df)} filas y {len(df.columns)} columnas")
            
            # Convertir a documentos
            documents = []
            for idx, row in df.iterrows():
                content = " | ".join([f"{col}: {row[col]}" for col in df.columns])
                metadata = {
                    "source": str(self.source_path),
                    "filename": self.source_path.name,
                    "row_index": idx,
                    "columns": list(df.columns)
                }
                documents.append({
                    "page_content": content,
                    "metadata": metadata
                })
            
            logger.info(f"✅ Procesadas {len(documents)} filas del CSV")
            return documents
            
        except Exception as e:
            logger.error(f"Error al cargar CSV: {e}")
            raise
    
    def load_as_dataframe(self) -> pd.DataFrame:
        """Carga el CSV como DataFrame de pandas"""
        try:
            return pd.read_csv(
                self.source_path,
                encoding=self.encoding,
                delimiter=self.delimiter,
                on_bad_lines='warn'
            )
        except Exception as e:
            logger.error(f"Error al cargar DataFrame: {e}")
            raise
    
    def get_summary(self) -> Dict[str, Any]:
        """Obtiene un resumen del CSV"""
        try:
            df = self.load_as_dataframe()
            return {
                "filename": self.source_path.name,
                "num_rows": len(df),
                "num_columns": len(df.columns),
                "columns": df.columns.tolist(),
                "memory_usage": df.memory_usage(deep=True).sum() / 1024,  # KB
            }
        except Exception as e:
            logger.error(f"Error obteniendo resumen: {e}")
            return {"error": str(e)}