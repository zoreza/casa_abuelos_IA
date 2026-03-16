#!/usr/bin/env python3
"""
🤖 TELEGRAM BOT - Casa Abuelos IA
Bot de Telegram para consultas interactivas sobre La Casa de los Abuelos
Usa polling (sin necesidad de IP pública)
"""

import logging
import sys
import uuid
import time
from pathlib import Path
from datetime import datetime

# Importar telegram
try:
    from telegram import Update, ForceReply
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
except ImportError:
    print("❌ python-telegram-bot no está instalado")
    print("   Instala con: pip3 install --break-system-packages python-telegram-bot")
    sys.exit(1)

# Agregar scripts al path
sys.path.insert(0, str(Path(__file__).parent))

from config import (
    PROMPTS, CONOCIMIENTO_PATH, VERBOSE_MODE, 
    MAX_CONTEXT_MESSAGES, LOGS_PATH
)
from utils import (
    sanitizar_pregunta, verificar_ollama_disponible,
    get_llm_vendedor, get_llm_auditor,
    agregar_al_historial, convertir_historial_lista_a_string,
    limpiar_respuesta, Metricas
)
from database import (
    inicializar_db, guardar_conversacion,
    crear_o_actualizar_lead, obtener_estadisticas_cliente,
    obtener_historial
)
from logger_config import logger

from crewai import Agent, Task, Crew, Process
import json
import os

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════════════════════

# Obtener token desde .env o variable de entorno
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
if not BOT_TOKEN:
    print("❌ TELEGRAM_BOT_TOKEN no configurado en .env")
    print("   Agrega al .env: TELEGRAM_BOT_TOKEN=tu-token-aqui")
    sys.exit(1)

# Logging para Telegram
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler(LOGS_PATH / 'telegram_bot.log'),
        logging.StreamHandler()
    ]
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)

# ═══════════════════════════════════════════════════════════════════════════
# CARGAR DATOS DE CONOCIMIENTO
# ═══════════════════════════════════════════════════════════════════════════

