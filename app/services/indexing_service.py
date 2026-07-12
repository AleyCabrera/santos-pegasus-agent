"""Servicio de indexación para el pipeline RAG"""
from pathlib import Path
from typing import List, Dict, Any, Optional
from app.loaders import PDFLoader, CSVLoader
from app.utils.text_processor import DocumentProcessor
from app.embeddings.embedding_manager import EmbeddingManager
from app.vector_store.faiss_store import FAISSVectorStore
from app.config import settings
from app.utils.logger import logger


class IndexingService:
    """
    Servicio que coordina todo el pipeline de indexación:
    1. Carga de documentos
    2. Chunking
    3. Generación de embeddings
    4. Almacenamiento en vector store
    """
    
    def __init__(
        self,
        document_processor: Optional[DocumentProcessor] = None,
        embedding_manager: Optional[EmbeddingManager] = None,
        vector_store: Optional[FAISSVectorStore] = None
    ):
        """
        Inicializa el servicio de indexación
        """
        self.document_processor = document_processor or DocumentProcessor()
        self.embedding_manager = embedding_manager or EmbeddingManager()
        self.vector_store = vector_store or FAISSVectorStore(self.embedding_manager)
        self.logger = logger
        
        # Inicializar vector store
        if not self.vector_store.is_loaded:
            embedding_dim = self.embedding_manager.model.get_sentence_embedding_dimension()
            self.vector_store.create_index(embedding_dim)
    
    def _load_text_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Carga un archivo de texto plano
        
        Args:
            file_path: Ruta al archivo .txt
        
        Returns:
            Lista con el contenido del archivo
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return [{
                'page_content': content,  # CORREGIDO: Usar 'page_content'
                'metadata': {
                    'source': str(file_path),
                    'filename': file_path.name,
                    'type': 'txt',
                    'file_size': file_path.stat().st_size
                }
            }]
        except Exception as e:
            self.logger.error(f"Error cargando archivo de texto {file_path.name}: {e}")
            return []
    
    def index_directories(
        self,
        pdf_dir: Optional[Path] = None,
        csv_dir: Optional[Path] = None,
        txt_dir: Optional[Path] = None,
        chunk_strategy: str = 'recursive'
    ) -> Dict[str, Any]:
        """
        Indexa todos los documentos en directorios
        
        Args:
            pdf_dir: Directorio de PDFs
            csv_dir: Directorio de CSVs
            txt_dir: Directorio de archivos de texto
            chunk_strategy: Estrategia de chunking
        
        Returns:
            Estadísticas del proceso
        """
        pdf_dir = pdf_dir or settings.PDFS_PATH
        csv_dir = csv_dir or settings.CSV_PATH
        txt_dir = txt_dir or settings.PDFS_PATH  # Usar mismo directorio
        
        self.logger.info(f"📂 Indexando documentos desde directorios")
        self.logger.info(f"   PDFs: {pdf_dir}")
        self.logger.info(f"   CSVs: {csv_dir}")
        self.logger.info(f"   TXTs: {txt_dir}")
        
        documents = []
        
        # Cargar PDFs
        if pdf_dir and pdf_dir.exists():
            pdf_files = list(pdf_dir.glob("*.pdf"))
            self.logger.info(f"📄 Encontrados {len(pdf_files)} PDFs")
            
            for pdf_path in pdf_files:
                try:
                    loader = PDFLoader(pdf_path)
                    docs = loader.load()
                    documents.extend(docs)
                    self.logger.info(f"   ✅ {pdf_path.name}: {len(docs)} páginas")
                except Exception as e:
                    self.logger.error(f"   ❌ Error cargando {pdf_path.name}: {e}")
        
        # Cargar archivos de texto (.txt)
        if txt_dir and txt_dir.exists():
            txt_files = list(txt_dir.glob("*.txt"))
            self.logger.info(f"📝 Encontrados {len(txt_files)} archivos de texto")
            
            for txt_path in txt_files:
                try:
                    docs = self._load_text_file(txt_path)
                    documents.extend(docs)
                    self.logger.info(f"   ✅ {txt_path.name}: {len(docs)} documentos")
                except Exception as e:
                    self.logger.error(f"   ❌ Error cargando {txt_path.name}: {e}")
        
        # Cargar CSVs
        if csv_dir and csv_dir.exists():
            csv_files = list(csv_dir.glob("*.csv"))
            self.logger.info(f"📊 Encontrados {len(csv_files)} CSVs")
            
            for csv_path in csv_files:
                try:
                    loader = CSVLoader(csv_path)
                    docs = loader.load()
                    documents.extend(docs)
                    self.logger.info(f"   ✅ {csv_path.name}: {len(docs)} filas")
                except Exception as e:
                    self.logger.error(f"   ❌ Error cargando {csv_path.name}: {e}")
        
        if not documents:
            self.logger.warning("⚠️ No se encontraron documentos para indexar")
            return {'documents_processed': 0}
        
        self.logger.info(f"📄 Total documentos cargados: {len(documents)}")
        
        return self.index_documents(documents, chunk_strategy)
    
    def index_documents(
        self,
        documents: List[Dict[str, Any]],
        chunk_strategy: str = 'recursive'
    ) -> Dict[str, Any]:
        """
        Procesa documentos, genera embeddings y los almacena en el vector store
        
        Args:
            documents: Lista de documentos con 'content' o 'page_content' y 'metadata'
            chunk_strategy: Estrategia de chunking ('recursive', 'character', 'sentence', 'overlap')
        
        Returns:
            Diccionario con estadísticas del proceso
        """
        self.logger.info(f"🔧 Procesando {len(documents)} documentos con estrategia: {chunk_strategy}")
        
        try:
            # 1. Procesar documentos (chunking)
            self.logger.info("📝 Aplicando chunking a los documentos...")
            chunks = self.document_processor.process_documents(
                documents, 
                strategy=chunk_strategy
            )
            
            self.logger.info(f"✅ Generados {len(chunks)} chunks")
            
            if not chunks:
                self.logger.warning("⚠️ No se generaron chunks. Verifica el contenido de los documentos.")
                return {
                    'documents_processed': len(documents),
                    'chunks_generated': 0,
                    'embeddings_generated': 0,
                    'total_added': 0,
                    'strategy': chunk_strategy
                }
            
            # Obtener estadísticas de chunking
            chunk_stats = self.document_processor.get_statistics(chunks)
            self.logger.info(f"   📏 Tamaño promedio: {chunk_stats['avg_chunk_size']:.0f} caracteres")
            self.logger.info(f"   📐 Rango: {chunk_stats['min_chunk_size']} - {chunk_stats['max_chunk_size']} caracteres")
            
            # 2. Extraer textos de los chunks
            texts = [chunk['page_content'] for chunk in chunks]
            metadatas = [chunk['metadata'] for chunk in chunks]
            
            # 3. Generar embeddings
            self.logger.info("🧠 Generando embeddings...")
            embeddings = self.embedding_manager.get_embeddings(texts, batch_size=32)
            
            self.logger.info(f"✅ Generados {len(embeddings)} embeddings")
            self.logger.info(f"   📏 Dimensión: {len(embeddings[0]) if embeddings else 0}")
            
            # 4. Preparar documentos para el vector store
            documents_for_store = []
            for i, (text, metadata, embedding) in enumerate(zip(texts, metadatas, embeddings)):
                documents_for_store.append({
                    'content': text,
                    'metadata': metadata,
                    'embedding': embedding
                })
            
            # 5. Agregar al vector store
            self.logger.info("💾 Agregando documentos al vector store...")
            total_added = self.vector_store.add_documents(documents_for_store, embeddings=embeddings)
            
            self.logger.info(f"✅ Agregados {total_added} documentos al vector store")
            
            # 6. Guardar vector store en disco
            self.logger.info("💾 Guardando vector store en disco...")
            self.vector_store.save()
            
            # 7. Obtener estadísticas finales
            vector_stats = self.vector_store.get_statistics()
            embedding_stats = self.embedding_manager.get_cache_stats()
            
            result = {
                'documents_processed': len(documents),
                'chunks_generated': len(chunks),
                'embeddings_generated': len(embeddings),
                'total_added': total_added,
                'chunk_stats': chunk_stats,
                'vector_stats': vector_stats,
                'embedding_stats': embedding_stats,
                'strategy': chunk_strategy
            }
            
            self.logger.info("🎉 Indexación completada exitosamente")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error durante la indexación: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            raise
    
    def reindex(
        self,
        pdf_dir: Optional[Path] = None,
        csv_dir: Optional[Path] = None,
        txt_dir: Optional[Path] = None,
        chunk_strategy: str = 'recursive'
    ) -> Dict[str, Any]:
        """
        Limpia el vector store y vuelve a indexar todos los documentos
        
        Args:
            pdf_dir: Directorio de PDFs
            csv_dir: Directorio de CSVs
            txt_dir: Directorio de archivos de texto
            chunk_strategy: Estrategia de chunking
        
        Returns:
            Estadísticas del proceso
        """
        self.logger.info("🔄 Iniciando re-indexación completa...")
        
        try:
            # 1. Limpiar vector store actual
            self.logger.info("🧹 Limpiando vector store...")
            self.vector_store.clear()
            
            # 2. Crear nuevo índice
            embedding_dim = self.embedding_manager.model.get_sentence_embedding_dimension()
            self.vector_store.create_index(embedding_dim)
            
            self.logger.info("✅ Vector store limpiado y recreado")
            
            # 3. Indexar documentos nuevamente
            return self.index_directories(
                pdf_dir=pdf_dir,
                csv_dir=csv_dir,
                txt_dir=txt_dir,
                chunk_strategy=chunk_strategy
            )
            
        except Exception as e:
            self.logger.error(f"❌ Error durante la re-indexación: {e}")
            raise