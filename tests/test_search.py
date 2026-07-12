# Crear archivo test_search.py
from app.vector_store.faiss_store import FAISSVectorStore
from app.embeddings.embedding_manager import EmbeddingManager
from app.utils.logger import logger

print("🔍 Probando búsqueda en Vector Store...")

# Cargar embedding manager y vector store
emb_manager = EmbeddingManager()
store = FAISSVectorStore(emb_manager)

# Cargar vector store existente
if store.load():
    print(f"✅ Vector store cargado: {store.index.ntotal} documentos")
    
    # Probar búsqueda
    queries = [
        "¿Cómo se manejan los incidentes críticos?",
        "¿Cuál es la estructura organizacional?",
        "¿Qué herramientas de comunicación usan?"
    ]
    
    for query in queries:
        print(f"\n📝 Pregunta: {query}")
        results = store.search(query, k=2)
        
        if results:
            for r in results:
                print(f"   📊 Score: {r['similarity']:.3f}")
                print(f"   📄 Texto: {r['content'][:100]}...")
                print(f"   📌 Fuente: {r['metadata'].get('filename', 'Desconocida')}")
        else:
            print("   ❌ No se encontraron resultados")
else:
    print("❌ No se encontró vector store. Indexa documentos primero.")