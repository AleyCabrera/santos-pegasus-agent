# 🤖 Santos Pegasus Soluciones - Agente IA RAG

> *Asistente virtual inteligente con arquitectura Retrieval Augmented Generation (RAG) para documentación interna empresarial.*

![Python](https://img.shields.io/badge/Python-3.12-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green) ![Streamlit](https://img.shields.io/badge/Streamlit-1.41-red) ![Docker](https://img.shields.io/badge/Docker-Ready-blueviolet) ![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📋 **ÍNDICE**

- [🤖 Santos Pegasus Soluciones - Agente IA RAG](#-santos-pegasus-soluciones---agente-ia-rag)
  - [📋 **ÍNDICE**](#-índice)
  - [🎯 **Introducción**](#-introducción)
    - [**Características Principales**](#características-principales)
  - [💼 **Problema de Negocio**](#-problema-de-negocio)
    - [**Contexto**](#contexto)
    - [**El Problema**](#el-problema)
    - [**La Solución**](#la-solución)
  - [🏗️ **Arquitectura del Sistema**](#️-arquitectura-del-sistema)
    - [**Diagrama de Arquitectura**](#diagrama-de-arquitectura)
  - [**Flujo de Datos**](#flujo-de-datos)
  - [**🛠️ Tecnologías Utilizadas**](#️-tecnologías-utilizadas)
  - [**📂 Estructura del Proyecto**](#-estructura-del-proyecto)
  - [**🔧 Instalación**](#-instalación)
  - [**⚙️ Variables de Entorno**](#️-variables-de-entorno)
  - [**🚀 Cómo Ejecutar el Proyecto**](#-cómo-ejecutar-el-proyecto)
  - [**📸 Capturas de Pantalla**](#-capturas-de-pantalla)
  - [**👥 Autor**](#-autor)
  - [**🙏 Agradecimientos**](#-agradecimientos)
    - [📝 Instrucciones finales:](#-instrucciones-finales)

---

## 🎯 **Introducción**

**Santos Pegasus Soluciones - Agente IA RAG** es un asistente virtual inteligente diseñado para automatizar la consulta de documentación interna empresarial mediante una arquitectura de **Retrieval Augmented Generation (RAG)**.

El sistema permite a los empleados realizar preguntas en lenguaje natural sobre:
- 📋 **Onboarding** - Manual de incorporación y cultura organizacional.
- 🔧 **Backend** - Guías de ingeniería y estándares de código.
- 🎨 **Frontend** - Stack tecnológico y mejores prácticas.
- 🚨 **Incidentes** - Protocolos de respuesta y post-mortems.
- 🏗️ **Arquitectura** - Microservicios y dependencias.

### **Características Principales**
- 🤖 **Generación de respuestas** con modelo LLM local (Ollama - llama3.2:3b).
- 🔍 **Búsqueda semántica** mediante embeddings y FAISS.
- 📚 **Conocimiento específico** de la empresa a través de documentos internos.
- 💬 **Interfaz conversacional** moderna con Streamlit.
- 🔌 **API REST** robusta con FastAPI.
- 🐳 **Despliegue containerizado** con Docker.

---

## 💼 **Problema de Negocio**

### **Contexto**
Santos Pegasus Soluciones es una empresa de tecnología en crecimiento con múltiples equipos de ingeniería. La organización genera constantemente documentación técnica crítica que suele perderse en repositorios estáticos.

### **El Problema**
Los empleados enfrentan dificultades para:
-  Encontrar información específica en documentos extensos.
- ❌ Acceder rápidamente a protocolos de incidentes críticos.
- ❌ Consultar estándares de código durante el desarrollo.
- ❌ Onboardear eficientemente sin saturar a los desarrolladores senior.

### **La Solución**
Un agente IA conversacional que:
- ✅ Procesa y indexa toda la documentación interna.
- ✅ Responde preguntas en lenguaje natural con precisión.
- ✅ Cita las fuentes de donde obtuvo la información.
- ✅ Está disponible 24/7 sin intervención humana.
- ✅ Funciona 100% local (sin costos de API externas ni fugas de datos).

---

## 🏗️ **Arquitectura del Sistema**

### **Diagrama de Arquitectura**

```text
┌─────────────────────────────────────────────────────────────┐
│                    INTERFAZ DE USUARIO                       │
│  ┌──────────────────┐         ┌──────────────────┐         │
│  │   Streamlit UI   │         │   FastAPI REST   │         │
│  │   (Puerto 8501)  │         │   (Puerto 8000)  │         │
│  └────────┬─────────┘         └────────┬─────────┘         │
└───────────┼─────────────────────────────┼───────────────────┘
            │                             │
            ──────────────┬──────────────┘
                           │
            ┌──────────────▼──────────────┐
            │      ChatService / RAG      │
            │         (Agente IA)         │
            └──────────────┬──────────────┘
                           │
            ┌──────────────▼──────────────┐
            │   LangChain Orchestration   │
            │  ┌───────────────────────┐  │
            │  │   Retrieval Chain     │  │
            │  └───────────────────────┘  │
            └──────────────┬──────────────┘
                           │
            ┌──────────────▼──────────────┐
            │   Vector Store (FAISS)      │
            │   - Embeddings 384-dim      │
            │   - Búsqueda de similitud   │
            ──────────────┬──────────────┘
                           │
            ┌──────────────▼──────────────┐
            │   Embedding Model           │
            │   all-MiniLM-L6-v2 (Local)  │
            └─────────────────────────────┘
                           │
            ┌──────────────▼──────────────┐
            │   LLM (Ollama)              │
            │   llama3.2:3b (Local)       │
            │   Puerto 11434              │
            └─────────────────────────────┘
```

## **Flujo de Datos**

1. Usuario hace una pregunta en Streamlit/FastAPI.
2. ChatService recibe la consulta y la pasa al agente RAG.
3. Embedding Manager convierte la pregunta a vector (384 dimensiones).
4. FAISS busca los documentos más similares (top-k).
5. LangChain construye el prompt con contexto + pregunta.
6. Ollama (llama3.2:3b) genera la respuesta basada en el contexto.
7. Respuesta se devuelve al usuario con fuentes citadas.

## **🛠️ Tecnologías Utilizadas**
**Stack Principal**

| Tecnología            | Versión   | Justificación                                 |
| --------------------- | --------- | --------------------------------------------- |
| Python                | 3.12.9    | Lenguaje principal, ecosistema rico en ML/AI. |
| LangChain             | 0.3.14    | Orquestación de pipelines RAG.                |
| Ollama                | Latest    | LLM local gratuito, sin costos de API.        |
| llama3.2:3b           | 3B params | Modelo ligero, optimizado para 7GB RAM.       |
| FAISS                 | 1.9.0     | Vector store eficiente de Meta (Facebook).    |
| sentence-transformers | 3.3.1     | Embeddings de alta calidad de HuggingFace.    |
| Streamlit             | 1.41.1    | UI rápida y moderna para prototipos.          |
| FastAPI               | 0.115.6   | API REST asíncrona y performante.             |


**¿Por qué todas gratuitas?**

✅ Ollama: Modelos LLM locales sin costos de tokens.

✅ FAISS: Vector store open-source y altamente optimizado.

✅ sentence-transformers: Embeddings gratuitos y ligeros.

✅ Streamlit/FastAPI: Frameworks open-source líderes.

✅ Docker: Containerización estándar de la industria.


## **📂 Estructura del Proyecto**

```
santos-pegasus-agent/
│
├── app/                          # Código principal de la aplicación
│   ├── agents/                   # Definición del agente RAG
│   ├── api/                      # Endpoints FastAPI
│   ├── chains/                   # Cadenas RAG (LangChain)
│   ├── embeddings/               # Gestión de embeddings
│   ├── loaders/                  # Carga de documentos (PDF, CSV, MD)
│   ├── models/                   # Esquemas Pydantic
│   ├── prompts/                  # Plantillas de prompts
│   ├── services/                 # Lógica de negocio
│   ├── ui/                       # Interfaz Streamlit
│   ├── utils/                    # Funciones auxiliares y logger
│   └── vector_store/             # Vector store FAISS
│
├── data/                         # Documentos fuente
│   ├── csv/                      # Archivos CSV
│   ├── markdown/                 # Documentos Markdown
│   └── pdfs/                     # Archivos PDF
│
├── tests/                        # Tests unitarios (pytest)
── vectorstore/                  # Índice FAISS persistido
├── docker-compose.yml            # Orquestación Docker
├── Dockerfile                    # Definición de imagen
├── requirements.txt              # Dependencias Python
├── index_documents.py            # Script de indexación
├── main.py                       # Entry point FastAPI
└── run_ui.py                     # Entry point Streamlit

```

## **🔧 Instalación**

Requisitos Previos
Python 3.12+ instalado.
Git instalado.
Ollama instalado localmente (Descargar aquí).
Docker (opcional, para despliegue containerizado).
Pasos de Instalación.

1. Clonar el repositorio
   
    git clone https://github.com/tu-usuario/santos-pegasus-agent.git
    cd santos-pegasus-agent

2. Crear y activar entorno virtual
   
    ```
    # Windows
    python -m venv .venv
    .venv\Scripts\activate
    # Linux/Mac
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3. Instalar dependencias
   
    ```
    pip install --upgrade pip
    pip install -r requirements.txtpip install --upgrade pip
    pip install -r requirements.txt
    ```

4. Configurar Ollama
   
    ```
    # Descargar el modelo recomendado (3B - balanceado para 7GB RAM)
    ollama pull llama3.2:3b

    # Verificar instalación
    ollama list
    ```

## **⚙️ Variables de Entorno**

Crea un archivo .env en la raíz del proyecto basado en .env.example:
```
# Configuración de Ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
OLLAMA_TEMPERATURE=0.7
OLLAMA_CONTEXT_WINDOW=2048

# Configuración de Embeddings
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Configuración de Vector Store
VECTOR_STORE_PATH=./vectorstore/faiss_index
CHUNK_SIZE=500
CHUNK_OVERLAP=50
SIMILARITY_THRESHOLD=0.3

# Configuración de la Aplicación
APP_NAME=Santos Pegasus Soluciones Agent
APP_VERSION=1.0.0
DEBUG=True
LOG_LEVEL=INFO
```

## **🚀 Cómo Ejecutar el Proyecto**

**Opción 1: Ejecución Local**
1. Iniciar Ollama (asegúrate de que esté corriendo en segundo plano).

2. Indexar documentos:
    ```
    python index_documents.py
    # Selecciona la opción 1 para indexar documentos nuevos
    ```

3. Ejecutar la interfaz Streamlit:
    ```
    python run_ui.py
    # O directamente: streamlit run app/ui/app.py
    ```
    Abre tu navegador en: http://localhost:8501

5. (Opcional) Ejecutar API FastAPI:
    ```
    python main.py
    # O directamente: uvicorn main:app --reload --port 8000
    ```
    Abre la documentación de la API en: http://localhost:8000/docs

**Opción 2: Ejecución con Docker**

```
# Construir y levantar todos los servicios
docker-compose up --build -d

# Verificar que los servicios estén corriendo
docker-compose ps

# Ver logs en tiempo real
docker-compose logs -f
```

Accesos Docker:

| Servicio     | URL                        | Descripción               |
| ------------ | -------------------------- | ------------------------- |
| Streamlit UI | http://localhost:8501      | Interfaz web del agente   |
| FastAPI      | http://localhost:8000      | API REST                  |
| FastAPI Docs | http://localhost:8000/docs | Documentación interactiva |


## **📸 Capturas de Pantalla**

**Interfaz Principal**
https://github.com/AleyCabrera/santos-pegasus-agent/blob/112c1d21f0598f675802c0a2b55ce71a6b40b44d/screenshots/img_1.png
```
https://github.com/AleyCabrera/santos-pegasus-agent/blob/112c1d21f0598f675802c0a2b55ce71a6b40b44d/screenshots/img_1.png
```
**Respuesta con Fuentes**
```
![Descripción de la imagen][([screenshots/img_1.png](https://github.com/AleyCabrera/santos-pegasus-agent/blob/112c1d21f0598f675802c0a2b55ce71a6b40b44d/screenshots/img_1.png))](https://github.com/AleyCabrera/santos-pegasus-agent/blob/112c1d21f0598f675802c0a2b55ce71a6b40b44d/screenshots/img_2.png)
```

![Descripción de la imagen]([screenshots/img_3.png](https://github.com/AleyCabrera/santos-pegasus-agent/blob/112c1d21f0598f675802c0a2b55ce71a6b40b44d/screenshots/img_3.png))



**💬 Ejemplos de Preguntas y Respuestas**

Ejemplo 1: Onboarding
Pregunta: "¿Cuáles son los valores de Santos Pegasus?"

Respuesta del Agente:

```
Santos Pegasus Soluciones se rige por los 
siguientes valores fundamentales:

- Excelencia Técnica: Buscamos la calidad en cada línea de código.
- Colaboración: Trabajamos en equipo para alcanzar objetivos comunes.
- Innovación: Exploramos nuevas tecnologías y metodologías.
```

**📚 Fuente: manual_onboarding.md**

Ejemplo 2: Backend
Pregunta: "¿Qué principios SOLID aplican en el back-end?"

Respuesta del Agente:
```
En Santos Pegasus aplicamos los 5 principios SOLID:
- S - Single Responsibility: Cada clase tiene una única responsabilidad.
- O - Open/Closed: Abierto para extensión, cerrado para modificación.
- L - Liskov Substitution: Subtipos deben ser sustituibles.
- I - Interface Segregation: Interfaces específicas sobre generales.
- D - Dependency Inversion: Depender de abstracciones, no concreciones.
```

**📚 Fuente: guia_backend.md**

Ejemplo 3: Incidentes
Pregunta: "¿Qué es un incidente SEV-1?"

Respuesta del Agente:
Un incidente SEV-1 (Severidad 1) es el nivel más crítico. 

```
Se caracteriza por:
- Impacto: Afecta a todos los usuarios o servicios críticos.
- Tiempo de respuesta: Requiere atención inmediata 24/7.
```

Ejemplos: Caída total del sistema, pérdida de datos, brecha de seguridad.
Fuente: protocolo_incidentes.md


**🧪 Testing**

El proyecto incluye una suite de tests unitarios con pytest que cubre loaders, chunking, embeddings, vector store y el agente RAG.

```
# Ejecutar todos los tests
pytest tests/ -v

# Ejecutar con cobertura
pytest tests/ --cov=app --cov-report=html

# Prueba interactiva del agente (requiere Ollama corriendo)
python tests/test_agent.py
```

**🐳 Docker**

El proyecto incluye configuración completa para despliegue con Docker, optimizada para equipos con recursos limitados (7GB RAM).

```
# Construir y levantar
docker-compose up --build -d

# Detener servicios
docker-compose down

# Detener y eliminar volúmenes (limpieza total)
docker-compose down -v
```

**🚀 Posibles Mejoras Futuras**

- Soporte para más formatos: DOCX, PPTX, imágenes (OCR).
- Historial de conversaciones: Persistencia en base de datos (PostgreSQL).
- Feedback del usuario: Sistema de rating de respuestas (Thumbs up/down).
- RAG avanzado: Implementar HyDE, re-ranking y multi-query.
- Autenticación: Login de usuarios con roles y permisos.
- Integraciones: Conectar el agente a Slack o Microsoft Teams.

**📄 Licencia**

Este proyecto está licenciado bajo la MIT License. Consulta el archivo LICENSE para más detalles.

## **👥 Autor**

Desarrollado por: Aley Cabrera De la hoz

Email: aley.cabrera@gmail.com

LinkedIn: https://www.linkedin.com/in/aley-cabrera/

GitHub: https://github.com/AleyCabrera

## **🙏 Agradecimientos**
Meta por FAISS.
HuggingFace por sentence-transformers.
Ollama por hacer los LLM accesibles localmente.
LangChain por el framework de orquestación.
Streamlit por la UI rápida y moderna.
- 📅 Última actualización: Julio 2026
- 🏷️ Versión: 1.0.0
- 🤖 Modelo: llama3.2:3b
- 📚 Documentos indexados: 627 chunks

### 📝 Instrucciones finales:
```
1. Crea un archivo llamado `README.md` en la raíz de tu proyecto (`santos-pegasus-agent/README.md`).
2. Copia todo el texto del bloque de código de arriba.
3. Pégalo en tu archivo `README.md`.
4. **Importante:** Crea una carpeta llamada `screenshots` en la raíz y agrega allí las capturas de pantalla de tu aplicación funcionando. Luego actualiza los nombres de las imágenes en la sección "Capturas de Pantalla" del README para que coincidan con tus archivos.
5. Reemplaza `[Tu Nombre]`, `[tu.email@ejemplo.com]` y los enlaces de LinkedIn/GitHub con tu información real.
```