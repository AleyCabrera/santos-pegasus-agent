"""Script para indexar documentos en el vector store"""
import sys
from pathlib import Path
from app.services.indexing_service import IndexingService
from app.utils.logger import logger

def main():
    """Función principal de indexación"""
    logger.info("="*60)
    logger.info("📚 SISTEMA DE INDEXACIÓN - Santos Pegasus Soluciones")
    logger.info("="*60)
    
    # Crear servicio de indexación
    indexer = IndexingService()
    
    # Opciones de indexación
    print("\n📋 Opciones:")
    print("1. Indexar documentos (nuevos)")
    print("2. Re-indexar (limpiar y volver a indexar)")
    print("3. Ver estadísticas")
    print("4. Salir")
    
    option = input("\nSelecciona una opción (1-4): ").strip()
    
    if option == "1":
        logger.info("🚀 Indexando documentos...")
        result = indexer.index_directories()
        
        print("\n📊 RESULTADOS:")
        print(f"   📄 Documentos procesados: {result.get('documents_processed', 0)}")
        print(f"   📝 Chunks generados: {result.get('chunks_generated', 0)}")
        print(f"   🧠 Embeddings generados: {result.get('embeddings_generated', 0)}")
        print(f"   💾 Total agregado: {result.get('total_added', 0)}")
        
        if 'vector_stats' in result:
            stats = result['vector_stats']
            print(f"\n🗄️ Estadísticas del Vector Store:")
            print(f"   📚 Documentos totales: {stats.get('total_documents', 0)}")
            print(f"   📏 Dimensión: {stats.get('embedding_dim', 0)}")
    
    elif option == "2":
        logger.info("🔄 Re-indexando todos los documentos...")
        result = indexer.reindex()
        
        print("\n📊 RESULTADOS DE RE-INDEXACIÓN:")
        print(f"   📄 Documentos procesados: {result.get('documents_processed', 0)}")
        print(f"   📝 Chunks generados: {result.get('chunks_generated', 0)}")
        print(f"   💾 Total agregado: {result.get('total_added', 0)}")
    
    elif option == "3":
        # Ver estadísticas
        stats = indexer.vector_store.get_statistics()
        embedding_stats = indexer.embedding_manager.get_cache_stats()
        
        print("\n📊 ESTADÍSTICAS:")
        print(f"\n🗄️ Vector Store:")
        print(f"   📚 Documentos totales: {stats.get('total_documents', 0)}")
        print(f"   📏 Dimensión: {stats.get('embedding_dim', 0)}")
        print(f"   📂 Path: {stats.get('store_path', 'N/A')}")
        
        print(f"\n🧠 Embeddings:")
        print(f"   🔢 Dimensión: {embedding_stats.get('embedding_dim', 0)}")
        print(f"   💾 Tamaño cache: {embedding_stats.get('cache_size', 0)}")
        print(f"   🎯 Hit rate: {embedding_stats.get('hit_rate', '0%')}")
    
    elif option == "4":
        logger.info("👋 Saliendo...")
        sys.exit(0)
    
    else:
        logger.error("❌ Opción no válida")

if __name__ == "__main__":
    main()