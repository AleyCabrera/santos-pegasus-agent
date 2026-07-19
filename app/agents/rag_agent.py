"""Agente RAG con LangChain y proveedores configurables"""
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

# ==========================================
# SOLUCIÓN INFALIBLE PARA STREAMLIT CLOUD
# ==========================================
# Forzar la inclusión de la raíz del proyecto en el sys.path.
# Esto garantiza que los imports 'from app...' funcionen en cualquier entorno.
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from app.config import settings
from app.vector_store.faiss_store import FAISSVectorStore
from app.embeddings.embedding_manager import EmbeddingManager
from app.prompts.prompt_templates import rag_prompt, no_context_prompt
from app.utils.logger import logger

# ==========================================
# IMPORTACIONES DE LLMs A NIVEL DE MÓDULO
# (Necesario para que los tests puedan hacer mock)
# ==========================================
from langchain_ollama import ChatOllama

try:
    from langchain_huggingface import HuggingFaceEndpoint
except ImportError:
    HuggingFaceEndpoint = None

try:
    from langchain_groq import ChatGroq
except ImportError:
    ChatGroq = None


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
        
        # Uso seguro de getattr para evitar AttributeError en la nube
        self.llm_provider = getattr(settings, 'LLM_PROVIDER', 'ollama').lower()
        self.model_name = model_name or getattr(settings, 'OLLAMA_MODEL', 'llama3.2:3b')
        self.temperature = temperature or getattr(settings, 'OLLAMA_TEMPERATURE', 0.7)
        self.context_window = context_window or getattr(settings, 'OLLAMA_CONTEXT_WINDOW', 2048)
        
        self.embedding_manager = embedding_manager or EmbeddingManager()
        self.vector_store = vector_store or FAISSVectorStore(self.embedding_manager)
        
        if not self.vector_store.is_loaded:
            loaded = self.vector_store.load()
            if not loaded:
                self.logger.warning("⚠️ No se encontró vector store. Indexa documentos primero.")
        
        self.conversation_history: List[ChatMessage] = []
        self.max_history = 10
        
        self._setup_llm()
        self.logger.info(f"🤖 Agente RAG inicializado con proveedor: {self.llm_provider}")

    def _setup_llm(self):
        """Configura el modelo LLM según el proveedor definido en settings"""
        try:
            if self.llm_provider == "huggingface" and HuggingFaceEndpoint:
                hf_token = getattr(settings, 'HF_TOKEN', '')
                hf_model = getattr(settings, 'HF_MODEL', 'mistralai/Mistral-7B-Instruct-v0.2')
                
                if not hf_token or hf_token.startswith("hf_tu_token"):
                    self.logger.warning("⚠️ HF_TOKEN no configurado o es de ejemplo. La conexión fallará.")
                
                self.logger.info(f"🔗 Configurando LLM: Hugging Face ({hf_model})")
                self.llm = HuggingFaceEndpoint(
                    repo_id=hf_model,
                    huggingfacehub_api_token=hf_token,
                    temperature=self.temperature,
                    max_new_tokens=512,
                )
            elif self.llm_provider == "groq" and ChatGroq:
                groq_key = getattr(settings, 'GROQ_API_KEY', '')
                groq_model = getattr(settings, 'GROQ_MODEL', 'llama3-8b-8192')
                
                self.logger.info(f"🔗 Configurando LLM: Groq ({groq_model})")
                self.llm = ChatGroq(
                    model=groq_model,
                    groq_api_key=groq_key,
                    temperature=self.temperature,
                )
            else: # Default a Ollama para desarrollo local y tests
                self.logger.info(f"🔗 Configurando LLM: Ollama ({self.model_name})")
                self.llm = ChatOllama(
                    model=self.model_name,
                    temperature=self.temperature,
                    num_ctx=self.context_window,
                    base_url=getattr(settings, 'OLLAMA_HOST', 'http://localhost:11434'),
                    num_predict=512,
                    top_k=40,
                    top_p=0.9
                )
                self._test_connection()
                
        except Exception as e:
            self.logger.error(f"❌ Error configurando LLM: {e}")
            raise

    def _test_connection(self):
        """Prueba la conexión con Ollama"""
        try:
            test_response = self.llm.invoke("Hola, ¿estás funcionando?")
            if test_response and hasattr(test_response, 'content') and test_response.content:
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
            
            # Asegurar que la respuesta sea siempre un string
            response = str(response) if response else ""
            if not response.strip():
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
        hf_model = getattr(settings, 'HF_MODEL', 'N/A')
        groq_model = getattr(settings, 'GROQ_MODEL', 'N/A')
        
        current_model = hf_model if self.llm_provider == "huggingface" else (groq_model if self.llm_provider == "groq" else self.model_name)
        
        return {
            'model': current_model,
            'temperature': self.temperature,
            'context_window': self.context_window,
            'vector_store_loaded': self.vector_store.is_loaded,
            'documents_in_store': self.vector_store.index.ntotal if self.vector_store.index else 0,
            'history_length': len(self.conversation_history),
            'embedding_model': self.embedding_manager.model_name
        }