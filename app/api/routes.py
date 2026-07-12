"""Endpoints FastAPI para el agente RAG"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from app.models.schemas import (
    QuestionRequest,
    AnswerResponse,
    ChatMessageResponse,
    ConversationHistoryResponse,
    AgentStatsResponse,
    IndexDocumentsRequest,
    IndexStatusResponse,
    ErrorResponse
)
from app.services.chat_service import ChatService
from app.services.indexing_service import IndexingService
from app.utils.logger import logger

# Crear router
router = APIRouter(prefix="/api/v1", tags=["RAG Agent"])

# Dependencias
def get_chat_service() -> ChatService:
    """Dependencia para el servicio de chat"""
    return ChatService()

def get_indexing_service() -> IndexingService:
    """Dependencia para el servicio de indexación"""
    return IndexingService()


# Endpoints de Chat
@router.post("/ask", response_model=AnswerResponse)
async def ask_question(
    request: QuestionRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Hace una pregunta al agente RAG
    
    - **question**: Pregunta del usuario
    - **k**: Número de documentos a recuperar (1-20)
    - **include_history**: Incluir historial de conversación
    """
    try:
        response = chat_service.ask(
            question=request.question,
            k=request.k,
            include_history=request.include_history
        )
        return response
    except Exception as e:
        logger.error(f"Error en /ask: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=ConversationHistoryResponse)
async def get_history(
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Obtiene el historial de conversación
    """
    messages = chat_service.get_history()
    return ConversationHistoryResponse(
        messages=messages,
        total_messages=len(messages)
    )


@router.delete("/history")
async def clear_history(
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Limpia el historial de conversación
    """
    return chat_service.clear_history()


@router.get("/stats", response_model=AgentStatsResponse)
async def get_stats(
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Obtiene estadísticas del agente
    """
    stats = chat_service.get_stats()
    return AgentStatsResponse(**stats)


# Endpoints de Indexación
@router.post("/index", response_model=IndexStatusResponse)
async def index_documents(
    request: IndexDocumentsRequest,
    indexing_service: IndexingService = Depends(get_indexing_service)
):
    """
    Indexa documentos desde los directorios configurados
    """
    try:
        if request.force_reindex:
            result = indexing_service.reindex(
                chunk_strategy=request.chunk_strategy
            )
        else:
            result = indexing_service.index_directories(
                pdf_dir=request.pdf_dir,
                csv_dir=request.csv_dir,
                txt_dir=request.txt_dir,
                chunk_strategy=request.chunk_strategy
            )
        
        return IndexStatusResponse(**result)
    except Exception as e:
        logger.error(f"Error en /index: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Health check
@router.get("/health")
async def health_check():
    """
    Verifica el estado del servicio
    """
    return {
        "status": "healthy",
        "service": "Santos Pegasus Soluciones RAG Agent",
        "version": "1.0.0"
    }