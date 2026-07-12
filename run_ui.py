"""Script para ejecutar la interfaz Streamlit"""

import sys
import subprocess
from pathlib import Path

def main():
    """Ejecuta la interfaz Streamlit"""
    
    # Obtener la ruta del archivo app.py
    app_path = Path(__file__).parent / "app" / "ui" / "app.py"
    
    # Comando para ejecutar Streamlit
    cmd = [
        "streamlit",
        "run",
        str(app_path),
        "--server.port=8501",
        "--server.address=localhost"  # Cambiado de 0.0.0.0 a localhost
    ]
    
    print(f"🚀 Ejecutando: {' '.join(cmd)}")
    print("📱 Abre: http://localhost:8501")
    print("⚠️  Presiona Ctrl+C para detener")
    print("-" * 50)
    
    # Ejecutar Streamlit
    sys.exit(subprocess.call(cmd))

if __name__ == "__main__":
    main()