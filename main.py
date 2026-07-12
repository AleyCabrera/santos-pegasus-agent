"""Punto de entrada para FastAPI"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.config import settings
from app.utils.logger import logger

# Crear app FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Agente RAG para Santos Pegasus Soluciones",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(router)

# Endpoint raíz
@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": f"Bienvenido a {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/api/v1/health"
    }

# Eventos de inicio/apagado
@app.on_event("startup")
async def startup_event():
    """Evento de inicio"""
    logger.info("🚀 Iniciando Santos Pegasus Soluciones RAG Agent")
    logger.info(f"📚 Configuración: {settings.model_dump()}")

@app.on_event("shutdown")
async def shutdown_event():
    """Evento de apagado"""
    logger.info("👋 Apagando Santos Pegasus Soluciones RAG Agent")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )