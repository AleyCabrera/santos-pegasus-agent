#!/bin/bash
# setup.sh - Script de instalación para Git Bash

echo "🚀 Configurando entorno para Python 3.12..."

# 1. Salir del entorno actual
deactivate 2>/dev/null

# 2. Eliminar entorno viejo
echo "📦 Eliminando entorno viejo..."
rm -rf .venv

# 3. Crear nuevo entorno con Python 3.12
echo "🔧 Creando nuevo entorno virtual..."
python3.12 -m venv .venv 2>/dev/null || /c/Users/Aley\ Cabrera\ D/AppData/Local/Programs/Python/Python312/python.exe -m venv .venv

# 4. Activar entorno
echo "🔌 Activando entorno..."
source .venv/Scripts/activate

# 5. Verificar versión
echo "📌 Versión de Python:"
python --version

# 6. Actualizar herramientas
echo "⬆️ Actualizando pip..."
python -m pip install --upgrade pip setuptools wheel

# 7. Instalar dependencias
echo "📦 Instalando dependencias..."
pip install pandas==2.0.3 --only-binary :all:
pip install torch==2.4.0 --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt

# 8. Verificar instalación
echo "✅ Verificando instalación..."
pip list | grep -E "pandas|torch|langchain|pytest|fastapi"

echo "🎉 ¡Instalación completada!"
echo "📌 Para activar el entorno en el futuro: source .venv/Scripts/activate"