"""Script para ejecutar la interfaz Streamlit"""
import sys
import os
from pathlib import Path

# Forzar UTF-8 en Windows para evitar errores con emojis
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'

def main():
    """Ejecuta la interfaz Streamlit"""
    cmd = [
        "streamlit",
        "run",
        str(Path(__file__).parent / "app" / "ui" / "app.py"),
        "--server.port=8501",
        "--server.address=0.0.0.0"
    ]
    
    # Imprimir sin emojis para evitar problemas de codificación en Windows
    print("Ejecutando Streamlit...")
    print(f"Comando: {' '.join(cmd)}")
    print("Abre: http://localhost:8501")
    print("Presiona Ctrl+C para detener")
    print("-" * 50)
    
    # Ejecutar Streamlit
    import streamlit.web.cli as stcli
    sys.argv = cmd
    sys.exit(stcli.main())

if __name__ == "__main__":
    main()