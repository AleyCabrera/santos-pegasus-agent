"""Entrypoint para Streamlit Cloud.

Este archivo asegura que el directorio raíz del proyecto esté en sys.path
antes de importar el paquete `app`, y luego ejecuta `app.ui.app` como módulo.

Usar este archivo como entrada en Streamlit Cloud (por defecto Streamlit busca
`streamlit_app.py` en la raíz del repositorio).
"""
from pathlib import Path
import sys
import importlib

# Añadir el directorio raíz del proyecto al sys.path para que las importaciones
# absolutas del paquete `app` funcionen correctamente en entornos como
# Streamlit Cloud donde el módulo puede ejecutarse fuera del paquete.
project_root = Path(__file__).parent.resolve()
sys.path.insert(0, str(project_root))

# Importar el módulo de la interfaz — al importarlo se ejecuta y registra los
# componentes de Streamlit (el script app/ui/app.py está diseñado para
# ejecutarse cuando se importa).
importlib.import_module("app.ui.app")
