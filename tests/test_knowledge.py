"""Script para probar el conocimiento de la documentación"""
import sys
from pathlib import Path

# AGREGAR LA RAÍZ DEL PROYECTO AL PATH
# Esto permite que Python encuentre el módulo 'app'
sys.path.insert(0, str(Path(__file__).parent.parent))

# Ahora sí podemos importar los módulos del proyecto
from app.agents.rag_agent import RAGAgent
from app.services.chat_service import ChatService


def test_knowledge():
    """Prueba preguntas específicas sobre la documentación"""
    
    print("🧪 PROBANDO CONOCIMIENTO DE LA DOCUMENTACIÓN")
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
        print("💡 Ejecuta: python index_documents.py")
        print("   Luego selecciona opción 1: Indexar documentos")
        return
    
    # Preguntas sobre cada documento
    questions = [
        # Manual de Onboarding
        "¿Cuáles son los valores de Santo Pegasus?",
        "¿Cómo es la estructura organizacional?",
        "¿Qué herramientas de comunicación usan?",
        "¿Cuántos días de vacaciones tienen los empleados?",
        
        # Guía Back-end
        "¿Qué principios SOLID aplican en el back-end?",
        "¿Cómo se manejan las credenciales en el código?",
        "¿Qué framework usan para pruebas unitarias?",
        "¿Cuál es la cobertura mínima de pruebas?",
        
        # Guía Front-end
        "¿Qué stack tecnológico usan en front-end?",
        "¿Cómo gestionan el estado global?",
        "¿Qué es Atomic Design?",
        "¿Cómo manejan la seguridad en front-end?",
        
        # Protocolo de Incidentes
        "¿Qué es un incidente SEV-1?",
        "¿Cómo se gestiona un incidente crítico?",
        "¿Qué es el Error Budget?",
        "¿Qué es un Post-Mortem?",
        
        # Arquitectura de Microservicios
        "¿Cuáles son los microservicios principales?",
        "¿Cómo se comunican los servicios?",
        "¿Qué bases de datos usan?",
        "¿Qué es el API Gateway?"
    ]
    
    print(f"\n📝 Se harán {len(questions)} preguntas de prueba.")
    print("   (Se ejecutarán las primeras 5 para no saturar)")
    input("\nPresiona Enter para comenzar...")
    
    for i, question in enumerate(questions[:5], 1):  # Solo 5 para no saturar
        print(f"\n{'='*60}")
        print(f"❓ Pregunta {i}: {question}")
        print(f"{'='*60}")
        
        print("🤔 Generando respuesta...")
        try:
            result = agent.ask(question)
            
            print(f"\n RESPUESTA:")
            print("-" * 50)
            print(result['answer'])
            print("-" * 50)
            
            if result['sources']:
                print(f"\n📚 Fuentes: {', '.join(result['sources'])}")
            
            if result['context_used']:
                print(f"📄 Contexto usado: {result['context_length']} caracteres")
            else:
                print("⚠️ No se usó contexto")
        except Exception as e:
            print(f"\n❌ Error generando respuesta: {e}")
        
        if i < 5:
            input("\n⏭️ Presiona Enter para continuar...")
    
    print("\n✅ Prueba completada!")


if __name__ == "__main__":
    try:
        test_knowledge()
    except KeyboardInterrupt:
        print("\n\n⚠️ Prueba interrumpida por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()