# test_manual.py
"""
Script de prueba manual para verificar los loaders
Ejecutar con: python test_manual.py
"""

from pathlib import Path
from app.loaders import PDFLoader, CSVLoader
from app.utils.logger import logger
import sys

def test_pdf_loader():
    """Prueba el cargador de PDF"""
    logger.info("=" * 50)
    logger.info("📄 Probando PDFLoader")
    logger.info("=" * 50)
    
    # Buscar archivos PDF en la carpeta data/pdfs
    pdf_dir = Path("data/pdfs")
    pdf_files = list(pdf_dir.glob("*.pdf"))
    
    if not pdf_files:
        logger.warning("⚠️ No se encontraron archivos PDF en data/pdfs/")
        logger.info("💡 Para probar, crea un PDF con el siguiente comando:")
        print("""
        python -c "
        from reportlab.pdfgen import canvas
        c = canvas.Canvas('data/pdfs/test.pdf')
        c.drawString(100, 750, 'Test PDF para Santos Pegasus Agent')
        c.drawString(100, 730, 'Este es un documento de prueba')
        c.drawString(100, 710, 'Contenido para pruebas de carga')
        c.save()
        print('✅ PDF creado en data/pdfs/test.pdf')
        "
        """)
        return
    
    # Probar cada PDF encontrado
    for pdf_path in pdf_files:
        try:
            logger.info(f"📄 Cargando: {pdf_path.name}")
            pdf_loader = PDFLoader(pdf_path)
            pdf_docs = pdf_loader.load()
            
            logger.info(f"✅ {pdf_path.name}: {len(pdf_docs)} documentos cargados")
            
            # Mostrar primer documento como ejemplo
            if pdf_docs:
                first_doc = pdf_docs[0]
                logger.info(f"📝 Primer documento ({len(first_doc.page_content)} caracteres):")
                print("-" * 40)
                print(first_doc.page_content[:200] + "..." if len(first_doc.page_content) > 200 else first_doc.page_content)
                print("-" * 40)
                
        except Exception as e:
            logger.error(f"❌ Error cargando {pdf_path.name}: {e}")

