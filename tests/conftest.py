# tests/conftest.py
"""Configuración de pytest"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path para importaciones
sys.path.insert(0, str(Path(__file__).parent.parent))

# Importar pytest y dotenv primero
import pytest
from dotenv import load_dotenv

# Cargar variables de entorno para tests
load_dotenv()

@pytest.fixture(autouse=True)
def setup_test_env():
    """Configuración automática para todos los tests"""
    # Configurar variables de entorno para tests
    os.environ['DEBUG'] = 'True'
    os.environ['LOG_LEVEL'] = 'ERROR'
    yield  # Esto permite que el fixture se ejecute antes y después del test

# Configuración adicional (opcional)
def pytest_configure(config):
    """Configuración de pytest antes de ejecutar los tests"""
    # Configurar opciones de pytest
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")