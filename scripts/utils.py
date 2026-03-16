"""
Utilidades compartidas: sanitización, validación, fallback, etc.
"""

import re
import requests
from datetime import datetime, date, timedelta
from typing import Optional, Tuple
from config import (
    OLLAMA_BASE_URL, OLLAMA_TIMEOUT_SECONDS, 
    OLLAMA_MODEL, GEMINI_MODEL, GOOGLE_API_KEY,
    VERBOSE_MODE, CAPACIDAD_MAXIMA, MINIMO_NOCHES,
    LLM_TEMPERATURE_VENDEDOR, LLM_TEMPERATURE_AUDITOR,
    LLM_NUM_CTX
)
# crewai is imported lazily inside get_llm_* functions to allow importing
# this module without requiring crewai (e.g. for unit tests or mock mode).

# ============================================
# SANITIZACIÓN DE ENTRADAS
# ============================================

def sanitizar_pregunta(pregunta: str, max_length: int = 500) -> str:
    """
    Sanitiza la pregunta del usuario:
    - Limpia espacios en blanco
    - Limita longitud
    - Remueve caracteres de control
    - Previene inyección de prompts
    """
    # Eliminar espacios en blanco al inicio y final
    pregunta = pregunta.strip()
    
    # Limitar longitud
    if len(pregunta) > max_length:
        pregunta = pregunta[:max_length]
    
    # Remover caracteres de control y caracteres especiales peligrosos
    pregunta = re.sub(r'[\x00-\x1f\x7f]', '', pregunta)
    
    # Prevenir inyección de prompts básica (búsqueda de patrones sospechosos)
    patrones_sospechosos = [
        r'ignore.*instruction',
        r'olvida.*tu.*rol',
        r'cambia.*de.*rol',
    ]
    
    for patron in patrones_sospechosos:
        if re.search(patron, pregunta, re.IGNORECASE):
            if VERBOSE_MODE:
                print(f"⚠️  Posible inyección de prompt detectada")
            # No bloquear, pero avisar
    
    return pregunta


# ============================================
# VALIDACIÓN DE FECHAS
# ============================================

def validar_fechas(fecha_inicio_str: str, fecha_fin_str: str) -> Tuple[bool, str]:
    """
    Valida fechas para una reserva.
    Retorna (es_válido, mensaje_error)
    """
    try:
        # Parsear fechas
        fecha_inicio = datetime.strptime(fecha_inicio_str, "%Y-%m-%d").date()
        fecha_fin = datetime.strptime(fecha_fin_str, "%Y-%m-%d").date()
        
        # Validar que fecha_inicio sea antes que fecha_fin
        if fecha_inicio >= fecha_fin:
            return False, "La fecha de inicio debe ser anterior a la fecha de fin"
        
        # Validar que no sean fechas pasadas
        hoy = date.today()
        if fecha_fin < hoy:
            return False, "Las fechas no pueden ser en el pasado"
        
        # Validar número mínimo de noches
        dias = (fecha_fin - fecha_inicio).days
        if dias < MINIMO_NOCHES:
            return False, f"Mínimo {MINIMO_NOCHES} noches requeridas. Usted solicita {dias} noches"
        
        return True, "OK"
    
    except ValueError as e:
        return False, f"Formato de fecha inválido. Use YYYY-MM-DD: {str(e)}"


# ============================================
# FALLBACK INTELIGENTE DE LLM
# ============================================

def verificar_ollama_disponible() -> bool:
    """
    Verifica si Ollama está disponible en la red local
    """
    try:
        response = requests.get(
            f"{OLLAMA_BASE_URL}/api/tags",
            timeout=OLLAMA_TIMEOUT_SECONDS
        )
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def get_llm_vendedor():
    """
    Retorna el LLM para vendedor/concierge con fallback automático
    """
    from crewai import LLM
    if verificar_ollama_disponible():
        if VERBOSE_MODE:
            print("✅ Usando Ollama (local) para vendedor")
        return LLM(
            model=f"ollama/{OLLAMA_MODEL}",
            base_url=OLLAMA_BASE_URL,
            temperature=LLM_TEMPERATURE_VENDEDOR,
            config={"num_ctx": LLM_NUM_CTX}
        )
    else:
        if VERBOSE_MODE:
            print("⚠️  Ollama no disponible, fallback a Google Gemini para vendedor")
        return LLM(
            model=GEMINI_MODEL,
            api_key=GOOGLE_API_KEY,
            temperature=LLM_TEMPERATURE_VENDEDOR
        )


def get_llm_auditor():
    """
    Retorna el LLM para auditor con fallback automático
    """
    from crewai import LLM
    if verificar_ollama_disponible():
        if VERBOSE_MODE:
            print("✅ Usando Ollama (local) para auditor")
        return LLM(
            model=f"ollama/{OLLAMA_MODEL}",
            base_url=OLLAMA_BASE_URL,
            temperature=LLM_TEMPERATURE_AUDITOR,
            config={"num_ctx": LLM_NUM_CTX}
        )
    else:
        if VERBOSE_MODE:
            print("⚠️  Ollama no disponible, fallback a Google Gemini para auditor")
        return LLM(
            model=GEMINI_MODEL,
            api_key=GOOGLE_API_KEY,
            temperature=LLM_TEMPERATURE_AUDITOR
        )


