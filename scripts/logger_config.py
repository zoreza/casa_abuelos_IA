"""
Configuración de logging estructurado
"""

import logging
import json
from logging.handlers import RotatingFileHandler
from datetime import datetime
from pathlib import Path
from config import LOG_LEVEL, LOG_FILE, VERBOSE_MODE

# Crear directorio de logs si no existe
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

# ============================================
# SETUPEAR LOGGER PRINCIPAL
# ============================================

logger = logging.getLogger('oficina_abuelos')
logger.setLevel(getattr(logging, LOG_LEVEL))

# Formato detallado
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Handler para archivo con rotación
file_handler = RotatingFileHandler(
    LOG_FILE,
    maxBytes=5_000_000,  # 5 MB
    backupCount=5,
    encoding='utf-8'
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Handler para consola (si VERBOSE_MODE activo)
if VERBOSE_MODE:
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

# ============================================
# FUNCIONES DE LOGGING ESPECÍFICAS
# ============================================

def log_consulta(cliente_id: str, pregunta: str, respuesta: str, tiempo_segundos: float):
    """Registra una consulta procesada"""
    logger.info(f"[CONSULTA] Cliente: {cliente_id} | Tiempo: {tiempo_segundos:.2f}s")
    if VERBOSE_MODE:
        logger.debug(f"Pregunta: {pregunta}")
        logger.debug(f"Respuesta: {respuesta[:200]}...")


def log_error(error_type: str, mensaje: str, cliente_id: str = "desconocido"):
    """Registra un error"""
    logger.error(f"[{error_type}] Cliente: {cliente_id} | {mensaje}")


def log_fallback(modelo_fallido: str, modelo_nuevo: str):
    """Registra un fallback a modelo alternativo"""
    logger.warning(f"[FALLBACK] {modelo_fallido} no disponible, usando {modelo_nuevo}")


def log_evento(evento: str, detalles: dict = None):
    """Registra un evento general"""
    if detalles:
        logger.info(f"[EVENTO] {evento} | Detalles: {json.dumps(detalles, ensure_ascii=False)}")
    else:
        logger.info(f"[EVENTO] {evento}")


def log_metricas(metricas_dict: dict):
    """Registra resumen de métricas"""
    logger.info(f"[MÉTRICAS] {json.dumps(metricas_dict, ensure_ascii=False)}")


def log_inicio_sesion():
    """Registra inicio de sesión"""
    logger.info("="*60)
    logger.info("🤖 SERVIDOR DE LA CASA DE LOS ABUELOS INICIADO")
    logger.info("="*60)


def log_cierre_sesion(metricas_dict: dict = None):
    """Registra cierre de sesión"""
    logger.info("="*60)
    logger.info("🔌 SERVIDOR APAGADO")
    if metricas_dict:
        logger.info(f"Métricas finales: {json.dumps(metricas_dict, ensure_ascii=False)}")
    logger.info("="*60)


# ============================================
# LOGGER PARA AUDITORÍA (Separado)
# ============================================

logger_auditoria = logging.getLogger('auditoria')
logger_auditoria.setLevel(logging.INFO)

auditoria_handler = RotatingFileHandler(
    LOG_FILE.parent / 'auditoria.log',
    maxBytes=5_000_000,
    backupCount=5,
    encoding='utf-8'
)

auditoria_formatter = logging.Formatter(
    '%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
auditoria_handler.setFormatter(auditoria_formatter)
logger_auditoria.addHandler(auditoria_handler)


def log_auditoria_error(cliente_id: str, tipo_error: str, detalles: str):
    """Registra errores en log de auditoría"""
    logger_auditoria.warning(f"ERROR | Cliente: {cliente_id} | Tipo: {tipo_error} | {detalles}")


def log_auditoria_alucinacion(cliente_id: str, contenido_sospechoso: str):
    """Registra posibles alucinaciones detectadas"""
    logger_auditoria.warning(f"ALUCINACIÓN | Cliente: {cliente_id} | Contenido: {contenido_sospechoso[:100]}")


# ============================================
# VERIFICACIÓN
# ============================================

if __name__ == "__main__":
    logger.info("✅ Sistema de logging configurado correctamente")
    print(f"📁 Archivo de log: {LOG_FILE}")
