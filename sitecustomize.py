"""Bootstrap para entornos donde la raíz del proyecto no está en sys.path.

Python importa automáticamente sitecustomize si está en sys.path al arrancar. Este
archivo añade la ruta del proyecto (la carpeta raíz del repo) a sys.path para
asegurar que "import app" funcione incluso si Streamlit ejecuta un script desde
un subdirectorio.

Esto es una solución conservadora para entornos PaaS como Streamlit Cloud.
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
