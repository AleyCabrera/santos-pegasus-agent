# 🤖 Santos Pegasus Soluciones - Agente IA RAG

## 📋 Introducción

Agente conversacional inteligente con arquitectura RAG (Retrieval Augmented Generation) para responder preguntas sobre la documentación interna de Santos Pegasus Soluciones.

## 🎯 Problema de Negocio

Santos Pegasus Soluciones necesita un asistente virtual que pueda responder preguntas sobre:
- Manual de onboarding para nuevos empleados
- Guías de ingeniería (back-end y front-end)
- Protocolos de incidentes y escalamiento
- Arquitectura de microservicios

## 🏗️ Arquitectura

Usuario → Streamlit → Agente LangChain → FAISS (Vector DB) → Ollama (LLM)
↑
Documentos PDF/CSV/MD


## 🛠️ Tecnologías

- **Frontend**: Streamlit (Open Source)
- **Backend**: FastAPI + Python 3.12
- **Orquestación**: LangChain
- **LLM**: Ollama (llama3.2:3b, local)
- **Embeddings**: Sentence-Transformers (local)
- **Vector DB**: FAISS (local)
- **Contenerización**: Docker
- **Deploy**: OCI Free Tier

## 📁 Estructura

santos-pegasus-agent/
├── app/
│ ├── api/ # Endpoints FastAPI
│ ├── agents/ # Definición del agente
│ ├── chains/ # Cadenas RAG
│ ├── prompts/ # Plantillas de prompts
│ ├── services/ # Lógica de negocio
│ ├── loaders/ # Carga de documentos
│ ├── models/ # Esquemas Pydantic
│ └── utils/ # Funciones auxiliares
├── data/ # Documentos fuente
├── vectorstore/ # Índice FAISS persistido
├── tests/ # Tests unitarios
├── screenshots/ # Evidencia visual
└── docker-compose.yml


## 🔧 Instalación

### Requisitos Previos
- Python 3.12+
- Ollama instalado localmente
- Git

### Pasos

1. Clonar repositorio
```bash
git clone https://github.com/tu-usuario/santos-pegasus-agent.git
cd santos-pegasus-agent

Crear entorno virtual

bash
python -m venv venv
source venv/bin/activate  # o venv\Scripts\activate en Windows
Instalar dependencias

bash
pip install -r requirements.txt
Configurar variables de entorno

bash
cp .env.example .env
# Editar .env con tus configuraciones
Descargar modelo Ollama

bash
ollama pull llama3.2:3b
🚀 Ejecución
Local
bash
# Levantar la aplicación
streamlit run app/ui/app.py
Con Docker
bash
docker-compose up --build
