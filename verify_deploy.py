#!/usr/bin/env python3
"""Script para verificar el despliegue en Docker"""

import requests
import sys
import time
import subprocess
import json
from pathlib import Path

# Colores para terminal
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def check_service(url: str, name: str, timeout: int = 5) -> bool:
    """Verifica que un servicio esté respondiendo"""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            print(f"{GREEN}✅ {name}: OK (status {response.status_code}){RESET}")
            return True
        else:
            print(f"{YELLOW}⚠️ {name}: Status {response.status_code}{RESET}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"{RED}❌ {name}: No responde (ConnectionError){RESET}")
        return False
    except requests.exceptions.Timeout:
        print(f"{RED}❌ {name}: Timeout{RESET}")
        return False
    except Exception as e:
        print(f"{RED}❌ {name}: {e}{RESET}")
        return False

def check_docker_container(container_name: str) -> bool:
    """Verifica que un contenedor esté corriendo"""
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", f"name={container_name}", "--format", "{{.Status}}"],
            capture_output=True,
            text=True
        )
        if "Up" in result.stdout:
            print(f"{GREEN}✅ Contenedor {container_name}: Corriendo{RESET}")
            return True
        else:
            print(f"{RED}❌ Contenedor {container_name}: No está corriendo{RESET}")
            return False
    except Exception as e:
        print(f"{RED}❌ Error verificando contenedor {container_name}: {e}{RESET}")
        return False

def check_ollama_model(model_name: str = "llama3.2:3b") -> bool:
    """Verifica que el modelo de Ollama esté descargado"""
    try:
        # Usar docker exec para verificar el modelo
        result = subprocess.run(
            ["docker", "exec", "santos-pegasus-ollama", "ollama", "list"],
            capture_output=True,
            text=True
        )
        if model_name in result.stdout:
            print(f"{GREEN}✅ Modelo {model_name}: Descargado{RESET}")
            return True
        else:
            print(f"{YELLOW}⚠️ Modelo {model_name}: No encontrado. Descargando...{RESET}")
            # Intentar descargar
            subprocess.run(
                ["docker", "exec", "santos-pegasus-ollama", "ollama", "pull", model_name],
                capture_output=True,
                text=True
            )
            return False
    except Exception as e:
        print(f"{RED}❌ Error verificando modelo: {e}{RESET}")
        return False

def main():
    """Verifica todos los servicios"""
    print("\n" + "="*60)
    print("🔍 VERIFICANDO DESPLIEGUE")
    print("="*60 + "\n")
    
    # 1. Verificar contenedores
    print("📦 Verificando contenedores:")
    containers = ["santos-pegasus-ollama", "santos-pegasus-app", "santos-pegasus-ui"]
    all_ok = True
    
    for container in containers:
        if not check_docker_container(container):
            all_ok = False
    print()
    
    # 2. Verificar modelos de Ollama
    print("🧠 Verificando modelos de Ollama:")
    if not check_ollama_model():
        print("   ⚠️ El modelo se está descargando. Espera unos minutos...")
    print()
    
    # 3. Verificar servicios HTTP
    print("🌐 Verificando servicios HTTP:")
    
    services = {
        "FastAPI": {
            "url": "http://localhost:8000/api/v1/health",
            "timeout": 5
        },
        "Streamlit": {
            "url": "http://localhost:8501",
            "timeout": 5
        },
        "Ollama": {
            "url": "http://localhost:11434/api/tags",
            "timeout": 5
        }
    }
    
    services_ok = True
    for name, config in services.items():
        if not check_service(config["url"], name, config["timeout"]):
            services_ok = False
        print()
    
    # 4. Resumen
    print("="*60)
    if all_ok and services_ok:
        print(f"{GREEN}✅ ¡TODOS LOS SERVICIOS ESTÁN FUNCIONANDO!{RESET}")
        print("\n📱 Puedes acceder a:")
        print("   FastAPI:   http://localhost:8000")
        print("   FastAPI Docs: http://localhost:8000/docs")
        print("   Streamlit: http://localhost:8501")
        print("   Ollama:    http://localhost:11434")
    else:
        print(f"{YELLOW}⚠️ Algunos servicios no responden correctamente{RESET}")
        print("\n📋 Comandos útiles:")
        print("   - Ver logs:     docker-compose logs -f")
        print("   - Ver estado:   docker-compose ps")
        print("   - Reiniciar:    docker-compose restart")
        print("   - Detener:      docker-compose down")
        
        if not all_ok:
            print("\n🔍 Problema: Contenedores no están corriendo")
            print("   Solución: docker-compose up -d")
        
        if not services_ok:
            print("\n🔍 Problema: Servicios no responden")
            print("   Solución: Espera a que los servicios terminen de iniciar (2-3 minutos)")
            print("   o revisa los logs: docker-compose logs -f")
    print("="*60 + "\n")
    
    return 0 if (all_ok and services_ok) else 1

if __name__ == "__main__":
    sys.exit(main())