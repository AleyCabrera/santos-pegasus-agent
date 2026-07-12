"""Tests para el agente RAG y servicio de chat"""
import sys
from pathlib import Path

# Agregar la raíz del proyecto al sys.path para que Python encuentre el módulo 'app'
sys.path.insert(0, str(Path(__file__).parent.parent))

# Ahora sí podemos importar los módulos del proyecto
import pytest
from unittest.mock import Mock, patch, MagicMock
from app.agents.rag_agent import RAGAgent
from app.services.chat_service import ChatService
from app.utils.logger import logger


class TestRAGAgent:
    """Tests para RAGAgent"""
    
    @pytest.fixture
    def mock_vector_store(self):
        """Mock del vector store"""
        store = Mock()
        store.is_loaded = True
        store.index = Mock()
        store.index.ntotal = 12
        store.search.return_value = [
            {
                'content': 'Contenido de prueba sobre Santos Pegasus',
                'metadata': {'filename': 'test.pdf', 'page': 1},
                'similarity': 0.85
            }
        ]
        return store
    
    @pytest.fixture
    def mock_embedding_manager(self):
        """Mock del embedding manager"""
        manager = Mock()
        manager.model_name = 'all-MiniLM-L6-v2'
        manager.model = Mock()
        manager.model.get_sentence_embedding_dimension.return_value = 384
        return manager
    
    @patch('app.agents.rag_agent.ChatOllama')
    def test_agent_initialization(self, mock_chat_ollama, mock_vector_store, mock_embedding_manager):
        """Prueba inicialización del agente"""
        mock_llm_instance = Mock()
        mock_llm_instance.invoke.return_value = Mock(content="Respuesta de prueba")
        mock_chat_ollama.return_value = mock_llm_instance
        
        agent = RAGAgent(
            vector_store=mock_vector_store,
            embedding_manager=mock_embedding_manager
        )
        
        assert agent.model_name == 'llama3.2:3b'
        assert agent.temperature == 0.7
        assert agent.context_window == 2048
        assert len(agent.conversation_history) == 0
    
    @patch('app.agents.rag_agent.ChatOllama')
    def test_ask_with_context(self, mock_chat_ollama, mock_vector_store, mock_embedding_manager):
        """Prueba pregunta con contexto"""
        mock_llm_instance = Mock()
        
        mock_response = Mock()
        mock_response.content = "Esta es la respuesta del agente sobre Santos Pegasus"
        mock_llm_instance.invoke.return_value = mock_response
        
        mock_chain = Mock()
        mock_chain.invoke.return_value = "Esta es la respuesta del agente sobre Santos Pegasus"
        mock_llm_instance.__or__ = Mock(return_value=mock_chain)
        
        mock_chat_ollama.return_value = mock_llm_instance
        
        agent = RAGAgent(
            vector_store=mock_vector_store,
            embedding_manager=mock_embedding_manager
        )
        
        result = agent.ask("¿Qué es Santos Pegasus?")
        
        assert 'question' in result
        assert 'answer' in result
        assert result['context_used'] is True
        assert len(result['sources']) > 0
    
    @patch('app.agents.rag_agent.ChatOllama')
    def test_ask_without_context(self, mock_chat_ollama, mock_vector_store, mock_embedding_manager):
        """Prueba pregunta sin contexto"""
        mock_vector_store.search.return_value = []
        
        mock_llm_instance = Mock()
        mock_chain = Mock()
        mock_chain.invoke.return_value = "No tengo información sobre eso en la documentación disponible"
        mock_llm_instance.__or__ = Mock(return_value=mock_chain)
        mock_chat_ollama.return_value = mock_llm_instance
        
        agent = RAGAgent(
            vector_store=mock_vector_store,
            embedding_manager=mock_embedding_manager
        )
        
        result = agent.ask("¿Qué es algo que no existe?")
        
        assert 'question' in result
        assert 'answer' in result
        assert result['context_used'] is False
    
    @patch('app.agents.rag_agent.ChatOllama')
    def test_get_stats(self, mock_chat_ollama, mock_vector_store, mock_embedding_manager):
        """Prueba obtención de estadísticas"""
        mock_llm_instance = Mock()
        mock_llm_instance.invoke.return_value = Mock(content="OK")
        mock_chat_ollama.return_value = mock_llm_instance
        
        agent = RAGAgent(
            vector_store=mock_vector_store,
            embedding_manager=mock_embedding_manager
        )
        
        stats = agent.get_stats()
        
        assert 'model' in stats
        assert 'documents_in_store' in stats
        assert stats['documents_in_store'] == 12
    
    @patch('app.agents.rag_agent.ChatOllama')
    def test_clear_history(self, mock_chat_ollama, mock_vector_store, mock_embedding_manager):
        """Prueba limpieza de historial"""
        mock_llm_instance = Mock()
        mock_llm_instance.invoke.return_value = Mock(content="OK")
        mock_chat_ollama.return_value = mock_llm_instance
        
        agent = RAGAgent(
            vector_store=mock_vector_store,
            embedding_manager=mock_embedding_manager
        )
        
        agent.conversation_history.append(Mock(role='user', content='Hola'))
        agent.conversation_history.append(Mock(role='assistant', content='Hola!'))
        
        assert len(agent.conversation_history) == 2
        
        agent.clear_history()
        
        assert len(agent.conversation_history) == 0


