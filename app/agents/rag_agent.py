"""Agente RAG con LangChain y Ollama"""
import sys
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.config import settings
from app.vector_store.faiss_store import FAISSVectorStore
from app.embeddings.embedding_manager import EmbeddingManager
from app.prompts.prompt_templates import rag_prompt, no_context_prompt
from app.utils.logger import logger


@dataclass
class ChatMessage:
    """Representa un mensaje en la conversación"""
    role: str  # 'user' o 'assistant'
    content: str
    timestamp: str = ""
    metadata: Optional[Dict[str, Any]] = None


class RAGAgent:
    """
    Agente RAG con LangChain y Ollama
    """
    
    def __init__(
        self,
        vector_store: Optional[FAISSVectorStore] = None,
        embedding_manager: Optional[EmbeddingManager] = None,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
        context_window: Optional[int] = None
    ):
        """
        Inicializa el agente RAG
        
        Args:
            vector_store: Vector store para búsqueda
            embedding_manager: Gestor de embeddings
            model_name: Nombre del modelo Ollama
            temperature: Temperatura para generación
            context_window: Tamaño de la ventana de contexto
        """
        # CORREGIDO: Asignar logger PRIMERO antes de cualquier método que lo use
        self.logger = logger
        
        # Configurar modelo
        self.model_name = model_name or settings.OLLAMA_MODEL
        self.temperature = temperature or settings.OLLAMA_TEMPERATURE
        self.context_window = context_window or settings.OLLAMA_CONTEXT_WINDOW
        
        # Inicializar componentes
        self.embedding_manager = embedding_manager or EmbeddingManager()
        self.vector_store = vector_store or FAISSVectorStore(self.embedding_manager)
        
        # Intentar cargar vector store existente
        if not self.vector_store.is_loaded:
            loaded = self.vector_store.load()
            if not loaded:
                self.logger.warning("⚠️ No se encontró vector store. Indexa documentos primero.")
        
        # Historial de conversación
        self.conversation_history: List[ChatMessage] = []
        self.max_history = 10  # Mantener solo los últimos 10 mensajes
        
        # Configurar modelo Ollama (AHORA self.logger ya existe)
        self._setup_llm()
        
        self.logger.info(f"🤖 Agente RAG inicializado con modelo: {self.model_name}")
    
    def _setup_llm(self):
        """Configura el modelo LLM con Ollama"""
        try:
            self.llm = ChatOllama(
                model=self.model_name,
                temperature=self.temperature,
                num_ctx=self.context_window,
                base_url=settings.OLLAMA_HOST,
                num_predict=512,  # Límite de tokens para respuesta
                top_k=40,
                top_p=0.9
            )
            
            # Verificar conexión
            self._test_connection()
            
        except Exception as e:
            self.logger.error(f"❌ Error configurando LLM: {e}")
            raise
    
    def _test_connection(self):
        """Prueba la conexión con Ollama"""
        try:
            test_response = self.llm.invoke("Hola, ¿estás funcionando?")
            if test_response and test_response.content:
                self.logger.info("✅ Conexión con Ollama establecida")
            else:
                self.logger.warning("⚠️ Respuesta vacía de Ollama")
        except Exception as e:
            self.logger.error(f"❌ Error conectando con Ollama: {e}")
            raise
    
    def _get_context(self, query: str, k: int = 5) -> str:
        """
        Obtiene contexto relevante para la consulta
        
        Args:
            query: Consulta del usuario
            k: Número de documentos a recuperar
        
        Returns:
            Contexto formateado como texto
        """
        if not self.vector_store.is_loaded or self.vector_store.index is None:
            self.logger.warning("Vector store no disponible")
            return ""
        
        if self.vector_store.index.ntotal == 0:
            self.logger.warning("Vector store vacío")
            return ""
        
        # Buscar documentos relevantes
        results = self.vector_store.search(query, k=k)
        
        if not results:
            return ""
        
        # Formatear contexto
        context_parts = []
        for i, result in enumerate(results, 1):
            source = result['metadata'].get('filename', 'Documento')
            page = result['metadata'].get('page', '')
            
            context_parts.append(f"[Documento {i}] Fuente: {source}")
            if page:
                context_parts.append(f"Página: {page}")
            context_parts.append(f"Contenido: {result['content']}")
            context_parts.append("")  # Línea vacía entre documentos
        
        return "\n".join(context_parts)
    
    def ask(
        self,
        question: str,
        k: int = 5,
        include_history: bool = True
    ) -> Dict[str, Any]:
        """
        Procesa una pregunta y genera una respuesta
        
        Args:
            question: Pregunta del usuario
            k: Número de documentos a recuperar
            include_history: Incluir historial de conversación
        
        Returns:
            Diccionario con respuesta y metadata
        """
        self.logger.info(f"📝 Pregunta: {question[:100]}...")
        
        # Obtener contexto
        context = self._get_context(question, k=k)
        
        # Preparar mensajes
        messages = []
        
        # Si hay historial, incluirlo
        if include_history and self.conversation_history:
            history_text = self._format_history()
            if history_text:
                messages.append(("system", f"Historial de conversación:\n{history_text}"))
        
        # Agregar pregunta actual
        if context:
            # Prompt con contexto
            prompt = rag_prompt.format(context=context, question=question)
            messages.append(("user", prompt))
        else:
            # Prompt sin contexto
            prompt = no_context_prompt.format(question=question)
            messages.append(("user", prompt))
        
        # Generar respuesta
        try:
            # Crear cadena simplificada
            chain = self.llm | StrOutputParser()
            
            # Obtener respuesta
            response = chain.invoke(messages[-1][1])
            
            # Verificar que la respuesta no esté vacía
            if not response or not response.strip():
                response = "Lo siento, no pude generar una respuesta. ¿Podrías reformular tu pregunta?"
            
            # Guardar en historial
            self._add_to_history(question, response)
            
            # Preparar resultado
            result = {
                'question': question,
                'answer': response,
                'context_used': bool(context),
                'sources': self._extract_sources(context) if context else [],
                'k': k,
                'context_length': len(context) if context else 0
            }
            
            self.logger.info(f"✅ Respuesta generada: {len(response)} caracteres")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error generando respuesta: {e}")
            return {
                'question': question,
                'answer': f"Lo siento, ocurrió un error: {str(e)}",
                'error': str(e),
                'context_used': False,
                'sources': []
            }
    
    def _format_history(self) -> str:
        """Formatea el historial de conversación"""
        if not self.conversation_history:
            return ""
        
        history_parts = []
        for msg in self.conversation_history[-6:]:  # Últimos 3 intercambios
            if msg.role == 'user':
                history_parts.append(f"Usuario: {msg.content}")
            else:
                history_parts.append(f"Asistente: {msg.content}")
        
        return "\n".join(history_parts)
    
    def _extract_sources(self, context: str) -> List[str]:
        """Extrae las fuentes del contexto"""
        sources = []
        for line in context.split('\n'):
            # CORREGIDO: La línea tiene el formato "[Documento X] Fuente: nombre.pdf"
            # Por lo tanto, validamos si 'Fuente:' está en la línea, no si empieza con ella.
            if 'Fuente:' in line:
                # Extraemos todo lo que está después de 'Fuente:'
                source = line.split('Fuente:')[-1].strip()
                if source and source not in sources:
                    sources.append(source)
        return sources
    
    def _add_to_history(self, question: str, answer: str):
        """Agrega mensaje al historial"""
        self.conversation_history.append(
            ChatMessage(role='user', content=question)
        )
        self.conversation_history.append(
            ChatMessage(role='assistant', content=answer)
        )
        
        # Limitar historial
        if len(self.conversation_history) > self.max_history * 2:
            self.conversation_history = self.conversation_history[-self.max_history * 2:]
    
    def clear_history(self):
        """Limpia el historial de conversación"""
        self.conversation_history = []
        self.logger.info("🧹 Historial de conversación limpiado")
    
    def get_conversation_summary(self) -> str:
        """Obtiene un resumen de la conversación"""
        if not self.conversation_history:
            return "No hay conversación previa."
        
        summary = f"Conversación con {len(self.conversation_history)} mensajes:\n"
        for i, msg in enumerate(self.conversation_history[-6:], 1):
            role = "👤 Usuario" if msg.role == 'user' else "🤖 Asistente"
            preview = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
            summary += f"{i}. {role}: {preview}\n"
        
        return summary
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del agente"""
        return {
            'model': self.model_name,
            'temperature': self.temperature,
            'context_window': self.context_window,
            'vector_store_loaded': self.vector_store.is_loaded,
            'documents_in_store': self.vector_store.index.ntotal if self.vector_store.index else 0,
            'history_length': len(self.conversation_history),
            'embedding_model': self.embedding_manager.model_name
        }