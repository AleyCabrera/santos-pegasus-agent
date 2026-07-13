#!/bin/bash

# ============================================================
# Script de detención - Santos Pegasus RAG Agent
# ============================================================

echo "🛑 Deteniendo Santos Pegasus RAG Agent..."
echo ""

docker-compose down

echo ""
echo "✅ Servicios detenidos correctamente"
echo ""
echo "💡 Los datos se mantienen en los volúmenes de Docker."
echo "   Para eliminar los datos también:"
echo "   docker-compose down -v"