# ============================================
# GESTIÓN DE HISTORIAL
# ============================================

def agregar_al_historial(historial_list: list, nuevo_mensaje: dict, max_msgs: int = None) -> list:
    """
    Agrega un nuevo mensaje al historial manteniendo un máximo de mensajes.
    
    Args:
        historial_list: Lista actual de mensajes
        nuevo_mensaje: {'rol': 'cliente|bot', 'contenido': 'texto'}
        max_msgs: Número máximo de mensajes a mantener
    
    Returns:
        Lista actualizada de mensajes
    """
    from config import MAX_CONTEXT_MESSAGES
    
    if max_msgs is None:
        max_msgs = MAX_CONTEXT_MESSAGES
    
    historial_list.append(nuevo_mensaje)
    
    # Mantener solo los últimos N mensajes
    if len(historial_list) > max_msgs:
        historial_list = historial_list[-max_msgs:]
    
    return historial_list


def convertir_historial_lista_a_string(historial_list: list) -> str:
    """
    Convierte lista de mensajes a string formateado para pasar a los agentes
    """
    resultado = ""
    for msg in historial_list:
        rol = msg.get('rol', 'Desconocido')
        contenido = msg.get('contenido', '')
        resultado += f"{rol}: {contenido}\n"
    
    return resultado.strip()


# ============================================
# CONVERSIÓN DE FORMATOS
# ============================================

def extraer_fechas_de_texto(texto: str) -> list:
    """
    Intenta extraer fechas en formato YYYY-MM-DD del texto
    """
    patron = r'\d{4}-\d{2}-\d{2}'
    fechas = re.findall(patron, texto)
    return fechas


def limpiar_respuesta(respuesta: str) -> str:
    """
    Limpia la respuesta del bot:
    - Elimina "NO_APLICA" del texto
    - Remueve espacios dobles
    - Trimea espacios al inicio/final
    """
    # Eliminar "NO_APLICA" y variaciones
    respuesta = re.sub(r'\b[Nn][Oo]_[Aa][Pp][Ll][Ii][Cc][Aa]\b\.?', '', respuesta)
    
    # Eliminar espacios múltiples
    respuesta = re.sub(r'\s+', ' ', respuesta)
    
    # Trim
    respuesta = respuesta.strip()
    
    return respuesta


# ============================================
# MÉTRICAS Y CONTADORES
# ============================================

class Metricas:
    """Clase para rastrear métricas de uso"""
    
    def __init__(self):
        self.total_consultas = 0
        self.consultas_correctas = 0
        self.consultas_error = 0
        self.tiempos_respuesta = []
        self.modelos_usados = {"ollama": 0, "gemini": 0}
        self.fecha_inicio = datetime.now()
    
    def registrar_consulta(self, tiempo_respuesta: float, modelo_usado: str, exitosa: bool = True):
        """Registra una consulta procesada"""
        self.total_consultas += 1
        self.tiempos_respuesta.append(tiempo_respuesta)
        
        if modelo_usado.lower() == "ollama":
            self.modelos_usados["ollama"] += 1
        else:
            self.modelos_usados["gemini"] += 1
        
        if exitosa:
            self.consultas_correctas += 1
        else:
            self.consultas_error += 1
    
    def tiempo_promedio(self) -> float:
        """Calcula tiempo promedio de respuesta"""
        if not self.tiempos_respuesta:
            return 0
        return sum(self.tiempos_respuesta) / len(self.tiempos_respuesta)
    
    def tasa_exito(self) -> float:
        """Calcula tasa de éxito"""
        if self.total_consultas == 0:
            return 0
        return (self.consultas_correctas / self.total_consultas) * 100
    
    def obtener_resumen(self) -> dict:
        """Retorna resumen de métricas"""
        return {
            "total_consultas": self.total_consultas,
            "consultas_correctas": self.consultas_correctas,
            "consultas_error": self.consultas_error,
            "tiempo_promedio_respuesta": round(self.tiempo_promedio(), 2),
            "tasa_exito_porcentaje": round(self.tasa_exito(), 2),
            "modelos_usados": self.modelos_usados,
            "tiempo_ejecucion_total_minutos": round(
                (datetime.now() - self.fecha_inicio).total_seconds() / 60, 2
            )
        }


# ============================================
# VERIFICACIÓN DE SEGURIDAD
# ============================================

def verificar_seguridad():
    """
    Verifica que no haya API keys hardcodeadas en archivos de scripts
    """
    import os
    from pathlib import Path
    
    archivos_a_revisar = [
        "debug_ia.py",
        "bunker_2026.py",
        "list_models.py",
        "oficina_v2.py"
    ]
    
    scripts_path = Path(__file__).parent
    
    for archivo in archivos_a_revisar:
        ruta = scripts_path / archivo
        if ruta.exists():
            with open(ruta, 'r', encoding='utf-8') as f:
                contenido = f.read()
                if 'AIzaSy' in contenido or 'api_key=' in contenido:
                    print(f"⚠️  ALERTA SEGURIDAD: {archivo} contiene posibles API keys")
    
    print("✅ Verificación de seguridad completada")
