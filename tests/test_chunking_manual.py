# tests/test_chunking_manual.py
"""Script para probar el chunking manualmente"""

from pathlib import Path
from app.utils.text_processor import DocumentProcessor
from app.loaders import PDFLoader, CSVLoader
from app.utils.logger import logger


def test_chunking():
    """Prueba manual del sistema de chunking"""
    
    logger.info("=" * 60)
    logger.info("🚀 Probando sistema de chunking...")
    logger.info("=" * 60)
    
    # Crear procesador - CORREGIDO
    processor = DocumentProcessor(chunk_size=300, overlap=50)
    
    # Cargar documentos
    documents = []
    
    # Cargar PDFs si existen
    pdf_dir = Path("data/pdfs")
    if pdf_dir.exists():
        pdf_files = list(pdf_dir.glob("*.pdf"))
        if pdf_files:
            logger.info(f"\n📄 Cargando {len(pdf_files)} PDFs...")
            for pdf_path in pdf_files:
                try:
                    logger.info(f"   📄 {pdf_path.name}")
                    loader = PDFLoader(pdf_path)
                    docs = loader.load()
                    documents.extend(docs)
                    logger.info(f"   ✅ {len(docs)} páginas cargadas")
                except Exception as e:
                    logger.error(f"   ❌ Error cargando {pdf_path.name}: {e}")
        else:
            logger.warning("⚠️ No hay PDFs en data/pdfs/")
    
    # Cargar CSVs si existen
    csv_dir = Path("data/csv")
    if csv_dir.exists():
        csv_files = list(csv_dir.glob("*.csv"))
        if csv_files:
            logger.info(f"\n📊 Cargando {len(csv_files)} CSVs...")
            for csv_path in csv_files:
                try:
                    logger.info(f"   📊 {csv_path.name}")
                    loader = CSVLoader(csv_path)
                    docs = loader.load()
                    documents.extend(docs)
                    logger.info(f"   ✅ {len(docs)} filas cargadas")
                except Exception as e:
                    logger.error(f"   ❌ Error cargando {csv_path.name}: {e}")
        else:
            logger.warning("⚠️ No hay CSVs en data/csv/")
    
    if not documents:
        logger.warning("\n⚠️ No se encontraron documentos para procesar")
        logger.info("💡 Crea documentos en data/pdfs/ o data/csv/")
        return
    
    logger.info(f"\n📄 Total documentos cargados: {len(documents)}")
    
    # Mostrar estadísticas básicas
    total_chars = sum(len(doc.get("page_content", "")) for doc in documents)
    logger.info(f"📊 Total caracteres: {total_chars:,}")
    logger.info(f"📊 Promedio por documento: {total_chars / len(documents):.0f} caracteres")
    
    # Probar diferentes estrategias
    strategies = ['recursive', 'sentence', 'character', 'overlap']
    
    results = {}
    
    for strategy in strategies:
        try:
            logger.info(f"\n{'='*40}")
            logger.info(f"🔧 Probando estrategia: {strategy.upper()}")
            logger.info(f"{'='*40}")
            
            # Procesar documentos con la estrategia
            chunks = processor.process_documents(documents, strategy=strategy)
            
            # Obtener estadísticas
            stats = processor.get_statistics(chunks)
            
            # Guardar resultados
            results[strategy] = {
                "num_chunks": stats['total_chunks'],
                "avg_size": stats['avg_chunk_size'],
                "min_size": stats['min_chunk_size'],
                "max_size": stats['max_chunk_size']
            }
            
            logger.info(f"   📊 Chunks generados: {stats['total_chunks']}")
            logger.info(f"   📏 Tamaño promedio: {stats['avg_chunk_size']:.0f} caracteres")
            logger.info(f"   📐 Rango: {stats['min_chunk_size']} - {stats['max_chunk_size']} caracteres")
            
            # Mostrar un ejemplo de chunk
            if chunks:
                sample_chunk = chunks[0]
                content = sample_chunk.get('page_content', '')
                logger.info(f"\n   📝 Ejemplo de chunk:")
                logger.info(f"   {'-'*40}")
                preview = content[:200] + "..." if len(content) > 200 else content
                logger.info(f"   {preview}")
                logger.info(f"   {'-'*40}")
                if sample_chunk.get('metadata'):
                    logger.info(f"   📌 Metadata: {sample_chunk['metadata']}")
                    
        except Exception as e:
            logger.error(f"   ❌ Error con estrategia {strategy}: {e}")
    
    # Comparar estrategias
    if results:
        logger.info(f"\n{'='*60}")
        logger.info("📊 COMPARACIÓN DE ESTRATEGIAS")
        logger.info(f"{'='*60}")
        logger.info(f"{'Estrategia':<12} {'Chunks':<10} {'Promedio':<12} {'Rango':<20}")
        logger.info(f"{'-'*60}")
        
        for strategy, data in results.items():
            logger.info(f"{strategy:<12} {data['num_chunks']:<10} {data['avg_size']:<12.0f} {data['min_size']}-{data['max_size']}")
    
    logger.info("\n✅ Prueba completada!")


if __name__ == "__main__":
    try:
        test_chunking()
    except KeyboardInterrupt:
        print("\n\n⚠️ Prueba interrumpida por el usuario")
    except Exception as e:
        logger.error(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()