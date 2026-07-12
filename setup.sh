#!/bin/bash
# setup_final.sh - Instalación final para Windows

echo "🔧 Configurando entorno para Windows..."

# 1. Activar entorno
source .venv/Scripts/activate

# 2. Actualizar herramientas
echo "⬆️ Actualizando pip, setuptools y wheel..."
python -m pip install --upgrade pip setuptools wheel

# 3. Instalar NumPy (precompilado)
echo "📦 Instalando NumPy 1.26.4..."
pip install numpy==1.26.4 --only-binary :all:

# 4. Instalar SciPy (precompilado)
echo "📦 Instalando SciPy 1.11.4..."
pip install scipy==1.11.4 --only-binary :all:

# 5. Instalar PyTorch (CPU)
echo "📦 Instalando PyTorch 2.3.1..."
pip install torch==2.3.1 --index-url https://download.pytorch.org/whl/cpu

# 6. Instalar TorchVision
echo "📦 Instalando TorchVision 0.18.1..."
pip install torchvision==0.18.1 --index-url https://download.pytorch.org/whl/cpu

# 7. Instalar FAISS
echo "📦 Instalando FAISS 1.8.0..."
pip install faiss-cpu==1.8.0

# 8. Instalar Sentence-Transformers
echo "📦 Instalando Sentence-Transformers 2.2.2..."
pip install sentence-transformers==2.2.2

# 9. Instalar Transformers
echo "📦 Instalando Transformers 4.41.2..."
pip install transformers==4.41.2

# 9b. Fijar huggingface-hub compatible con sentence-transformers 2.2.2
# (versiones >=0.26 eliminaron cached_download; transformers 4.41.2 requiere >=0.23)
echo "📦 Fijando huggingface-hub compatible..."
pip install "huggingface-hub>=0.23.0,<0.26.0"

# 10. Instalar el resto de dependencias
echo "📦 Instalando resto de dependencias..."
pip install python-dotenv==1.0.1 \
    pydantic==2.9.2 \
    pydantic-settings==2.5.0 \
    PyPDF2==3.0.1 \
    pandas==2.1.4 --only-binary :all: \
    markdown==3.7 \
    langchain==0.3.1 \
    langchain-community==0.3.1 \
    langchain-ollama==0.2.0 \
    fastapi==0.115.0 \
    "uvicorn[standard]==0.30.6" \
    streamlit==1.38.0 \
    httpx==0.27.2 \
    pytest==8.3.3 \
    pytest-cov==5.0.0 \
    black==24.10.0 \
    flake8==7.1.1 \
    mypy==1.11.2 \
    loguru==0.7.2

# 11. Verificar instalación
echo ""
echo "🔍 Verificando instalación..."
python -c "
import sys
packages = {
    'numpy': '1.26.4',
    'scipy': '1.11.4',
    'torch': '2.3.1',
    'torchvision': '0.18.1',
    'faiss': '1.8.0',
    'sentence_transformers': '2.2.2',
    'transformers': '4.41.2'
}

ok = True
for pkg, ver in packages.items():
    try:
        mod = __import__(pkg.replace('-', '_'))
        installed = getattr(mod, '__version__', 'desconocido')
        status = '✅' if ver in installed else '⚠️'
        print(f'{status} {pkg}: {installed} (esperado: {ver})')
        if ver not in installed:
            ok = False
    except ImportError:
        print(f'❌ {pkg}: NO INSTALADO')
        ok = False

if ok:
    print('\n✅ Todas las dependencias instaladas correctamente!')
else:
    print('\n⚠️ Algunas dependencias tienen versiones diferentes')
"

# 12. Ejecutar pruebas
echo ""
echo "🧪 Ejecutando pruebas..."
pytest tests/ -v