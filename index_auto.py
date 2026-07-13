"""Script de indexación automática para Docker - sin interacción"""
import sys
from pathlib import Path
from app.services.indexing_service import IndexingService
from app.utils.logger import logger

def main():
    """Función principal de indexación automática"""
    logger.info("="*60)
    logger.info("📚 INDEXACIÓN AUTOMÁTICA - Santos Pegasus Soluciones")
    logger.info("="*60)
    
    try:
        # Crear servicio de indexación
        indexer = IndexingService()
        
        # Intentar cargar vector store existente
        if indexer.vector_store.is_loaded and indexer.vector_store.index.ntotal > 0:
            logger.info(f"✅ Vector store existente encontrado: {indexer.vector_store.index.ntotal} documentos")
            logger.info("💡 Para re-indexar, elimina el volumen Docker o ejecuta manualmente")
            return
        
        # Indexar documentos automáticamente
        logger.info("🚀 Indexando documentos automáticamente...")
        result = indexer.index_directories()
        
        # Mostrar resultados
        logger.info("="*60)
        logger.info("📊 RESULTADOS DE INDEXACIÓN:")
        logger.info(f"   📄 Documentos procesados: {result.get('documents_processed', 0)}")
        logger.info(f"   📝 Chunks generados: {result.get('chunks_generated', 0)}")
        logger.info(f"   🧠 Embeddings generados: {result.get('embeddings_generated', 0)}")
        logger.info(f"   💾 Total agregado: {result.get('total_added', 0)}")
        
        if 'vector_stats' in result:
            stats = result['vector_stats']
            logger.info(f"   🗄️ Documentos en Vector Store: {stats.get('total_documents', 0)}")
        
        logger.info("="*60)
        logger.info("✅ Indexación completada exitosamente")
        
    except Exception as e:
        logger.error(f"❌ Error durante la indexación: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()