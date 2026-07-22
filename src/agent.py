"""
Módulo del agente RAG
Orquestación de la cadena de recuperación y generación
"""
from langchain_core.prompts import ChatPromptTemplate
from langchain_cohere import ChatCohere
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from src.config import COHERE_API_KEY, TEMPERATURE, MAX_RETRIEVAL_DOCS


def format_docs(docs):
    """Formatea los documentos recuperados para el prompt"""
    if not docs:
        return "No hay documentos relevantes."
    
    formatted = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "Documento desconocido")
        content = doc.page_content[:500]  # Limitar para no exceder contexto
        formatted.append(f"[Fuente {i}: {source}]\n{content}")
    
    return "\n\n---\n\n".join(formatted)