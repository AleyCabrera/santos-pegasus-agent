"""
Módulo del agente RAG
Orquestación de la cadena de recuperación y generación
"""
import logging
from typing import List, Dict, Any, Optional

from langchain_core.prompts import ChatPromptTemplate
from langchain_cohere import ChatCohere
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.schema import Document

from src.config import COHERE_API_KEY, TEMPERATURE, MAX_RETRIEVAL_DOCS
from src.vectorstore import load_vector_store, search_documents

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """
Eres un asistente experto para Santos Pegasus Soluciones. 
Tu función es responder preguntas basándote EXCLUSIVAMENTE en los documentos internos proporcionados.

REGLAS IMPORTANTES:
1. Responde SOLO con información que encuentres en los documentos.
2. Si no encuentras la respuesta en los documentos, di: "No encuentro esta información en los documentos disponibles."
3. SIEMPRE cita la fuente de la información (nombre del documento).
4. Sé conciso y profesional, pero con un tono amable.
5. Si la pregunta no está relacionada con los documentos, indícalo educadamente.

RESPONDE EN ESPAÑOL, a menos que la pregunta sea en otro idioma.
"""

USER_PROMPT_TEMPLATE = """
DOCUMENTOS RELEVANTES:
{context}

PREGUNTA DEL USUARIO:
{question}

INSTRUCCIONES ADICIONALES:
- Basa tu respuesta EXCLUSIVAMENTE en los documentos relevantes.
- Menciona la fuente de cada dato (nombre del documento).
- Si no encuentras la información, indícalo claramente.

RESPUESTA:
"""


def format_docs(docs: List[Document]) -> str:
    """Formatea los documentos recuperados para el prompt."""
    if not docs:
        return "No hay documentos relevantes disponibles."
    
    formatted = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "Documento desconocido")
        content = doc.page_content
        
        if len(content) > 600:
            content = content[:600] + "..."
        
        formatted.append(f"[Documento {i}] Fuente: {source}\n{content}")
    
    return "\n\n---\n\n".join(formatted)


def get_retriever(k: int = MAX_RETRIEVAL_DOCS):
    """Obtiene un retriever funcional desde el vector store."""
    vector_store = load_vector_store()
    
    if vector_store is None:
        logger.error("❌ No se pudo cargar el vector store")
        return None
    
    def retriever(query: str) -> List[Document]:
        """Retriever que busca documentos relevantes."""
        # 🔥 CORRECCIÓN: Asegurar que query es string
        if not isinstance(query, str):
            query = str(query)
        return search_documents(query, vector_store, k=k)
    
    logger.info("✅ Retriever configurado correctamente")
    return retriever


def create_rag_chain():
    """Crea la cadena RAG completa con LangChain y Cohere."""
    try:
        if not COHERE_API_KEY:
            logger.error("❌ COHERE_API_KEY no configurada")
            return None
        
        # 🔥 CORRECCIÓN: Modelo actualizado (activo)
        llm = ChatCohere(
            cohere_api_key=COHERE_API_KEY,
            model="command-a-03-2025",  # Modelo activo
            temperature=TEMPERATURE,
            max_tokens=500
        )
        logger.info(f"✅ LLM configurado: command-a-03-2025 (temp={TEMPERATURE})")
        
        retriever = get_retriever()
        if retriever is None:
            return None
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", USER_PROMPT_TEMPLATE)
        ])
        
        def retrieve_context(question: str) -> Dict[str, Any]:
            """Recupera documentos y prepara el contexto."""
            # 🔥 CORRECCIÓN: Forzar string aquí también
            if not isinstance(question, str):
                question = str(question)
            
            docs = retriever(question)
            context = format_docs(docs)
            
            return {
                "context": context,
                "question": question,
                "docs": docs
            }
        
        chain = (
            RunnablePassthrough() |
            retrieve_context |
            prompt |
            llm |
            StrOutputParser()
        )
        
        logger.info("✅ RAG Chain creada exitosamente")
        return chain
        
    except Exception as e:
        logger.error(f"❌ Error al crear RAG chain: {e}")
        import traceback
        traceback.print_exc()
        return None


def ask_question(chain, question: str) -> Dict[str, Any]:
    """Ejecuta una consulta en el agente RAG."""
    if chain is None:
        return {
            "answer": "❌ El agente no está configurado correctamente.",
            "sources": [],
            "success": False
        }
    
    if not question or not question.strip():
        return {
            "answer": "Por favor, haz una pregunta válida.",
            "sources": [],
            "success": False
        }
    
    try:
        logger.info(f"💬 Procesando pregunta: {question[:50]}...")
        # 🔥 CORRECCIÓN: Pasar la pregunta como string
        answer = chain.invoke({"question": str(question)})
        
        return {
            "answer": answer,
            "sources": [],
            "success": True
        }
        
    except Exception as e:
        logger.error(f"❌ Error al procesar pregunta: {e}")
        return {
            "answer": f"❌ Error al procesar la pregunta: {str(e)}",
            "sources": [],
            "success": False
        }


if __name__ == "__main__":
    import sys
    from src.ingest import process_documents
    from src.vectorstore import create_vector_store
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🚀 Inicializando agente RAG...")
    print("="*50)
    
    from src.vectorstore import load_vector_store
    vector_store = load_vector_store()
    
    if vector_store is None:
        print("📂 No se encontró índice FAISS. Creando uno nuevo...")
        chunks = process_documents()
        if chunks:
            vector_store = create_vector_store(chunks)
        else:
            print("❌ No se pudieron procesar documentos")
            sys.exit(1)
    
    chain = create_rag_chain()
    
    if chain is None:
        print("❌ No se pudo crear la RAG chain")
        sys.exit(1)
    
    print("\n✅ Agente listo para preguntas!")
    print("="*50)
    
    test_questions = [
        "¿Cuál es la filosofía de Santos Pegasus Soluciones?",
        "¿Qué herramientas usa la empresa para desarrollo backend?",
        "¿Cómo se manejan los incidentes críticos?",
        "¿Qué es la arquitectura de microservicios?"
    ]
    
    for question in test_questions:
        print(f"\n🔍 Pregunta: {question}")
        print("-"*40)
        
        result = ask_question(chain, question)
        
        if result["success"]:
            print(f"✅ Respuesta:\n{result['answer']}")
        else:
            print(f"❌ Error: {result['answer']}")
        
        print("="*50)