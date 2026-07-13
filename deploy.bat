@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ============================================================
echo 🚀 SANTOS PEGASUS RAG AGENT - DEPLOY
echo ============================================================
echo.

REM ============================================================
REM 1. VERIFICAR DOCKER
REM ============================================================
echo 📌 Verificando Docker...
where docker >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Docker no esta instalado.
    echo    Descarga Docker Desktop desde: https://www.docker.com/products/docker-desktop/
    pause
    exit /b 1
)
echo ✅ Docker encontrado

REM ============================================================
REM 2. VERIFICAR DOCKER COMPOSE
REM ============================================================
echo 📌 Verificando Docker Compose...
docker-compose --version >nul 2>nul
if %errorlevel% neq 0 (
    echo ⚠️ Docker Compose no encontrado, usando 'docker compose'...
    set COMPOSE_CMD=docker compose
) else (
    set COMPOSE_CMD=docker-compose
)
echo ✅ Listo

REM ============================================================
REM 3. VERIFICAR ARCHIVOS
REM ============================================================
echo 📌 Verificando archivos...
if not exist "Dockerfile" (
    echo ❌ Dockerfile no encontrado
    pause
    exit /b 1
)
if not exist "docker-compose.yml" (
    echo ❌ docker-compose.yml no encontrado
    pause
    exit /b 1
)
echo ✅ Archivos OK

REM ============================================================
REM 4. MENÚ DE DEPLOY
REM ============================================================
echo.
echo 📋 ¿Que servicio deseas desplegar?
echo    1) FastAPI + Ollama (Backend)
echo    2) Streamlit + Ollama (Frontend UI)
echo    3) Ambos (Full Stack)
echo    4) Solo Ollama
echo    5) Ver estado de servicios
echo    6) Detener servicios
echo    7) Salir
echo.

set /p DEPLOY_OPTION="Selecciona una opcion (1-7): "

if "%DEPLOY_OPTION%"=="1" goto deploy_api
if "%DEPLOY_OPTION%"=="2" goto deploy_ui
if "%DEPLOY_OPTION%"=="3" goto deploy_full
if "%DEPLOY_OPTION%"=="4" goto deploy_ollama
if "%DEPLOY_OPTION%"=="5" goto check_status
if "%DEPLOY_OPTION%"=="6" goto stop_services
if "%DEPLOY_OPTION%"=="7" goto exit

echo ❌ Opcion no valida
pause
goto :eof

REM ============================================================
REM DEPLOY API
REM ============================================================
:deploy_api
echo.
echo 🚀 Desplegando FastAPI + Ollama...
%COMPOSE_CMD% up -d ollama
echo ⏳ Esperando que Ollama este listo...
timeout /t 15 /nobreak >nul
%COMPOSE_CMD% up -d app
echo.
echo ✅ FastAPI disponible en: http://localhost:8000
echo ✅ Docs en: http://localhost:8000/docs
echo ✅ Health check: http://localhost:8000/api/v1/health
goto show_commands

REM ============================================================
REM DEPLOY UI
REM ============================================================
:deploy_ui
echo.
echo 🚀 Desplegando Streamlit + Ollama...
%COMPOSE_CMD% up -d ollama
echo ⏳ Esperando que Ollama este listo...
timeout /t 15 /nobreak >nul
%COMPOSE_CMD% up -d ui
echo.
echo ✅ Streamlit disponible en: http://localhost:8501
goto show_commands

REM ============================================================
REM DEPLOY FULL
REM ============================================================
:deploy_full
echo.
echo 🚀 Desplegando Full Stack...
%COMPOSE_CMD% up -d
echo.
echo ✅ FastAPI disponible en: http://localhost:8000
echo ✅ Docs en: http://localhost:8000/docs
echo ✅ Streamlit disponible en: http://localhost:8501
echo ✅ Ollama disponible en: http://localhost:11434
goto show_commands

REM ============================================================
REM DEPLOY OLLAMA
REM ============================================================
:deploy_ollama
echo.
echo 🚀 Desplegando solo Ollama...
%COMPOSE_CMD% up -d ollama
echo ✅ Ollama disponible en: http://localhost:11434
goto show_commands

REM ============================================================
REM CHECK STATUS
REM ============================================================
:check_status
echo.
echo 📊 Estado de los servicios:
%COMPOSE_CMD% ps
echo.
pause
goto :eof

REM ============================================================
REM STOP SERVICES
REM ============================================================
:stop_services
echo.
echo 🛑 Deteniendo servicios...
%COMPOSE_CMD% down
echo ✅ Servicios detenidos
echo.
pause
goto :eof

REM ============================================================
REM MOSTRAR COMANDOS UTILES
REM ============================================================
:show_commands
echo.
echo ============================================================
echo ✅ DEPLOY COMPLETADO EXITOSAMENTE
echo ============================================================
echo.
echo 📋 Comandos utiles:
echo    - Ver logs:        docker logs santos-pegasus-app
echo    - Ver estado:      %COMPOSE_CMD% ps
echo    - Detener:         %COMPOSE_CMD% down
echo    - Reiniciar:       %COMPOSE_CMD% restart
echo    - Verificar deploy: python verify_deploy.py
echo.
pause
goto :eof

:exit
echo 👋 ¡Hasta luego!