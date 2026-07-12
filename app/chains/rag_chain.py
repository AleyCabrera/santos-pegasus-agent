"""Cadena RAG con LangChain"""

from typing import List, Dict, Any, Optional
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from app.config import settings
from app.vector_store.faiss_store import FAISSVectorStore
from app.embeddings.embedding_manager import EmbeddingManager
from app.prompts.prompt_templates import RAG_PROMPT_TEMPLATE
from app.utils.logger import logger


class RAGChain:
    """
    Cadena RAG completa usando LangChain
    """
    
    def __init__(
        self,
        vector_store: Optional[FAISSVectorStore] = None,
        embedding_manager: Optional[EmbeddingManager] = None,
        model_name: Optional[str] = None
    ):
        """
        Inicializa la cadena RAG
        
        Args:
            vector_store: Vector store para búsqueda
            embedding_manager: Gestor de embeddings
            model_name: Nombre del modelo Ollama
        """
        self.embedding_manager = embedding_manager or EmbeddingManager()
        self.vector_store = vector_store or FAISSVectorStore(self.embedding_manager)
        
        if not self.vector_store.is_loaded:
            self.vector_store.load()
        
        self.model_name = model_name or settings.OLLAMA_MODEL
        
        # Configurar LLM
        self.llm = ChatOllama(
            model=self.model_name,
            temperature=settings.OLLAMA_TEMPERATURE,
            num_ctx=settings.OLLAMA_CONTEXT_WINDOW,
            base_url=settings.OLLAMA_HOST
        )
        
        # Crear prompt
        self.prompt = ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)
        
        # Crear cadena
        self.chain = (
            {
                "context": self._retrieve_context,
                "question": RunnablePassthrough()
            }
            | self.prompt
            | self.llm
            | StrOutputParser()
        )
        
        self.logger = logger
        self.logger.info(f"🔗 Cadena RAG inicializada con modelo: {self.model_name}")
    
    def _retrieve_context(self, question: str) -> str:
        """
        Recupera contexto relevante para la pregunta
        
        Args:
            question: Pregunta del usuario
            
        Returns:
            Contexto formateado
        """
        results = self.vector_store.search(question, k=5)
        
        if not results:
            return "No se encontró información relevante."
        
        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(f"[Documento {i}]")
            context_parts.append(result['content'])
            context_parts.append("")
        
        return "\n".join(context_parts)
    
    def invoke(self, question: str) -> str:
        """
        Ejecuta la cadena RAG con una pregunta
        
        Args:
            question: Pregunta del usuario
            
        Returns:
            Respuesta generada
        """
        try:
            response = self.chain.invoke(question)
            return response
        except Exception as e:
            self.logger.error(f"Error en cadena RAG: {e}")
            return f"Error generando respuesta: {str(e)}"
    
    def stream(self, question: str):
        """
        Genera respuesta en streaming
        
        Args:
            question: Pregunta del usuario
            
        Yields:
            Fragmentos de respuesta
        """
        try:
            for chunk in self.chain.stream(question):
                yield chunk
        except Exception as e:
            self.logger.error(f"Error en streaming: {e}")
            yield f"Error generando respuesta: {str(e)}"