"""Esquemas Pydantic para la API"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class QuestionRequest(BaseModel):
    """Request para hacer una pregunta"""
    question: str = Field(..., description="Pregunta del usuario", min_length=1)
    k: int = Field(5, description="Número de documentos a recuperar", ge=1, le=20)
    include_history: bool = Field(True, description="Incluir historial de conversación")


class AnswerResponse(BaseModel):
    """Response con la respuesta"""
    question: str
    answer: str
    sources: List[str] = Field(default_factory=list)
    context_used: bool = False
    k: int = 5
    context_length: int = 0
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class ChatMessageResponse(BaseModel):
    """Mensaje de chat"""
    role: str
    content: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class ConversationHistoryResponse(BaseModel):
    """Historial de conversación"""
    messages: List[ChatMessageResponse]
    total_messages: int


class AgentStatsResponse(BaseModel):
    """Estadísticas del agente"""
    model: str
    temperature: float
    context_window: int
    vector_store_loaded: bool
    documents_in_store: int
    history_length: int
    embedding_model: str


class IndexDocumentsRequest(BaseModel):
    """Request para indexar documentos"""
    pdf_dir: Optional[str] = None
    csv_dir: Optional[str] = None
    txt_dir: Optional[str] = None
    chunk_strategy: str = Field("recursive", description="Estrategia de chunking")
    force_reindex: bool = Field(False, description="Forzar re-indexación")


class IndexStatusResponse(BaseModel):
    """Estado de indexación"""
    documents_processed: int
    chunks_generated: int
    embeddings_generated: int
    total_added: int
    strategy: str
    vector_stats: Dict[str, Any]
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class ErrorResponse(BaseModel):
    """Response de error"""
    error: str
    detail: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())