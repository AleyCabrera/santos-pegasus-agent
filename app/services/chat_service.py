"""Servicio de chat para el agente RAG"""

from typing import Dict, Any, Optional, List
from app.agents.rag_agent import RAGAgent, ChatMessage
from app.models.schemas import AnswerResponse, ChatMessageResponse
from app.utils.logger import logger


class ChatService:
    """
    Servicio de chat que envuelve al agente RAG
    """
    
    def __init__(self):
        """Inicializa el servicio de chat"""
        self.agent = RAGAgent()
        self.logger = logger
        self.logger.info("💬 Servicio de chat inicializado")
    
    def ask(self, question: str, k: int = 5, include_history: bool = True) -> AnswerResponse:
        """
        Procesa una pregunta y devuelve respuesta estructurada
        
        Args:
            question: Pregunta del usuario
            k: Número de documentos a recuperar
            include_history: Incluir historial
            
        Returns:
            AnswerResponse con la respuesta
        """
        result = self.agent.ask(question, k=k, include_history=include_history)
        
        return AnswerResponse(
            question=result['question'],
            answer=result['answer'],
            sources=result.get('sources', []),
            context_used=result.get('context_used', False),
            k=k,
            context_length=result.get('context_length', 0)
        )
    
    def get_history(self) -> List[ChatMessageResponse]:
        """
        Obtiene el historial de conversación
        
        Returns:
            Lista de mensajes formateados
        """
        return [
            ChatMessageResponse(
                role=msg.role,
                content=msg.content
            )
            for msg in self.agent.conversation_history
        ]
    
    def clear_history(self) -> Dict[str, Any]:
        """
        Limpia el historial de conversación
        
        Returns:
            Confirmación
        """
        self.agent.clear_history()
        return {"status": "success", "message": "Historial limpiado"}
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del agente
        
        Returns:
            Estadísticas
        """
        return self.agent.get_stats()
    
    def get_conversation_summary(self) -> str:
        """
        Obtiene resumen de la conversación
        
        Returns:
            Resumen en texto
        """
        return self.agent.get_conversation_summary()