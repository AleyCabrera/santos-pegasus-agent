"""
Módulo de ingesta de documentos
Carga, procesa y trocea documentos para el pipeline RAG
"""
import logging
from pathlib import Path
from typing import List, Dict, Any

from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from src.config import DOCUMENTS_DIR, CHUNK_SIZE, CHUNK_OVERLAP

logger = logging.getLogger(__name__)


def load_documents() -> List[Dict[str, Any]]:
    """
    Carga todos los documentos PDF del directorio configurado.
    """
    documents = []
    pdf_files = list(DOCUMENTS_DIR.glob("*.pdf"))
    
    if not pdf_files:
        logger.warning(f"No se encontraron PDFs en {DOCUMENTS_DIR}")
        return documents
    
    logger.info(f"📄 Encontrados {len(pdf_files)} PDFs para procesar")
    
    for pdf_path in pdf_files:
        try:
            logger.info(f"📖 Procesando: {pdf_path.name}")
            reader = PdfReader(pdf_path)
            
            full_text = ""
            total_pages = len(reader.pages)
            
            for page_num, page in enumerate(reader.pages, 1):
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
            
            if full_text.strip():
                documents.append({
                    "content": full_text.strip(),
                    "source": pdf_path.name,
                    "metadata": {
                        "filename": pdf_path.name,
                        "pages": total_pages,
                        "size_bytes": pdf_path.stat().st_size,
                        "characters": len(full_text)
                    }
                })
                logger.info(f"✅ {pdf_path.name}: {len(full_text)} caracteres, {total_pages} páginas")
            else:
                logger.warning(f"⚠️ {pdf_path.name}: sin texto extraíble")
                
        except Exception as e:
            logger.error(f"❌ Error al procesar {pdf_path.name}: {e}")
    
    logger.info(f"✅ Cargados {len(documents)} documentos exitosamente")
    return documents


def chunk_documents(documents: List[Dict[str, Any]], 
                   chunk_size: int = None, 
                   chunk_overlap: int = None) -> List[Dict[str, Any]]:
    """
    Trocea documentos en chunks para embeddings.
    """
    chunk_size = chunk_size or CHUNK_SIZE
    chunk_overlap = chunk_overlap or CHUNK_OVERLAP
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
        keep_separator=False
    )
    
    all_chunks = []
    
    for doc in documents:
        content = doc["content"]
        source = doc["source"]
        metadata = doc.get("metadata", {})
        
        chunks = text_splitter.split_text(content)
        
        for i, chunk_text in enumerate(chunks):
            if chunk_text.strip():
                all_chunks.append({
                    "content": chunk_text.strip(),
                    "source": source,
                    "chunk_id": f"{source}_{i+1}",
                    "metadata": {
                        **metadata,
                        "chunk_index": i + 1,
                        "total_chunks": len(chunks)
                    }
                })
        
        logger.info(f"📝 {source}: {len(chunks)} chunks generados")
    
    logger.info(f"✅ Total de chunks generados: {len(all_chunks)}")
    return all_chunks


def process_documents() -> List[Dict[str, Any]]:
    """
    Pipeline completo de procesamiento: carga + chunking
    """
    logger.info("🚀 Iniciando pipeline de ingesta de documentos")
    
    documents = load_documents()
    if not documents:
        logger.error("❌ No se cargaron documentos para procesar")
        return []
    
    chunks = chunk_documents(documents)
    
    if chunks:
        logger.info(f"✅ Pipeline completado: {len(chunks)} chunks generados")
    else:
        logger.warning("⚠️ No se generaron chunks de los documentos")
    
    return chunks