def cargar_json(ruta):
    """Carga un archivo JSON con manejo de errores"""
    try:
        with open(ruta, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error cargando {ruta}: {e}")
        return {}

# Cargar datos
casa_data = cargar_json(CONOCIMIENTO_PATH / "casa_abuelos.json")
disponibilidad = cargar_json(CONOCIMIENTO_PATH / "disponibilidad.json")
politicas = ""
propiedad = ""

ruta_politicas = CONOCIMIENTO_PATH / "politicas.txt"
if ruta_politicas.exists():
    with open(ruta_politicas, 'r', encoding='utf-8') as f:
        politicas = f.read()

ruta_propiedad = CONOCIMIENTO_PATH / "propiedad.txt"
if ruta_propiedad.exists():
    with open(ruta_propiedad, 'r', encoding='utf-8') as f:
        propiedad = f.read()

# ═══════════════════════════════════════════════════════════════════════════
# ESTADO GLOBAL Y AGENTES
# ═══════════════════════════════════════════════════════════════════════════

# Inicializar DB
inicializar_db()

# Verificar Ollama
OLLAMA_DISPONIBLE = verificar_ollama_disponible()

# LLMs
llm_vendedor = get_llm_vendedor()
llm_auditor = get_llm_auditor()

# Convertir datos a strings
casa_abuelos_str = json.dumps(casa_data, indent=2, ensure_ascii=False)
disponibilidad_str = json.dumps(disponibilidad, indent=2, ensure_ascii=False)

# Crear Agentes
agente_concierge = Agent(
    role="Concierge Especializado en Casa de Abuelos",
    goal="Proporcionar atención al cliente excepcional destacando amenidades",
    backstory=PROMPTS["concierge"],
    llm=llm_vendedor,
    verbose=False
)

agente_logistica = Agent(
    role="Especialista en Logística y Disponibilidad",
    goal="Verificar disponibilidad, calcular costos y coordinar reservas",
    backstory=PROMPTS["logistica"],
    llm=llm_vendedor,
    verbose=False
)

agente_auditor = Agent(
    role="Auditor de Calidad",
    goal="Validar respuestas contra datos oficiales de la propiedad",
    backstory=PROMPTS["auditor"],
    llm=llm_auditor,
    verbose=False
)

# Diccionario de historial por usuario (cliente_id -> lista de mensajes)
historial_usuarios = {}
metricas_usuarios = {}

# ═══════════════════════════════════════════════════════════════════════════
# FUNCIONES DE PROCESAMIENTO
# ═══════════════════════════════════════════════════════════════════════════

def procesar_consulta(pregunta: str, usuario_id: str) -> tuple:
    """
    Procesa una consulta a través de los 3 agentes
    Returns: (respuesta_final, tiempo_procesamiento)
    """
    try:
        # Inicializar historial del usuario si no existe
        if usuario_id not in historial_usuarios:
            historial_usuarios[usuario_id] = []
            metricas_usuarios[usuario_id] = Metricas()
        
        # Sanitizar entrada
        pregunta_limpia = sanitizar_pregunta(pregunta)
        if not pregunta_limpia:
            return "❌ Pregunta vacía o inválida", 0
        
        historial_lista = historial_usuarios[usuario_id]
        
        # Agregar al historial
        historial_lista = agregar_al_historial(
            historial_lista, 
            {'rol': 'cliente', 'contenido': pregunta_limpia},
            MAX_CONTEXT_MESSAGES
        )
        historial_usuarios[usuario_id] = historial_lista
        
        # Convertir historial para los agentes
        historial_str = convertir_historial_lista_a_string(historial_lista)
        
        inicio = time.time()
        
        # Crear tareas
        tarea_concierge = Task(
            description="""Eres el Concierge de atención al cliente.
Historial de la conversación:
{historial}

NUEVA CONSULTA DEL CLIENTE: {pregunta}

DATOS DE LA PROPIEDAD:
{propiedad_info}

Responde a las dudas sobre amenidades, servicios o reglas. IGNORA fechas o presupuestos.
Sé directo, cálido pero conciso. Basa tu respuesta ÚNICAMENTE en los datos de la propiedad.""",
            expected_output="Mensaje sobre características de la propiedad, basado en los datos proporcionados",
            agent=agente_concierge,
            output_file=None
        )
        
        tarea_logistica = Task(
            description="""Eres el Especialista en Disponibilidad y Costos.
Historial de la conversación:
{historial}

NUEVA CONSULTA DEL CLIENTE: {pregunta}

INFORMACIÓN DE DISPONIBILIDAD Y TARIFAS:
{disponibilidad_info}

Si hay fechas o meses mencionados, verifica disponibilidad y calcula el costo exacto.
Si NO menciona fechas, responde ÚNICA Y ESTRICTAMENTE: 'NO_APLICA'
Incluye: desglose de noches, costo total, y apartado (1 noche).""",
            expected_output="Desglose matemático (fechas, costo, apartado) o 'NO_APLICA' si no hay fechas",
            agent=agente_logistica,
            output_file=None
        )
        
        tarea_auditor = Task(
            description="""Eres el Auditor Final de Calidad.
Tu función es ensamblarse respuesta final verificando contra los datos.

Recibirás dos respuestas:
1. Del Concierge (sobre amenidades)
2. De Logística (sobre fechas/costos o 'NO_APLICA')

INSTRUCCIONES:
- Si Logística es 'NO_APLICA', ignóralo. Pule solo el Concierge.
- Si Logística tiene información, intégrala fluido al final del Concierge.
- Verifica que no haya información falsa.
- Elimina completamente cualquier mención de 'NO_APLICA' del texto.
- Cero redundancias: Elimina saludos dobles.

Proporciona UN ÚNICO mensaje final cohesionado, directo, veraz y amable para el cliente.""",
            expected_output="Mensaje final cohesionado, sin 'NO_APLICA', directo y veraz",
            agent=agente_auditor,
            context=[tarea_concierge, tarea_logistica]
        )
        
        # Ejecutar crew
        crew = Crew(
            agents=[agente_concierge, agente_logistica, agente_auditor],
            tasks=[tarea_concierge, tarea_logistica, tarea_auditor],
            process=Process.sequential,
            verbose=False
        )
        
        # Inputs
        inputs_cliente = {
            'historial': historial_str,
            'pregunta': pregunta_limpia,
            'propiedad_info': casa_abuelos_str,
            'disponibilidad_info': disponibilidad_str
        }
        
        resultado = crew.kickoff(inputs=inputs_cliente)
        tiempo = time.time() - inicio
        
        # Obtener respuesta
        if hasattr(resultado, 'raw'):
            respuesta_crudo = resultado.raw
        else:
            respuesta_crudo = str(resultado).strip()
        
        respuesta_final = limpiar_respuesta(respuesta_crudo) if respuesta_crudo else "No se pudo procesar la consulta"
        
        # Guardar en BD
        guardar_conversacion(
            usuario_id,
            pregunta_limpia,
            respuesta_final if respuesta_final else respuesta_crudo,
            modelo_usado="ollama/mistral-nemo" if OLLAMA_DISPONIBLE else "gemini-1.5-flash",
            tiempo_respuesta_segundos=tiempo,
            exitosa=True
        )
        
        # Actualizar lead
        crear_o_actualizar_lead(usuario_id, nombre="Usuario Telegram", estado="prospecto")
        
        # Actualizar métricas
        metricas_usuarios[usuario_id].registrar_consulta(tiempo, "exitosa", 
                                   "ollama/mistral-nemo" if OLLAMA_DISPONIBLE else "gemini-1.5-flash")
        
        # Agregar respuesta al historial
        historial_lista = agregar_al_historial(
            historial_lista,
            {'rol': 'agente', 'contenido': respuesta_final[:500]},
            MAX_CONTEXT_MESSAGES
        )
        historial_usuarios[usuario_id] = historial_lista
        
        return respuesta_final, tiempo
        
    except Exception as e:
        logger.error(f"Error procesando consulta del usuario {usuario_id}: {e}")
        return f"❌ Error procesando tu consulta: {str(e)[:100]}", 0

# ═══════════════════════════════════════════════════════════════════════════
# HANDLERS DEL BOT
# ═══════════════════════════════════════════════════════════════════════════

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /start"""
    usuario_id = str(update.effective_user.id)
    user = update.effective_user
    
    mensaje = f"""👋 ¡Hola {user.first_name}!

Bienvenido/a a **Casa de los Abuelos IA**. 

Soya tu asistente virtual para consultas sobre:
✅ Disponibilidad de fechas
✅ Precios y tarifas
✅ Amenidades e información de la propiedad
✅ Políticas de reserva

💡 *Escriba su pregunta* y te daré una respuesta completa en segundos.

📱 Ejemplos:
• ¿Tienen disponible del 20 al 23 de marzo para 6 personas?
• ¿Cuánto cuesta por noche en mayo?
• ¿Aceptan mascotas?"""
    
    await update.message.reply_text(mensaje, parse_mode='Markdown')
    logger.info(f"Usuario {usuario_id} ({user.first_name}) inició sesión")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /help"""
    ayuda = """📖 **GUÍA DE COMANDOS**

/start - Mensaje de bienvenida
/help - Esta guía
/stats - Ver tus estadísticas
/historial - Últimas 5 consultas
/nuevo - Iniciar nueva sesión

💬 *Para hacer una pregunta*, simplemente escríbela sin comandos"""
    
    await update.message.reply_text(ayuda, parse_mode='Markdown')

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /stats - Mostrar estadísticas del usuario"""
    usuario_id = str(update.effective_user.id)
    
    if usuario_id in metricas_usuarios:
        metricas = metricas_usuarios[usuario_id]
        stats_msg = f"""📊 **TUS ESTADÍSTICAS**

Total de consultas: {metricas.total_consultas}
Consultas exitosas: {metricas.consultas_correctas}
Errores: {metricas.consultas_error}
Tiempo promedio: {metricas.tiempo_promedio():.2f}s
Tasa de éxito: {metricas.tasa_exito():.1f}%"""
    else:
        stats_msg = "📊 Aún no has hecho ninguna consulta."
    
    await update.message.reply_text(stats_msg, parse_mode='Markdown')

async def historial_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /historial - Mostrar historial de consultas"""
    usuario_id = str(update.effective_user.id)
    
    try:
        historial = obtener_historial(usuario_id, limit=5)
        
        if not historial:
            await update.message.reply_text("📝 Aún no hay consultas en tu historial")
            return
        
        msg = "📝 **HISTORIAL (Últimas 5)**\n\n"
        for i, item in enumerate(historial, 1):
            pregunta = item.get('pregunta', '')[:50] + "..." if len(item.get('pregunta', '')) > 50 else item.get('pregunta', '')
            timestamp = item.get('timestamp', '')
            msg += f"{i}. {pregunta}\n   ⏰ {timestamp}\n\n"
        
        await update.message.reply_text(msg, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error al obtener historial: {e}")
        await update.message.reply_text(f"❌ Error al obtener historial: {str(e)[:100]}")

async def nuevo_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /nuevo - Iniciar nueva sesión"""
    usuario_id = str(update.effective_user.id)
    
    historial_usuarios[usuario_id] = []
    metricas_usuarios[usuario_id] = Metricas()
    
    await update.message.reply_text("✅ Nueva sesión iniciada. Historial limpio.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja mensajes de texto (consultas del usuario)"""
    usuario_id = str(update.effective_user.id)
    pregunta = update.message.text
    
    # Mostrar indicador de "escribiendo"
    await update.message.chat.send_action("typing")
    
    # Enviar mensaje de procesamiento
    msg_procesando = await update.message.reply_text("⏳ Procesando tu consulta...")
    
    # Procesar consulta
    respuesta, tiempo = procesar_consulta(pregunta, usuario_id)
    
    # Editar mensaje con la respuesta
    try:
        await msg_procesando.edit_text(
            f"🤖 **Respuesta** (⏱️ {tiempo:.1f}s)\n\n{respuesta}",
            parse_mode='Markdown'
        )
    except Exception as e:
        # Si la respuesta es muy larga, dividir
        logger.warning(f"Respuesta muy larga, dividiendo: {e}")
        
        # Enviar respuesta en chunks
        max_len = 4096
        for i in range(0, len(respuesta), max_len):
            chunk = respuesta[i:i+max_len]
            if i == 0:
                await msg_procesando.edit_text(chunk, parse_mode='Markdown')
            else:
                await update.message.reply_text(chunk, parse_mode='Markdown')
    
    logger.info(f"Usuario {usuario_id}: '{pregunta[:50]}...' → Respuesta en {tiempo:.2f}s")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja errores"""
    logger.error(f"Error: {context.error}", exc_info=context.error)
    if update and update.message:
        await update.message.reply_text(f"❌ Error: {str(context.error)[:100]}")

# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

def main():
    """Inicia el bot (no async)"""
    print("\n" + "="*80)
    print("🤖 TELEGRAM BOT - CASA ABUELOS IA")
    print("="*80)
    print(f"\n📡 Estado Ollama: {'✅ Disponible' if OLLAMA_DISPONIBLE else '⚠️ No disponible (usará Gemini)'}")
    print(f"✅ Base de datos inicializada")
    print(f"✅ Agentes configurados")
    print(f"\n🚀 Iniciando bot con polling...")
    print(f"📍 Modo: Polling (sin necesidad de IP pública)")
    print(f"⏸️  Presiona Ctrl+C para detener\n")
    
    # Crear application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Agregar handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("historial", historial_command))
    application.add_handler(CommandHandler("nuevo", nuevo_command))
    
    # Handler para mensajes de texto
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Handler de errores
    application.add_error_handler(error_handler)
    
    # Iniciar bot (sin asyncio.run() para evitar conflictos de event loop)
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Bot detenido por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
        sys.exit(1)
