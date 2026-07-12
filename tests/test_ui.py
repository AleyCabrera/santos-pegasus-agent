"""Script rápido para probar la UI sin Streamlit"""

from app.services.chat_service import ChatService

print("🧪 Probando servicio de chat para UI...")

try:
    service = ChatService()
    stats = service.get_stats()
    
    print(f"✅ Servicio de chat inicializado")
    print(f"   📚 Documentos en store: {stats.get('documents_in_store', 0)}")
    print(f"   🤖 Modelo: {stats.get('model', 'N/A')}")
    
    if stats.get('documents_in_store', 0) == 0:
        print("⚠️ No hay documentos indexados. Ejecuta: python index_documents.py")
    else:
        # Probar pregunta
        response = service.ask("¿Qué es Santos Pegasus Soluciones?")
        print(f"\n📝 Pregunta de prueba:")
        print(f"   👤: ¿Qué es Santos Pegasus Soluciones?")
        print(f"   🤖: {response.answer[:150]}...")
        print(f"   📚 Fuentes: {response.sources}")
        
except Exception as e:
    print(f"❌ Error: {e}")