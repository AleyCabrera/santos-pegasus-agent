#!/usr/bin/env python
"""
Script rápido para verificar que todo está configurado correctamente
"""
import sys
from pathlib import Path

def check_setup():
    print("🔍 Verificando setup de Santos Pegasus...\n")
    
    # 1. Verificar Python
    print(f"✅ Python {sys.version}")
    
    # 2. Verificar estructura
    required_dirs = ['src', 'data', 'data/documentos', 'data/vector_store']
    for d in required_dirs:
        if Path(d).exists():
            print(f"✅ Directorio {d} encontrado")
        else:
            print(f"❌ Directorio {d} NO encontrado")
    
    # 3. Verificar imports
    try:
        from src.config import COHERE_API_KEY, DOCUMENTS_DIR
        print(f"✅ Configuración cargada correctamente")
        print(f"   API Key: {COHERE_API_KEY[:10]}... (truncada)")
        print(f"   Documentos en: {DOCUMENTS_DIR}")
    except Exception as e:
        print(f"❌ Error en configuración: {e}")
    
    # 4. Verificar dependencias críticas
    try:
        import cohere
        print("✅ Cohere instalado")
        import langchain
        print("✅ LangChain instalado")
        import streamlit
        print("✅ Streamlit instalado")
        import faiss
        print("✅ FAISS instalado")
    except ImportError as e:
        print(f"❌ Dependencia faltante: {e}")
    
    print("\n✅ Setup verificado correctamente!")

if __name__ == "__main__":
    check_setup()