class TestChatService:
    """Tests para ChatService"""
    
    @pytest.fixture
    def mock_agent(self):
        """Mock del agente"""
        agent = Mock()
        agent.ask.return_value = {
            'question': '¿Qué es esto?',
            'answer': 'Esto es una prueba',
            'sources': ['test.pdf'],
            'context_used': True,
            'context_length': 100
        }
        agent.conversation_history = []
        agent.get_stats.return_value = {
            'model': 'llama3.2:3b',
            'documents_in_store': 12,
            'history_length': 0
        }
        return agent
    
    @patch('app.services.chat_service.RAGAgent')
    def test_chat_service_initialization(self, mock_agent_class):
        """Prueba inicialización del servicio"""
        service = ChatService()
        assert service.agent is not None
    
    @patch('app.services.chat_service.RAGAgent')
    def test_ask_method(self, mock_agent_class):
        """Prueba método ask"""
        mock_agent = Mock()
        mock_agent.ask.return_value = {
            'question': 'Pregunta',
            'answer': 'Respuesta',
            'sources': [],
            'context_used': False,
            'context_length': 0
        }
        mock_agent_class.return_value = mock_agent
        
        service = ChatService()
        
        response = service.ask("Pregunta de prueba")
        
        assert response.question == 'Pregunta'
        assert response.answer == 'Respuesta'


# ============================================
# PRUEBAS INTERACTIVAS (NO son tests de pytest)
# Se ejecutan solo con: python tests/test_agent.py
# ============================================

def run_agent_interactive():
    """Prueba interactiva del agente RAG con preguntas predefinidas"""
    print("\n" + "="*60)
    print("🧪 PROBANDO AGENTE RAG")
    print("="*60)
    
    print("🤖 Inicializando agente RAG...")
    agent = RAGAgent()
    
    # Verificar estado
    stats = agent.get_stats()
    print(f"\n📊 Estadísticas del agente:")
    print(f"   🤖 Modelo: {stats['model']}")
    print(f"   📚 Documentos en store: {stats['documents_in_store']}")
    print(f"    Historial: {stats['history_length']} mensajes")
    print(f"   📏 Contexto: {stats['context_window']} tokens")
    
    if stats['documents_in_store'] == 0:
        print("\n⚠️ NO HAY DOCUMENTOS EN EL VECTOR STORE.")
        print("💡 Ejecuta: python index_documents.py")
        print("   Luego selecciona opción 1: Indexar documentos")
        return
    
    # Preguntas de prueba
    questions = [
        "¿Cómo es la estructura organizacional de Santos Pegasus?",
        "¿Qué herramientas de comunicación usan en la empresa?",
        "¿Cómo se maneja un incidente crítico?",
        "¿Cuál es la arquitectura de microservicios?",
        "¿Qué tecnologías usan en el backend?"
    ]
    
    print(f"\n📝 Se harán {len(questions)} preguntas de prueba.")
    input("Presiona Enter para comenzar...")
    
    for i, question in enumerate(questions, 1):
        print(f"\n{'='*60}")
        print(f"❓ Pregunta {i}: {question}")
        print(f"{'='*60}")
        
        print("🤔 Generando respuesta...")
        result = agent.ask(question)
        
        print(f"\n🤖 RESPUESTA:")
        print("-" * 50)
        print(result['answer'])
        print("-" * 50)
        
        if result['sources']:
            print(f"\n📚 Fuentes: {', '.join(result['sources'])}")
        
        if result['context_used']:
            print(f"📄 Contexto usado: {result['context_length']} caracteres")
        else:
            print("⚠️ No se usó contexto (respuesta genérica)")
        
        if i < len(questions):
            input("\n️ Presiona Enter para la siguiente pregunta...")
    
    # Mostrar resumen de la conversación
    print(f"\n{'='*60}")
    print("📋 RESUMEN DE LA CONVERSACIÓN")
    print(f"{'='*60}")
    print(agent.get_conversation_summary())
    
    print("\n✅ Prueba completada!")


