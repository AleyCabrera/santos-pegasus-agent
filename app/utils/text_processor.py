# app/utils/text_processor.py
"""
Procesamiento de texto para documentos
"""
import re
from typing import List, Dict, Any, Optional
from app.utils.logger import logger


class TextNormalizer:
    """Normalizador de texto para procesamiento de documentos"""
    
    def __init__(self):
        self.special_chars = {
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
            'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
            'ñ': 'n', 'Ñ': 'N'
        }
    
    def clean_text(self, text: str) -> str:
        """
        Limpia y normaliza el texto
        
        Args:
            text: Texto a limpiar
        
        Returns:
            Texto limpio y normalizado
        """
        if not text:
            return ""
        
        # Eliminar espacios al inicio y final
        text = text.strip()
        
        # Reemplazar saltos de línea y tabs con espacios
        text = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
        
        # Eliminar espacios múltiples
        text = re.sub(r' +', ' ', text)
        
        # Eliminar espacios antes de signos de puntuación
        text = re.sub(r' ([,.;:!?])', r'\1', text)
        
        # Asegurar espacio después de signos de puntuación
        text = re.sub(r'([,.;:!?])([^\s])', r'\1 \2', text)
        
        return text.strip()
    
    def normalize_whitespace(self, text: str) -> str:
        """Normaliza los espacios en blanco"""
        if not text:
            return ""
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def remove_repeated_punctuation(self, text: str) -> str:
        """Elimina signos de puntuación repetidos"""
        if not text:
            return ""
        text = re.sub(r'([!?.]){2,}', r'\1', text)
        return text
    
    def standardize_dates(self, text: str) -> str:
        """Estandariza formatos de fecha"""
        if not text:
            return ""
        # Ejemplo: 01/01/2023 -> 2023-01-01
        text = re.sub(r'(\d{2})/(\d{2})/(\d{4})', r'\3-\2-\1', text)
        return text


class ChunkingStrategy:
    """Estrategias de división de texto en chunks"""
    
    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.normalizer = TextNormalizer()
    
    def character_split(self, text: str) -> List[str]:
        """Divide el texto por caracteres"""
        if not text:
            return []
        
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = min(start + self.chunk_size, text_length)
            chunks.append(text[start:end])
            start = end - self.overlap if end < text_length else text_length
        
        return chunks
    
    def sentence_split(self, text: str) -> List[str]:
        """Divide el texto por oraciones"""
        if not text:
            return []
        
        # Dividir por oraciones
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) + 1 <= self.chunk_size:
                if current_chunk:
                    current_chunk += " "
                current_chunk += sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def recursive_split(self, text: str) -> List[str]:
        """Divide el texto recursivamente respetando el tamaño máximo"""
        if not text:
            return []
        
        # Si el texto es más corto que el chunk_size, devolverlo directamente
        if len(text) <= self.chunk_size:
            return [text]
        
        # Dividir por oraciones
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            # Si la oración es más larga que chunk_size, dividir por palabras
            if len(sentence) > self.chunk_size:
                # Si hay texto acumulado, guardarlo primero
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = ""
                
                # Dividir la oración larga por palabras
                words = sentence.split()
                temp_chunk = ""
                
                for word in words:
                    if len(temp_chunk) + len(word) + 1 <= self.chunk_size:
                        if temp_chunk:
                            temp_chunk += " "
                        temp_chunk += word
                    else:
                        if temp_chunk:
                            chunks.append(temp_chunk.strip())
                        temp_chunk = word
                
                if temp_chunk:
                    current_chunk = temp_chunk
            else:
                # Intentar agregar la oración al chunk actual
                if len(current_chunk) + len(sentence) + 1 <= self.chunk_size:
                    if current_chunk:
                        current_chunk += " "
                    current_chunk += sentence
                else:
                    # Guardar chunk actual y comenzar uno nuevo
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = sentence
        
        # Agregar el último chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def split_with_overlap(self, text: str) -> List[str]:
        """Divide el texto con superposición"""
        if not text:
            return []
        
        words = text.split()
        chunks = []
        i = 0
        
        while i < len(words):
            chunk_words = words[i:i + self.chunk_size]
            chunks.append(" ".join(chunk_words))
            i += self.chunk_size - self.overlap
        
        return chunks
    
    def process_document(self, document: Dict[str, Any], strategy: str = "recursive") -> List[Dict[str, Any]]:
        """Procesa un documento y lo divide en chunks"""
        # CORREGIDO: Buscar tanto 'page_content' como 'content'
        text = document.get("page_content") or document.get("content", "")
        
        if not text or not text.strip():
            return []
        
        # Seleccionar estrategia
        strategies = {
            "character": self.character_split,
            "sentence": self.sentence_split,
            "recursive": self.recursive_split,
            "overlap": self.split_with_overlap
        }
        
        split_func = strategies.get(strategy, self.recursive_split)
        chunks = split_func(text)
        
        # Crear documentos enriquecidos
        result = []
        for i, chunk in enumerate(chunks):
            chunk_doc = {
                "page_content": chunk,
                "metadata": {
                    **document.get("metadata", {}),
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "chunk_size": len(chunk)
                }
            }
            result.append(chunk_doc)
        
        return result


