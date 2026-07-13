# ============================================================
# DOCKERFILE - Santos Pegasus RAG Agent
# Optimizado para 7GB RAM
# ============================================================

# Usar Python 3.12 slim para reducir tamaño de imagen
FROM python:3.12-slim

# Crear directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Crear directorios necesarios
RUN mkdir -p data/pdfs data/csv vectorstore logs

# Exponer puertos
EXPOSE 8501 8000

# Health check para la app
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "app/ui/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
