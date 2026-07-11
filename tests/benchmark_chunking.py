"""Benchmark de estrategias de chunking"""

import time
from pathlib import Path
from typing import List, Dict, Any
from app.utils.text_processor import DocumentProcessor
from app.loaders import PDFLoader, CSVLoader
from app.utils.logger import logger


class ChunkingBenchmark:
    """Benchmark para comparar estrategias de chunking"""
    
    def __init__(self):
        self.processor = DocumentProcessor(
            chunk_size=500,
            chunk_overlap=50
        )
        self.results = []
    
    def load_documents(self) -> List[Dict[str, Any]]:
        """Carga documentos de prueba"""
        documents = []
        
        # Cargar PDFs
        pdf_dir = Path("data/pdfs")
        if pdf_dir.exists():
            for pdf_path in pdf_dir.glob("*.pdf"):
                loader = PDFLoader(pdf_path)
                docs = loader.load()
                documents.extend(docs)
                logger.info(f"Cargado PDF: {pdf_path.name}")
        
        # Cargar CSVs
        csv_dir = Path("data/csv")
        if csv_dir.exists():
            for csv_path in csv_dir.glob("*.csv"):
                loader = CSVLoader(csv_path)
                docs = loader.load()
                documents.extend(docs)
                logger.info(f"Cargado CSV: {csv_path.name}")
        
        return documents
    
    def benchmark_strategy(self, documents: List[Dict[str, Any]], strategy: str) -> Dict[str, Any]:
        """
        Ejecuta benchmark para una estrategia específica
        
        Args:
            documents: Documentos a procesar
            strategy: Estrategia de chunking
            
        Returns:
            Resultados del benchmark
        """
        start_time = time.time()
        
        chunks = self.processor.process_documents(documents, strategy=strategy)
        
        elapsed_time = time.time() - start_time
        
        stats = self.processor.get_statistics(chunks)
        stats['elapsed_time'] = elapsed_time
        stats['strategy'] = strategy
        stats['chunks_per_second'] = len(chunks) / elapsed_time if elapsed_time > 0 else 0
        
        return stats
    
    def run_all_benchmarks(self):
        """Ejecuta benchmarks para todas las estrategias"""
        logger.info("🚀 Iniciando benchmark de chunking...")
        
        # Cargar documentos
        documents = self.load_documents()
        
        if not documents:
            logger.warning("⚠️ No hay documentos para benchmark")
            return
        
        logger.info(f"📄 Documentos cargados: {len(documents)}")
        
        # Estrategias a probar
        strategies = ['recursive', 'character', 'sentence', 'paragraph']
        
        for strategy in strategies:
            logger.info(f"\n📊 Probando estrategia: {strategy}")
            result = self.benchmark_strategy(documents, strategy)
            self.results.append(result)
            
            # Mostrar resultados
            logger.info(f"   ✅ Chunks generados: {result['total_chunks']}")
            logger.info(f"   ⏱️  Tiempo: {result['elapsed_time']:.2f}s")
            logger.info(f"   📏 Tamaño promedio: {result['average_size']:.0f} caracteres")
            logger.info(f"   🚀 Velocidad: {result['chunks_per_second']:.1f} chunks/s")
    
    def print_summary(self):
        """Imprime resumen de resultados"""
        if not self.results:
            logger.warning("No hay resultados para mostrar")
            return
        
        logger.info("\n" + "="*60)
        logger.info("📊 RESUMEN DE BENCHMARK")
        logger.info("="*60)
        
        # Encontrar la mejor estrategia
        fastest = min(self.results, key=lambda x: x['elapsed_time'])
        most_chunks = max(self.results, key=lambda x: x['total_chunks'])
        
        logger.info(f"\n🏆 Estrategia más rápida: {fastest['strategy']} ({fastest['elapsed_time']:.2f}s)")
        logger.info(f"📈 Estrategia con más chunks: {most_chunks['strategy']} ({most_chunks['total_chunks']} chunks)")
        
        logger.info("\n📋 Detalles por estrategia:")
        for result in self.results:
            logger.info(
                f"\n  {result['strategy'].upper()}:"
                f"\n    - Chunks: {result['total_chunks']}"
                f"\n    - Tiempo: {result['elapsed_time']:.2f}s"
                f"\n    - Tamaño promedio: {result['average_size']:.0f} chars"
                f"\n    - Velocidad: {result['chunks_per_second']:.1f} chunks/s"
            )


def main():
    """Función principal del benchmark"""
    benchmark = ChunkingBenchmark()
    benchmark.run_all_benchmarks()
    benchmark.print_summary()


if __name__ == "__main__":
    main()