class DocumentProcessor:
    """Procesador de documentos completo"""
    
    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        self.chunking_strategy = ChunkingStrategy(chunk_size, overlap)
        self.normalizer = TextNormalizer()
    
    def process_documents(self, documents: List[Dict[str, Any]], strategy: str = "recursive") -> List[Dict[str, Any]]:
        """Procesa múltiples documentos"""
        all_chunks = []
        for doc in documents:
            chunks = self.process_document(doc, strategy)
            all_chunks.extend(chunks)
        return all_chunks
    
    def process_document(self, document: Dict[str, Any], strategy: str = "recursive") -> List[Dict[str, Any]]:
        """Procesa un solo documento"""
        # CORREGIDO: Buscar tanto 'page_content' como 'content'
        if "page_content" in document:
            document["page_content"] = self.normalizer.clean_text(document["page_content"])
        elif "content" in document:
            document["page_content"] = self.normalizer.clean_text(document["content"])
        
        # Dividir en chunks
        return self.chunking_strategy.process_document(document, strategy)
    
    def get_statistics(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Obtiene estadísticas de los documentos"""
        if not documents:
            # CORREGIDO: Incluir todas las claves incluso si está vacío
            return {
                "total_documents": 0,
                "total_chunks": 0,
                "avg_chunk_size": 0,
                "min_chunk_size": 0,
                "max_chunk_size": 0
            }
        
        # CORREGIDO: Buscar chunks que tengan 'chunk_index' en metadata
        chunked_docs = [doc for doc in documents if "chunk_index" in doc.get("metadata", {})]
        
        if not chunked_docs:
            return {
                "total_documents": len(documents),
                "total_chunks": 0,
                "avg_chunk_size": 0,
                "min_chunk_size": 0,
                "max_chunk_size": 0
            }
        
        chunk_sizes = [
            len(doc.get("page_content", "")) 
            for doc in chunked_docs 
            if doc.get("page_content")
        ]
        
        return {
            "total_documents": len(documents),
            "total_chunks": len(chunked_docs),
            "avg_chunk_size": sum(chunk_sizes) / len(chunk_sizes) if chunk_sizes else 0,
            "min_chunk_size": min(chunk_sizes) if chunk_sizes else 0,
            "max_chunk_size": max(chunk_sizes) if chunk_sizes else 0
        }


class Chunk:
    """Representa un chunk de texto con metadatos"""
    
    def __init__(self, text: str, metadata: dict = None):
        self.text = text
        self.metadata = metadata or {}
        self.length = len(text)
        self.page_content = text  # Para compatibilidad con otros formatos
    
    def __repr__(self):
        return f"Chunk(length={self.length}, metadata={self.metadata})"
    
    def to_dict(self) -> dict:
        """Convierte el chunk a diccionario"""
        return {
            "page_content": self.text,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Crea un Chunk desde un diccionario"""
        return cls(
            text=data.get("page_content", ""),
            metadata=data.get("metadata", {})
        )