"""Configuración de pytest"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path para importaciones
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configuración adicional de pytest
import pytest
from dotenv import load_dotenv

# Cargar variables de entorno para tests
load_dotenv()

@pytest.fixture(autouse=True)
def setup_test_env():
    """Configuración automática para todos los tests"""
    # Configurar variables de entorno para tests
    import os
    os.environ['DEBUG'] = 'True'
    os.environ['LOG_LEVEL'] = 'ERROR'