def run_chat_service_interactive():
    """Prueba interactiva del servicio de chat"""
    print("\n" + "="*60)
    print("🧪 PROBANDO SERVICIO DE CHAT")
    print("="*60)
    
    print("💬 Inicializando servicio de chat...")
    service = ChatService()
    
    # Verificar estado
    stats = service.get_stats()
    print(f"\n📊 Documentos en store: {stats['documents_in_store']}")
    
    if stats['documents_in_store'] == 0:
        print("⚠️ No hay documentos en el vector store.")
        print("💡 Ejecuta: python index_documents.py")
        return
    
    # Conversación de prueba
    questions = [
        "¿Cuántos días de vacaciones tienen los empleados?",
        "¿Qué herramientas de desarrollo usan?",
        "¿Cómo es el proceso de onboarding?"
    ]
    
    print(f"\n📝 Conversación de {len(questions)} preguntas...")
    
    for question in questions:
        print(f"\n👤 Usuario: {question}")
        response = service.ask(question)
        
        # Mostrar respuesta (primeros 200 caracteres)
        preview = response.answer[:200] + "..." if len(response.answer) > 200 else response.answer
        print(f"🤖 Asistente: {preview}")
        
        if response.sources:
            print(f"📚 Fuentes: {', '.join(response.sources[:2])}")
    
    # Mostrar historial
    history = service.get_history()
    print(f"\n📋 Historial de conversación ({len(history)} mensajes)")
    
    # Mostrar últimos 6 mensajes
    for msg in history[-6:]:
        role = " Usuario" if msg.role == "user" else "🤖 Asistente"
        preview = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
        print(f"   {role}: {preview}")
    
    print("\n✅ Prueba completada!")


def run_interactive_chat():
    """Chat interactivo con el agente"""
    print("\n" + "="*60)
    print("💬 CHAT INTERACTIVO CON EL AGENTE")
    print("="*60)
    
    print("🤖 Inicializando agente...")
    agent = RAGAgent()
    
    # Verificar estado
    stats = agent.get_stats()
    if stats['documents_in_store'] == 0:
        print("⚠️ No hay documentos en el vector store.")
        print("💡 Ejecuta: python index_documents.py")
        return
    
    print("\n✅ Agente listo! Escribe 'salir' para terminar.")
    print("📝 Ejemplos de preguntas:")
    print("   - ¿Cómo es la estructura organizacional?")
    print("   - ¿Qué herramientas usan?")
    print("   - ¿Cómo se manejan los incidentes?")
    print("\n" + "-"*60)
    
    while True:
        try:
            question = input("\n Tú: ").strip()
            
            if question.lower() in ['salir', 'exit', 'quit', 'q']:
                print("👋 ¡Hasta luego!")
                break
            
            if not question:
                continue
            
            print("🤔 Pensando...")
            result = agent.ask(question)
            
            print(f"\n🤖 Asistente: {result['answer']}")
            
            if result['sources']:
                print(f"\n📚 Fuentes: {', '.join(result['sources'][:3])}")
            
        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


def main():
    """Función principal con menú interactivo"""
    
    print("\n" + "="*60)
    print("🧪 SISTEMA DE PRUEBAS - SANTOS PEGASUS RAG AGENT")
    print("="*60)
    
    print("\n📋 OPCIONES:")
    print("   1. Probar agente RAG (preguntas predefinidas)")
    print("   2. Probar servicio de chat")
    print("   3. Chat interactivo (escribe tus preguntas)")
    print("   4. Probar todo")
    print("   5. Salir")
    
    option = input("\n👉 Selecciona una opción (1-5): ").strip()
    
    if option == "1":
        run_agent_interactive()
    elif option == "2":
        run_chat_service_interactive()
    elif option == "3":
        run_interactive_chat()
    elif option == "4":
        run_agent_interactive()
        print("\n" + "="*60 + "\n")
        run_chat_service_interactive()
        print("\n" + "="*60 + "\n")
        run_interactive_chat()
    elif option == "5":
        print("👋 ¡Hasta luego!")
        sys.exit(0)
    else:
        print("❌ Opción no válida")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Prueba interrumpida por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)