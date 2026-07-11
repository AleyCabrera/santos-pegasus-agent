# check_env.py
import sys
import os
from pathlib import Path

print("=== Verificación del entorno ===")
print(f"Python version: {sys.version}")
print(f"Python path: {sys.executable}")
print(f"Current directory: {Path.cwd()}")

# Verificar importaciones
try:
    from dotenv import load_dotenv
    print("✅ python-dotenv instalado")
except ImportError as e:
    print(f"❌ python-dotenv NO instalado: {e}")

try:
    import pytest
    print(f"✅ pytest instalado (versión {pytest.__version__})")
except ImportError as e:
    print(f"❌ pytest NO instalado: {e}")

try:
    import pandas
    print(f"✅ pandas instalado (versión {pandas.__version__})")
except ImportError as e:
    print(f"❌ pandas NO instalado: {e}")

print("=== Fin de verificación ===")