def test_csv_loader():
    """Prueba el cargador de CSV"""
    logger.info("=" * 50)
    logger.info("📊 Probando CSVLoader")
    logger.info("=" * 50)
    
    csv_dir = Path("data/csv")
    csv_files = list(csv_dir.glob("*.csv"))
    
    if not csv_files:
        logger.warning("⚠️ No se encontraron archivos CSV en data/csv/")
        logger.info("💡 Para probar, crea un CSV de prueba:")
        print("""
        cat > data/csv/test.csv << 'EOF'
        nombre,edad,ciudad,profesion
        Juan,30,Madrid,Ingeniero
        Maria,25,Barcelona,Doctora
        Pedro,35,Valencia,Profesor
        Ana,28,Sevilla,Arquitecta
        EOF
        """)
        return
    
    # Probar cada CSV encontrado
    for csv_path in csv_files:
        try:
            logger.info(f"📊 Cargando: {csv_path.name}")
            
            # Intentar cargar con diferentes separadores
            try:
                csv_loader = CSVLoader(csv_path)
                csv_docs = csv_loader.load()
            except Exception as e:
                logger.warning(f"⚠️ Error con separador por defecto: {e}")
                logger.info("🔄 Intentando con separador punto y coma...")
                # Crear loader con delimitador específico
                csv_loader = CSVLoader(csv_path, delimiter=';')
                csv_docs = csv_loader.load()
            
            logger.info(f"✅ {csv_path.name}: {len(csv_docs)} filas cargadas")
            
            # Mostrar resumen
            if csv_docs:
                first_doc = csv_docs[0]
                logger.info(f"📝 Primera fila: {len(first_doc.page_content)} caracteres")
                print("-" * 40)
                print(first_doc.page_content[:200] + "..." if len(first_doc.page_content) > 200 else first_doc.page_content)
                print("-" * 40)
                
                # Mostrar estructura del documento
                if first_doc.metadata:
                    logger.info(f"📋 Metadatos: {list(first_doc.metadata.keys())}")
                    
        except Exception as e:
            logger.error(f"❌ Error cargando {csv_path.name}: {e}")
            
            # Mostrar contenido del archivo para debugging
            try:
                with open(csv_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    logger.info(f"📄 El archivo tiene {len(lines)} líneas")
                    logger.info(f"📄 Primeras 3 líneas:")
                    for i, line in enumerate(lines[:3]):
                        print(f"  Línea {i+1}: {line[:100]}...")
            except:
                pass

def test_with_existing_files():
    """Prueba con archivos específicos si existen"""
    logger.info("=" * 50)
    logger.info("🔍 Probando archivos específicos")
    logger.info("=" * 50)
    
    # Probar archivos específicos si existen
    specific_files = [
        ("data/pdfs/manual_onboarding.pdf", PDFLoader),
        ("data/csv/incidentes_protocolo.csv", CSVLoader),
    ]
    
    for file_path, LoaderClass in specific_files:
        path = Path(file_path)
        if path.exists():
            try:
                logger.info(f"📄 Probando: {file_path}")
                loader = LoaderClass(path)
                docs = loader.load()
                logger.info(f"✅ Cargado: {len(docs)} documentos")
            except Exception as e:
                logger.error(f"❌ Error: {e}")
        else:
            logger.info(f"⏭️  Archivo no encontrado: {file_path}")

def create_sample_files():
    """Crea archivos de muestra para pruebas"""
    logger.info("=" * 50)
    logger.info("📝 Creando archivos de muestra")
    logger.info("=" * 50)
    
    # Crear PDF de muestra
    pdf_dir = Path("data/pdfs")
    pdf_dir.mkdir(parents=True, exist_ok=True)
    
    pdf_path = pdf_dir / "sample.pdf"
    if not pdf_path.exists():
        try:
            from reportlab.pdfgen import canvas
            c = canvas.Canvas(str(pdf_path))
            c.drawString(100, 750, "Sample PDF for Santos Pegasus Agent")
            c.drawString(100, 730, "Este es un documento de prueba")
            c.drawString(100, 710, "Contenido para pruebas de carga")
            c.save()
            logger.info(f"✅ PDF creado: {pdf_path}")
        except ImportError:
            logger.warning("⚠️ reportlab no instalado. No se pudo crear PDF")
    
    # Crear CSV de muestra
    csv_dir = Path("data/csv")
    csv_dir.mkdir(parents=True, exist_ok=True)
    
    csv_path = csv_dir / "sample.csv"
    if not csv_path.exists():
        with open(csv_path, 'w', encoding='utf-8') as f:
            f.write("nombre,edad,ciudad,profesion\n")
            f.write("Juan,30,Madrid,Ingeniero\n")
            f.write("Maria,25,Barcelona,Doctora\n")
            f.write("Pedro,35,Valencia,Profesor\n")
            f.write("Ana,28,Sevilla,Arquitecta\n")
        logger.info(f"✅ CSV creado: {csv_path}")

def main():
    """Función principal"""
    print("\n" + "=" * 60)
    print("🚀 SANTOS PEGASUS AGENT - TEST MANUAL")
    print("=" * 60 + "\n")
    
    # Verificar estructura de carpetas
    required_dirs = ["data", "data/pdfs", "data/csv", "logs"]
    for dir_path in required_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    # Crear archivos de muestra si no existen
    create_sample_files()
    
    # Ejecutar pruebas
    test_pdf_loader()
    print("\n")
    test_csv_loader()
    print("\n")
    test_with_existing_files()
    
    print("\n" + "=" * 60)
    logger.info("✅ Pruebas manuales completadas")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Prueba interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Error inesperado: {e}")
        sys.exit(1)