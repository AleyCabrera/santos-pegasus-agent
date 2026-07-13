#!/bin/bash

# ============================================================
# SCRIPT DE DEPLOY - Santos Pegasus RAG Agent
# Para Linux y macOS
# ============================================================

set -e

# Colores para mejor legibilidad
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "============================================================"
echo "🚀 SANTOS PEGASUS RAG AGENT - DEPLOY"
echo "============================================================"
echo ""

# ============================================================
# 1. VERIFICAR DOCKER
# ============================================================
echo -e "${BLUE}📌 Verificando Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker no está instalado.${NC}"
    echo "   Instala Docker: https://docs.docker.com/get-docker/"
    exit 1
fi
echo -e "${GREEN}✅ Docker encontrado${NC}"

# ============================================================
# 2. VERIFICAR DOCKER COMPOSE
# ============================================================
echo -e "${BLUE}📌 Verificando Docker Compose...${NC}"
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    echo -e "${RED}❌ Docker Compose no encontrado${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker Compose listo${NC}"

# ============================================================
# 3. VERIFICAR ARCHIVOS
# ============================================================
echo -e "${BLUE}📌 Verificando archivos...${NC}"
if [ ! -f "Dockerfile" ]; then
    echo -e "${RED}❌ Dockerfile no encontrado${NC}"
    exit 1
fi
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}❌ docker-compose.yml no encontrado${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Archivos OK${NC}"

# ============================================================
# 4. MENÚ DE DEPLOY
# ============================================================
echo ""
echo -e "${BLUE}📋 ¿Qué servicio deseas desplegar?${NC}"
echo "   1) FastAPI + Ollama (Backend)"
echo "   2) Streamlit + Ollama (Frontend UI)"
echo "   3) Ambos (Full Stack)"
echo "   4) Solo Ollama"
echo "   5) Ver estado de servicios"
echo "   6) Detener servicios"
echo "   7) Salir"
echo ""

read -p "Selecciona una opción (1-7): " DEPLOY_OPTION

case $DEPLOY_OPTION in
    1)
        echo ""
        echo -e "${GREEN}🚀 Desplegando FastAPI + Ollama...${NC}"
        $COMPOSE_CMD up -d ollama
        echo -e "${YELLOW}⏳ Esperando que Ollama esté listo...${NC}"
        sleep 15
        $COMPOSE_CMD up -d app
        echo ""
        echo -e "${GREEN}✅ FastAPI disponible en: http://localhost:8000${NC}"
        echo -e "${GREEN}✅ Docs en: http://localhost:8000/docs${NC}"
        echo -e "${GREEN}✅ Health check: http://localhost:8000/api/v1/health${NC}"
        ;;
    2)
        echo ""
        echo -e "${GREEN}🚀 Desplegando Streamlit + Ollama...${NC}"
        $COMPOSE_CMD up -d ollama
        echo -e "${YELLOW}⏳ Esperando que Ollama esté listo...${NC}"
        sleep 15
        $COMPOSE_CMD up -d ui
        echo ""
        echo -e "${GREEN}✅ Streamlit disponible en: http://localhost:8501${NC}"
        ;;
    3)
        echo ""
        echo -e "${GREEN}🚀 Desplegando Full Stack...${NC}"
        $COMPOSE_CMD up -d
        echo ""
        echo -e "${GREEN}✅ FastAPI disponible en: http://localhost:8000${NC}"
        echo -e "${GREEN}✅ Docs en: http://localhost:8000/docs${NC}"
        echo -e "${GREEN}✅ Streamlit disponible en: http://localhost:8501${NC}"
        echo -e "${GREEN}✅ Ollama disponible en: http://localhost:11434${NC}"
        ;;
    4)
        echo ""
        echo -e "${GREEN}🚀 Desplegando solo Ollama...${NC}"
        $COMPOSE_CMD up -d ollama
        echo ""
        echo -e "${GREEN}✅ Ollama disponible en: http://localhost:11434${NC}"
        ;;
    5)
        echo ""
        echo -e "${BLUE}📊 Estado de los servicios:${NC}"
        $COMPOSE_CMD ps
        echo ""
        read -p "Presiona Enter para continuar..."
        exit 0
        ;;
    6)
        echo ""
        echo -e "${YELLOW}🛑 Deteniendo servicios...${NC}"
        $COMPOSE_CMD down
        echo -e "${GREEN}✅ Servicios detenidos${NC}"
        echo ""
        exit 0
        ;;
    7)
        echo -e "${GREEN}👋 ¡Hasta luego!${NC}"
        exit 0
        ;;
    *)
        echo -e "${RED}❌ Opción no válida${NC}"
        exit 1
        ;;
esac

# ============================================================
# MOSTRAR COMANDOS ÚTILES
# ============================================================
echo ""
echo "============================================================"
echo -e "${GREEN}✅ DEPLOY COMPLETADO EXITOSAMENTE${NC}"
echo "============================================================"
echo ""
echo -e "${YELLOW}📋 Comandos útiles:${NC}"
echo "   - Ver logs:        docker logs santos-pegasus-app"
echo "   - Ver estado:      $COMPOSE_CMD ps"
echo "   - Detener:         $COMPOSE_CMD down"
echo "   - Reiniciar:       $COMPOSE_CMD restart"
echo "   - Verificar deploy: python verify_deploy.py"
echo ""