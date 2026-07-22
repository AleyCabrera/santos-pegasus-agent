#!/usr/bin/env python
"""
Script de prueba para verificar la ingesta de documentos
"""
import sys
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_ingestion():
    """Prueba el pipeline de ingesta"""
    print("🧪 Probando pipeline de ingesta...\n")
    
    # Verificar que existan documentos
    docs_dir = Path("data/documentos")
    pdf_files = list(docs_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("❌ No se encontraron PDFs en data/documentos/")
        print("👉 Ejecuta: python generate_sample_docs.py primero")
        return False
    
    print(f"📄 Encontrados {len(pdf_files)} PDFs:")
    for pdf in pdf_files:
        print(f"   - {pdf.name} ({pdf.stat().st_size} bytes)")
    
    # Probar ingesta
    try:
        from src.ingest import process_documents
        chunks = process_documents()
        
        if chunks:
            print(f"\n✅ Éxito: {len(chunks)} chunks generados")
            
            # Mostrar estadísticas
            sources = {}
            for chunk in chunks:
                src = chunk["source"]
                sources[src] = sources.get(src, 0) + 1
            
            print("\n📊 Distribución por documento:")
            for src, count in sources.items():
                print(f"   - {src}: {count} chunks")
            
            # Mostrar ejemplo
            print("\n📝 Ejemplo del primer chunk:")
            first_chunk = chunks[0]
            print(f"Fuente: {first_chunk['source']}")
            print(f"ID: {first_chunk['chunk_id']}")
            print(f"Contenido: {first_chunk['content'][:150]}...")
            
            return True
        else:
            print("❌ No se generaron chunks")
            return False
            
    except Exception as e:
        print(f"❌ Error en la ingesta: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_ingestion()
    sys.exit(0 if success else 1)