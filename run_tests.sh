#!/bin/bash
# run_tests.sh - Script para ejecutar pruebas con cobertura

echo "🧪 Ejecutando pruebas con cobertura..."

# Activar entorno (si no está activado)
source .venv/Scripts/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null

# Instalar dependencias de prueba si no están
pip install pytest pytest-cov -q

# Ejecutar pruebas
pytest tests/ -v \
    --cov=app \
    --cov-report=term-missing \
    --cov-report=html \
    --cov-report=xml \
    --cov-omit="tests/*,app/config.py"

# Mostrar resumen
echo ""
echo "📊 Reporte de cobertura generado en:"
echo "  - HTML: htmlcov/index.html"
echo "  - XML: coverage.xml"
echo ""
echo "Abrir reporte HTML: start htmlcov/index.html"