#!/usr/bin/env python
"""
Script para inicializar el agente en producción
Se ejecuta automáticamente en Streamlit Cloud
"""
import logging
import sys
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_production():
    """Prepara el agente para producción"""
    logger.info("🚀 Configurando agente para producción...")
    
    # Verificar documentos
    docs_dir = Path("data/documentos")
    pdf_files = list(docs_dir.glob("*.pdf"))
    
    if not pdf_files:
        logger.warning("⚠️ No se encontraron documentos. Generando ejemplos...")
        try:
            # Intentar generar documentos de ejemplo
            from generate_sample_docs import create_sample_documents
            create_sample_documents()
            pdf_files = list(docs_dir.glob("*.pdf"))
        except Exception as e:
            logger.error(f"❌ Error al generar documentos: {e}")
            return False
    
    logger.info(f"📄 Encontrados {len(pdf_files)} documentos")
    
    # Procesar documentos y crear vector store
    try:
        from src.ingest import process_documents
        from src.vectorstore import create_vector_store
        
        chunks = process_documents()
        if not chunks:
            logger.error("❌ No se generaron chunks")
            return False
        
        vector_store = create_vector_store(chunks, force_rebuild=True)
        if vector_store is None:
            logger.error("❌ No se pudo crear el vector store")
            return False
        
        logger.info("✅ Vector store creado exitosamente")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en la configuración: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = setup_production()
    sys.exit(0 if success else 1)