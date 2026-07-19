"""Agente RAG con LangChain y proveedores configurables"""
import sys
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
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
    """Agente RAG con LangChain y proveedores configurables"""
    
    def __init__(
        self,
        vector_store: Optional[FAISSVectorStore] = None,
        embedding_manager: Optional[EmbeddingManager] = None,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
        context_window: Optional[int] = None
    ):
        self.logger = logger
        self.model_name = model_name or settings.OLLAMA_MODEL
        self.temperature = temperature or settings.OLLAMA_TEMPERATURE
        self.context_window = context_window or settings.OLLAMA_CONTEXT_WINDOW
        
        self.embedding_manager = embedding_manager or EmbeddingManager()
        self.vector_store = vector_store or FAISSVectorStore(self.embedding_manager)
        
        if not self.vector_store.is_loaded:
            loaded = self.vector_store.load()
            if not loaded:
                self.logger.warning("⚠️ No se encontró vector store. Indexa documentos primero.")
        
        self.conversation_history: List[ChatMessage] = []
        self.max_history = 10
        
        self._setup_llm()
        self.logger.info(f"🤖 Agente RAG inicializado con proveedor: {settings.LLM_PROVIDER}")

    def _setup_llm(self):
        """Configura el modelo LLM según el proveedor definido en settings"""
        try:
            provider = settings.LLM_PROVIDER.lower()
            
            if provider == "huggingface":
                from langchain_huggingface import HuggingFaceEndpoint
                self.logger.info(f"🔗 Configurando LLM: Hugging Face ({settings.HF_MODEL})")
                self.llm = HuggingFaceEndpoint(
                    repo_id=settings.HF_MODEL,
                    huggingfacehub_api_token=settings.HF_TOKEN,
                    temperature=self.temperature,
                    max_new_tokens=512,
                )
            elif provider == "groq":
                from langchain_groq import ChatGroq
                self.logger.info(f"🔗 Configurando LLM: Groq ({settings.GROQ_MODEL})")
                self.llm = ChatGroq(
                    model=settings.GROQ_MODEL,
                    groq_api_key=settings.GROQ_API_KEY,
                    temperature=self.temperature,
                )
            else: # Default a Ollama para desarrollo local
                from langchain_ollama import ChatOllama
                self.logger.info(f"🔗 Configurando LLM: Ollama ({self.model_name})")
                self.llm = ChatOllama(
                    model=self.model_name,
                    temperature=self.temperature,
                    num_ctx=self.context_window,
                    base_url=settings.OLLAMA_HOST,
                    num_predict=512,
                    top_k=40,
                    top_p=0.9
                )
                self._test_connection()
                
        except Exception as e:
            self.logger.error(f"❌ Error configurando LLM: {e}")
            raise

    def _test_connection(self):
        """Prueba la conexión con Ollama (solo si se usa Ollama)"""
        if settings.LLM_PROVIDER.lower() != "ollama":
            self.logger.info("✅ LLM en la nube configurado (no se requiere prueba de conexión local)")
            return
            
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
        if not self.vector_store.is_loaded or self.vector_store.index is None:
            self.logger.warning("Vector store no disponible")
            return ""
        if self.vector_store.index.ntotal == 0:
            self.logger.warning("Vector store vacío")
            return ""
            
        results = self.vector_store.search(query, k=k)
        if not results:
            return ""
            
        context_parts = []
        for i, result in enumerate(results, 1):
            source = result['metadata'].get('filename', 'Documento')
            page = result['metadata'].get('page', '')
            context_parts.append(f"[Documento {i}] Fuente: {source}")
            if page:
                context_parts.append(f"Página: {page}")
            context_parts.append(f"Contenido: {result['content']}")
            context_parts.append("")
        return "\n".join(context_parts)

    def ask(self, question: str, k: int = 5, include_history: bool = True) -> Dict[str, Any]:
        self.logger.info(f"📝 Pregunta: {question[:100]}...")
        context = self._get_context(question, k=k)
        
        messages = []
        if include_history and self.conversation_history:
            history_text = self._format_history()
            if history_text:
                messages.append(("system", f"Historial de conversación:\n{history_text}"))
                
        if context:
            prompt = rag_prompt.format(context=context, question=question)
            messages.append(("user", prompt))
        else:
            prompt = no_context_prompt.format(question=question)
            messages.append(("user", prompt))
            
        try:
            chain = self.llm | StrOutputParser()
            response = chain.invoke(messages[-1][1])
            
            if not response or not response.strip():
                response = "Lo siento, no pude generar una respuesta. ¿Podrías reformular tu pregunta?"
                
            self._add_to_history(question, response)
            
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
        if not self.conversation_history:
            return ""
        history_parts = []
        for msg in self.conversation_history[-6:]:
            if msg.role == 'user':
                history_parts.append(f"Usuario: {msg.content}")
            else:
                history_parts.append(f"Asistente: {msg.content}")
        return "\n".join(history_parts)

    def _extract_sources(self, context: str) -> List[str]:
        sources = []
        for line in context.split('\n'):
            if 'Fuente:' in line:
                source = line.split('Fuente:')[-1].strip()
                if source and source not in sources:
                    sources.append(source)
        return sources

    def _add_to_history(self, question: str, answer: str):
        self.conversation_history.append(ChatMessage(role='user', content=question))
        self.conversation_history.append(ChatMessage(role='assistant', content=answer))
        if len(self.conversation_history) > self.max_history * 2:
            self.conversation_history = self.conversation_history[-self.max_history * 2:]

    def clear_history(self):
        self.conversation_history = []
        self.logger.info("🧹 Historial de conversación limpiado")

    def get_conversation_summary(self) -> str:
        if not self.conversation_history:
            return "No hay conversación previa."
        summary = f"Conversación con {len(self.conversation_history)} mensajes:\n"
        for i, msg in enumerate(self.conversation_history[-6:], 1):
            role = "👤 Usuario" if msg.role == 'user' else "🤖 Asistente"
            preview = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
            summary += f"{i}. {role}: {preview}\n"
        return summary

    def get_stats(self) -> Dict[str, Any]:
        return {
            'model': settings.HF_MODEL if settings.LLM_PROVIDER == "huggingface" else (settings.GROQ_MODEL if settings.LLM_PROVIDER == "groq" else self.model_name),
            'temperature': self.temperature,
            'context_window': self.context_window,
            'vector_store_loaded': self.vector_store.is_loaded,
            'documents_in_store': self.vector_store.index.ntotal if self.vector_store.index else 0,
            'history_length': len(self.conversation_history),
            'embedding_model': self.embedding_manager.model_name
        }