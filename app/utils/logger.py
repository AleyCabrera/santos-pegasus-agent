import sys
from loguru import logger
from app.config import settings

def setup_logger():
    """Configura el logger de la aplicación"""
    
    # Remover handlers por defecto
    logger.remove()
    
    # Configurar formato
    format_string = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
    
    # Handler para consola
    logger.add(
        sys.stdout,
        format=format_string,
        level=settings.LOG_LEVEL,
        colorize=True
    )
    
    # Handler para archivo (opcional)
    logger.add(
        "logs/app.log",
        format=format_string,
        level=settings.LOG_LEVEL,
        rotation="500 MB",
        retention="10 days",
        compression="zip"
    )
    
    return logger

# Logger global
logger = setup_logger()