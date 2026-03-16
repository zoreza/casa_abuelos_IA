"""
OFICINA ABUELOS v2.0 - Refactorizada y Optimizada
Sistema multiagente para gestión de reservas y atención al cliente
Con seguridad mejorada, persistencia, logging y métricas
"""

import os
import json
import time
import uuid
from datetime import datetime
from pathlib import Path

# Importar módulos locales
from config import (
    CONOCIMIENTO_PATH, PROMPTS, VERBOSE_MODE,
    MAX_CONTEXT_MESSAGES, MAX_HISTORIAL_LENGTH,
    CAPACIDAD_MAXIMA, MINIMO_NOCHES
)
from utils import (
    sanitizar_pregunta, validar_fechas, get_llm_vendedor, get_llm_auditor,
    agregar_al_historial, convertir_historial_lista_a_string, limpiar_respuesta,
    Metricas, verificar_seguridad
)
from database import (
    guardar_conversacion, obtener_historial, crear_o_actualizar_lead,
    guardar_reserva, guardar_metricas
)
from logger_config import logger, log_consulta, log_error, log_evento, log_inicio_sesion, log_cierre_sesion

from crewai import Agent, Task, Crew, Process

# ============================================
# UTILIDADES DE CARGA
# ============================================

def cargar_json(nombre_archivo: str) -> str:
    """
    Carga un archivo JSON del directorio 'conocimiento'
    Retorna como string formateado
    """
    ruta = CONOCIMIENTO_PATH / nombre_archivo
    try:
        with open(ruta, 'r', encoding='utf-8') as f:
            datos = json.load(f)
            return json.dumps(datos, indent=2, ensure_ascii=False)
    except FileNotFoundError:
        logger.error(f"❌ Archivo no encontrado: {ruta}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"❌ Error al parsear JSON {nombre_archivo}: {e}")
        raise


# ============================================
# CARGA DE CONOCIMIENTO BASE
# ============================================

print("📚 Cargando base de conocimiento...")
info_casa = cargar_json('casa_abuelos.json')
info_calendario = cargar_json('disponibilidad.json')
print("✅ Base de conocimiento cargada")

# ============================================
# CONFIGURACIÓN DE AGENTES CON LLM INTELIGENTE
# ============================================

print("🤖 Inicializando agentes...")

# Obtener LLMs con fallback automático
llm_vendedor = get_llm_vendedor()
llm_auditor = get_llm_auditor()

# Configurar fecha actual
fecha_actual = datetime.now().strftime("%Y-%m-%d")

# Backstory del Concierge
prompt_backstory_concierge = f"""
Eres el Concierge y primer punto de contacto de 'La Casa de los Abuelos' en Punta Pérula.
Tienes dos misiones principales:
1. Prospectos: Entusiasmar a los clientes potenciales destacando nuestras amenidades (Starlink de 200MB/s, A/C en las habitaciones y cercanía a la playa).
2. Huéspedes: Brindar soporte rápido sobre logística, accesos y reglas durante su estancia.

REGLAS ESTRICTAS E INQUEBRANTABLES:
- TU ÚNICA FUENTE DE VERDAD ES ESTE JSON: {info_casa}
- CERO ALUCINACIONES: Tienes estrictamente prohibido inventar características, vistas, servicios o amenidades que no estén en el JSON.
- PROTOCOLO DE INCERTIDUMBRE: Si el cliente pregunta algo NO documentado en el JSON, responde: 'No tengo esa información disponible en este momento, lo consulto con Mario o Elia y regreso con usted'.
- LÍMITE DE ROL (FECHAS Y COSTOS): PROHIBIDO hablar de fechas disponibles o hacer cotizaciones. Responde: 'En un momento nuestro especialista de logística le confirmará los espacios libres'.
- TONO: Cálido, profesional, servicial y claro.
"""

concierge = Agent(
    role='Concierge de Ventas',
    goal='Atender dudas y entusiasmar al cliente ÚNICAMENTE con las amenidades y reglas.',
    backstory=prompt_backstory_concierge,
    llm=llm_vendedor,
    verbose=VERBOSE_MODE
)

# Backstory del Especialista de Logística
prompt_backstory_logistica = f"""
Eres el Especialista de Disponibilidad, Cotización y Logística para 'La Casa de los Abuelos'.
Tu objetivo es interpretar solicitudes de fechas, verificar disponibilidad y calcular costos.

FECHA ACTUAL: {fecha_actual}

REGLAS DE NEGOCIO ESTRICTAS:
1. CAPACIDAD: Máximo {CAPACIDAD_MAXIMA} personas.
2. ESTANCIA MÍNIMA: {MINIMO_NOCHES} noches obligatorias.
3. TARIFAS: Verifica 'temporada_alta_rangos' en el calendario. Si ALGUNA fecha cae en esos rangos, aplica $4,500 MXN/noche. Si NO, aplica $3,500 MXN/noche.
4. CÁLCULO: (Número de noches) x (Tarifa) = Costo Total. Apartado = 1 noche.

INSTRUCCIONES:
- DISPONIBILIDAD: Verifica calendario: {info_calendario}. Si hay conflicto en 'fechas_no_disponibles', ofrece fechas cercanas libres.
- ÉXITO: Desglosa noches, costo total y apartado.
- FUERA DE DOMINIO: Si NO hay preguntas sobre fechas, responde ÚNICA Y ESTRICTAMENTE: 'NO_APLICA'
"""

especialista_cal = Agent(
    role='Especialista de Disponibilidad, Cotización y Logística',
    goal='Interpretar fechas, validar calendario sin errores y calcular cotizaciones exactas.',
    backstory=prompt_backstory_logistica,
    llm=llm_vendedor,
    verbose=VERBOSE_MODE
)

# Backstory del Auditor QA
prompt_auditor = f"""
Eres el Auditor Final de Calidad (QA) y Veracidad para 'La Casa de los Abuelos'.
Tu función es validar respuestas contra el Baseline oficial.

BASELINE DE VERDAD:
{info_casa}

REGLAS DE VALIDACIÓN CRÍTICA (Tolerancia Cero):
1. ALUCINACIONES: La propiedad está a 12 min caminando de la playa. NO tiene vista al mar. Reescribe si es necesario.
2. AMENIDADES: Confirma: No se prometen toallas, internet es 'Starlink', mascotas SOLO exterior.
3. FINANCIERA: PROHIBIDO descuentos o alteraciones en costos.
4. RUIDO DEL SISTEMA: Elimina completamente la palabra 'NO_APLICA' si aparece.
5. TONO: Elimina adjetivos exagerados. Mantén cálido con hechos comprobables.

Tu única respuesta: MENSAJE FINAL CORREGIDO Y APROBADO para el cliente.
"""

auditor_qa = Agent(
    role='Auditor de Veracidad y Regresión (QA)',
    goal='Validar cada respuesta contra el JSON y limpiar variables de sistema.',
    backstory=prompt_auditor,
    llm=llm_auditor,
    verbose=VERBOSE_MODE
)

print("✅ Agentes configurados")

# ============================================
# DEFINICIÓN DE TASKS
# ============================================

task_atencion = Task(
    description="""Historial de la conversación:
    {historial}
    
    Analiza la NUEVA consulta del cliente: '{pregunta}'. 
    Responde a las dudas sobre amenidades, servicios o reglas. IGNORA fechas o presupuestos. Sé directo y ve al grano.""",
    expected_output="Mensaje cálido pero conciso sobre características, basado estrictamente en el JSON. Cero fechas o precios.",
    agent=concierge
)

task_calendario = Task(
    description="""Historial de la conversación:
    {historial}
    
    Analiza la NUEVA consulta del cliente: '{pregunta}'. 
    Si hay fechas o meses, verifica disponibilidad y calcula costo exacto. Si NO menciona fechas, responde ÚNICA Y ESTRICTAMENTE: 'NO_APLICA'""",
    expected_output="Desglose matemático de la reserva (fechas, costo total, apartado), o la palabra 'NO_APLICA'. Sin saludos.",
    agent=especialista_cal
)

task_auditoria = Task(
    description="""Recibirás la respuesta del Concierge y la de Logística.
    INSTRUCCIONES DE ENSAMBLAJE:
    1. Si Logística es 'NO_APLICA', ignóralo. Pule solo el Concierge.
    2. Si Logística tiene información, intégrala fluido al final del Concierge.
    3. REVISIÓN DE QA: Verifica contra el JSON que no haya mentiras.
    4. Cero redundancias: Elimina saludos dobles.
    5. Elimina completamente cualquier mención de 'NO_APLICA'.""",
    expected_output="Un único mensaje final cohesionado, directo, veraz y amable para el cliente. Sin 'NO_APLICA'.",
    agent=auditor_qa,
    context=[task_atencion, task_calendario]
)

# ============================================
# CREW PRINCIPAL
# ============================================

oficina = Crew(
    agents=[concierge, especialista_cal, auditor_qa],
    tasks=[task_atencion, task_calendario, task_auditoria],
    process=Process.sequential,
    memory=False,
    cache=False,
    verbose=VERBOSE_MODE
)

# ============================================
# FUNCIONES DE PROCESAMIENTO
# ============================================

def procesar_consulta(pregunta_usuario: str, cliente_id: str, historial_lista: list) -> tuple:
    """
    Procesa una consulta completa a través del pipeline de agentes
    
    Returns:
        (respuesta_final, tiempo_procesamiento, modelo_usado)
    """
    tiempo_inicio = time.time()
    
    # 1. Sanitizar entrada
    pregunta_limpia = sanitizar_pregunta(pregunta_usuario)
    
    if pregunta_limpia != pregunta_usuario and VERBOSE_MODE:
        logger.warning(f"Pregunta modificada: '{pregunta_usuario}' -> '{pregunta_limpia}'")
    
    # 2. Convertir historial a string para pasar a agentes
    historial_string = convertir_historial_lista_a_string(historial_lista)
    
    # 3. Ejecutar el crew
    try:
        inputs_cliente = {
            'historial': historial_string,
            'pregunta': pregunta_limpia
        }
        
        respuesta_raw = oficina.kickoff(inputs=inputs_cliente)
        
        # Manejar diferentes formatos de respuesta según versión de CrewAI
        if hasattr(respuesta_raw, 'raw'):
            respuesta_texto = respuesta_raw.raw
        else:
            respuesta_texto = str(respuesta_raw)
        
        # 4. Limpiar respuesta
        respuesta_final = limpiar_respuesta(respuesta_texto)
        
        tiempo_procesamiento = time.time() - tiempo_inicio
        
        return respuesta_final, tiempo_procesamiento, "ollama/gemini"
    
    except Exception as e:
        logger.error(f"Error en procesamiento para cliente {cliente_id}: {e}")
        tiempo_procesamiento = time.time() - tiempo_inicio
        return f"❌ Error procesando su solicitud: {str(e)}", tiempo_procesamiento, "error"


# ============================================
# BUCLE PRINCIPAL INTERACTIVO
# ============================================

def main():
    """Función principal del servidor interactivo"""
    
    # Verificar seguridad
    verificar_seguridad()
    
    # Inicializar métricas
    metricas = Metricas()
    
    # Log de inicio
    log_inicio_sesion()
    print("\n" + "═"*60)
    print("🤖 Servidor de La Casa de los Abuelos INICIADO (v2.0)")
    print("Escribe 'salir' para apagar el bot.")
    print("═"*60 + "\n")
    
    # Inicializar cliente
    cliente_id = f"cliente_{uuid.uuid4().hex[:8]}"
    historial_lista = []
    
    try:
        while True:
            pregunta_usuario = input("👤 Cliente: ").strip()
            
            # Comando de salida
            if pregunta_usuario.lower() in ['salir', 'exit', 'quit', 'apagar']:
                print("🔌 Apagando el servidor...")
                break
            
            # Ignorar líneas vacías
            if not pregunta_usuario:
                continue
            
            print("⏳ Procesando (Concierge -> Logística -> QA)...")
            
            # Procesar consulta
            respuesta_final, tiempo_respuesta, modelo_usado = procesar_consulta(
                pregunta_usuario, cliente_id, historial_lista
            )
            
            # Mostrar respuesta
            print(f"\n🤖 Bot: {respuesta_final}\n")
            print("-" * 60)
            
            # Registrar en historial
            historial_lista = agregar_al_historial(
                historial_lista,
                {'rol': 'cliente', 'contenido': pregunta_usuario},
                MAX_CONTEXT_MESSAGES
            )
            historial_lista = agregar_al_historial(
                historial_lista,
                {'rol': 'bot', 'contenido': respuesta_final},
                MAX_CONTEXT_MESSAGES
            )
            
            # Guardar en base de datos
            try:
                guardar_conversacion(
                    cliente_id=cliente_id,
                    pregunta=pregunta_usuario,
                    respuesta=respuesta_final,
                    modelo_usado=modelo_usado,
                    tiempo_respuesta_segundos=tiempo_respuesta,
                    exitosa=True
                )
                
                # Crear/actualizar lead
                crear_o_actualizar_lead(cliente_id, estado="prospecto")
            except Exception as e:
                logger.error(f"Error guardando en DB: {e}")
            
            # Registrar en métricas
            metricas.registrar_consulta(tiempo_respuesta, modelo_usado, exitosa=True)
            
            # Log
            log_consulta(cliente_id, pregunta_usuario, respuesta_final, tiempo_respuesta)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrumpido por el usuario")
    
    except Exception as e:
        logger.error(f"Error en bucle principal: {e}")
        print(f"\n❌ Error: {e}")
    
    finally:
        # Guardar métricas finales
        resumen_metricas = metricas.obtener_resumen()
        print("\n" + "="*60)
        print("📊 RESUMEN DE SESIÓN")
        print("="*60)
        print(json.dumps(resumen_metricas, indent=2, ensure_ascii=False))
        
        try:
            guardar_metricas(resumen_metricas)
        except Exception as e:
            logger.error(f"Error guardando métricas: {e}")
        
        log_cierre_sesion(resumen_metricas)
        print("\n✅ Servidor apagado correctamente\n")


# ============================================
# PUNTO DE ENTRADA
# ============================================

if __name__ == "__main__":
    main()
