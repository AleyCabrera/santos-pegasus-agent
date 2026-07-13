#!/bin/bash

# ============================================================
# Script de inicio - Santos Pegasus RAG Agent
# ============================================================

echo "🚀 Iniciando Santos Pegasus RAG Agent con Docker..."
echo ""

# Verificar que Docker esté corriendo
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker no está corriendo. Por favor, inicia Docker Desktop."
    exit 1
fi

# Verificar que docker-compose esté disponible
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose no está instalado."
    exit 1
fi

echo "✅ Docker está corriendo"
echo ""

# Construir y levantar los servicios
echo "🔨 Construyendo imágenes Docker..."
docker-compose up --build -d

echo ""
echo "⏳ Esperando a que los servicios estén listos..."
sleep 15

# Verificar el estado de los servicios
echo ""
echo "📊 Estado de los servicios:"
docker-compose ps

echo ""
echo "✅ Servicios iniciados correctamente"
echo ""
echo "🌐 Accede a la aplicación en:"
echo "   Streamlit: http://localhost:8501"
echo "   FastAPI:   http://localhost:8000"
echo "   FastAPI Docs: http://localhost:8000/docs"
echo ""
echo "📝 Para ver los logs:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 Para detener los servicios:"
echo "   docker-compose down"