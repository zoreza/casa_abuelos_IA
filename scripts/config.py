"""
Configuración centralizada del proyecto
Carga variables desde .env y proporciona valores por defecto
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar .env desde la raíz del proyecto
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# ============================================
# RUTAS
# ============================================
BASE_PATH = Path(__file__).parent.parent
SCRIPTS_PATH = BASE_PATH / 'scripts'
CONOCIMIENTO_PATH = BASE_PATH / 'conocimiento'
LOGS_PATH = BASE_PATH / 'logs'
LEADS_PATH = BASE_PATH / 'leads'
SALIDAS_PATH = BASE_PATH / 'salidas'

# Crear directorios si no existen
LOGS_PATH.mkdir(exist_ok=True)
LEADS_PATH.mkdir(exist_ok=True)
SALIDAS_PATH.mkdir(exist_ok=True)

# ============================================
# API KEYS Y CONEXIONES
# ============================================
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')
if not GOOGLE_API_KEY:
    import warnings
    warnings.warn("⚠️  GOOGLE_API_KEY no configurada en .env")

OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')

# ============================================
# MODELOS LLM
# ============================================
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'mistral-nemo')
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')

# ============================================
# PARÁMETROS LLM
# ============================================
LLM_TEMPERATURE_VENDEDOR = float(os.getenv('LLM_TEMPERATURE_VENDEDOR', '0.7'))
LLM_TEMPERATURE_AUDITOR = float(os.getenv('LLM_TEMPERATURE_AUDITOR', '0.1'))
LLM_NUM_CTX = int(os.getenv('LLM_NUM_CTX', '4096'))

# ============================================
# HISTORIAL Y MEMORY
# ============================================
MAX_CONTEXT_MESSAGES = int(os.getenv('MAX_CONTEXT_MESSAGES', '10'))
MAX_HISTORIAL_LENGTH = int(os.getenv('MAX_HISTORIAL_LENGTH', '5000'))

# ============================================
# DATABASE
# ============================================
DATABASE_PATH = LOGS_PATH / os.getenv('DATABASE_PATH', 'chats.db')

# ============================================
# LOGGING
# ============================================
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_DIR = LOGS_PATH
LOG_FILE = LOG_DIR / os.getenv('LOG_FILE', 'oficina.log')

# ============================================
# TIMEOUTS
# ============================================
OLLAMA_TIMEOUT_SECONDS = int(os.getenv('OLLAMA_TIMEOUT_SECONDS', '10'))
GOOGLE_TIMEOUT_SECONDS = int(os.getenv('GOOGLE_TIMEOUT_SECONDS', '30'))

# ============================================
# REGLAS DE NEGOCIO
# ============================================
CAPACIDAD_MAXIMA = int(os.getenv('CAPACIDAD_MAXIMA', '11'))
MINIMO_NOCHES = int(os.getenv('MINIMO_NOCHES', '2'))
TARIFA_TEMPORADA_BAJA = float(os.getenv('TARIFA_TEMPORADA_BAJA', '3500'))
TARIFA_TEMPORADA_ALTA = float(os.getenv('TARIFA_TEMPORADA_ALTA', '4500'))

# ============================================
# DEBUG Y METRICS
# ============================================
VERBOSE_MODE = os.getenv('VERBOSE_MODE', 'True').lower() == 'true'
ENABLE_METRICS = os.getenv('ENABLE_METRICS', 'True').lower() == 'true'

# ============================================
# PROMPTS (Centralizados)
# ============================================
PROMPTS = {
    "concierge": """Eres el Concierge y primer punto de contacto de 'La Casa de los Abuelos' en Punta Pérula.
Tienes dos misiones principales:
1. Prospectos: Entusiasmar a los clientes potenciales destacando nuestras amenidades (Starlink de 200MB/s, A/C en las habitaciones y cercanía a la playa).
2. Huéspedes: Brindar soporte rápido sobre logística, accesos y reglas durante su estancia.

REGLAS ESTRICTAS E INQUEBRANTABLES:
- TU ÚNICA FUENTE DE VERDAD ES EL JSON DE PROPIEDADES
- CERO ALUCINACIONES: Prohibido inventar características que no estén en el JSON
- PROTOCOLO DE INCERTIDUMBRE: Si pregunta algo no documentado, responde: 'No tengo esa información disponible en este momento, lo consulto con Mario o Elia y regreso con usted'
- LÍMITE DE ROL (FECHAS Y COSTOS): PROHIBIDO hablar de disponibilidad o hacer cotizaciones. Di: 'En un momento nuestro especialista de logística le confirmará los espacios libres'
- TONO: Cálido, profesional, servicial y claro.""",

    "logistica": """Eres el Especialista de Disponibilidad, Cotización y Logística para 'La Casa de los Abuelos'.
Tu objetivo es interpretar solicitudes de fechas, verificar disponibilidad y calcular costos.

REGLAS DE NEGOCIO ESTRICTAS:
1. CAPACIDAD: Máximo 11 personas en total.
2. ESTANCIA MÍNIMA: 2 noches obligatorias.
3. TARIFAS: Verifica 'temporada_alta_rangos'. Si ALGUNA fecha cae en rango de temporada alta, aplica $4,500 MXN/noche. Si NO, aplica $3,500 MXN/noche.
4. CÁLCULO: (Número de noches) x (Tarifa) = Costo Total. Apartado = 1 noche.

INSTRUCCIONES:
- DISPONIBILIDAD: Verifica 'fechas_no_disponibles'. Si hay conflicto, ofrece fechas cercanas disponibles.
- ÉXITO: Desglosa noches, costo total y apartado.
- FUERA DE DOMINIO: Si NO hay preguntas sobre fechas, responde ÚNICA Y ESTRICTAMENTE: 'NO_APLICA'""",

    "auditor": """Eres el Auditor Final de Calidad (QA) y Veracidad para 'La Casa de los Abuelos'.
Tu función es validar respuestas contra el Baseline oficial de propiedades.

REGLAS DE VALIDACIÓN CRÍTICA (Tolerancia Cero):
1. ALUCINACIONES: La propiedad está a 12 min caminando de la playa. NO tiene vista al mar. Reescribe si es necesario.
2. AMENIDADES: Confirma: No se prometen toallas, internet es 'Starlink', mascotas SOLO exterior.
3. FINANCIERA: PROHIBIDO descuentos o alteraciones en costos.
4. RUIDO DEL SISTEMA: Elimina completamente la palabra 'NO_APLICA' si aparece.
5. TONO: Elimina adjetivos exagerados ('majestuoso', 'paraíso'). Mantén calor con hechos comprobables.

Tu respuesta final: Devuelve la información CORREGIDA y APROBADA, lista para el cliente. Si algo viene de los agentes anteriores, mejóralo pero mantén la esencia del mensaje."""
}

# ============================================
# INFORMACIÓN DE VERIFICACIÓN
# ============================================
print("✅ Configuración cargada desde:", env_path if env_path.exists() else "valores por defecto")
print(f"📁 Base path: {BASE_PATH}")
print(f"📁 Database: {DATABASE_PATH}")
