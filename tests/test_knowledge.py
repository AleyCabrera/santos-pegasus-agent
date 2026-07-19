"""Script para probar el conocimiento de la documentación (Automatizado para pytest)"""
import sys
from pathlib import Path

# AGREGAR LA RAÍZ DEL PROYECTO AL PATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.agents.rag_agent import RAGAgent
from app.services.chat_service import ChatService


def test_knowledge():
    """Prueba preguntas específicas sobre la documentación de forma automática"""
    
    print("\n🧪 PROBANDO CONOCIMIENTO DE LA DOCUMENTACIÓN (Modo Automático)")
    print("="*60)
    
    # Crear agente
    try:
        agent = RAGAgent()
    except Exception as e:
        print(f"❌ Error inicializando el agente: {e}")
        print("💡 Verifica que Ollama esté corriendo: ollama serve")
        return
    
    stats = agent.get_stats()
    
    print(f"\n📊 Estado del agente:")
    print(f"   📚 Documentos en store: {stats['documents_in_store']}")
    print(f"   🤖 Modelo: {stats['model']}")
    
    if stats['documents_in_store'] == 0:
        print("\n⚠️ No hay documentos indexados.")
        print("💡 Ejecuta: python index_auto.py")
        return
    
    # Preguntas sobre cada documento (Ejecutamos solo 3 para que el test sea rápido)
    questions = [
        "¿Cuáles son los valores de Santo Pegasus?",
        "¿Qué principios SOLID aplican en el back-end?",
        "¿Qué es un incidente SEV-1?"
    ]
    
    print(f"\n📝 Ejecutando {len(questions)} preguntas de prueba automáticas...\n")
    
    for i, question in enumerate(questions, 1):
        print(f"❓ Pregunta {i}: {question}")
        try:
            result = agent.ask(question)
            
            # Verificación básica: que haya respuesta y no sea un error
            assert 'answer' in result, "La respuesta no contiene la clave 'answer'"
            assert len(result['answer']) > 10, "La respuesta es demasiado corta"
            
            print(f"   ✅ Respuesta generada ({len(result['answer'])} caracteres)")
            
            if result['sources']:
                print(f"   📚 Fuentes: {', '.join(result['sources'])}")
            
        except Exception as e:
            print(f"   ❌ Error generando respuesta: {e}")
            raise  # Esto hará que pytest marque el test como fallido si hay un error real
            
    print("\n" + "="*60)
    print("✅ ¡Prueba de conocimiento completada exitosamente!")
    print("="*60 + "\n")


if __name__ == "__main__":
    try:
        test_knowledge()
    except KeyboardInterrupt:
        print("\n\n⚠️ Prueba interrumpida por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()