#!/usr/bin/env python3
"""
🎯 TEST INTERACTIVO - Casa Abuelos IA v2.0
Prueba manual de los agentes con respuestas en tiempo real
"""

import sys
import uuid
import time
from pathlib import Path
from datetime import datetime

# Agregar scripts al path
sys.path.insert(0, str(Path(__file__).parent))

from config import PROMPTS, GOOGLE_API_KEY, OLLAMA_BASE_URL, MAX_CONTEXT_MESSAGES
from utils import (
    sanitizar_pregunta, 
    validar_fechas, 
    verificar_ollama_disponible,
    get_llm_vendedor,
    get_llm_auditor,
    agregar_al_historial,
    convertir_historial_lista_a_string,
    limpiar_respuesta,
    Metricas
)
from database import (
    inicializar_db,
    guardar_conversacion,
    crear_o_actualizar_lead,
    obtener_estadisticas_cliente
)
from logger_config import log_consulta, log_error, log_fallback

from crewai import Agent, Task, Crew, Process
import json

# ═══════════════════════════════════════════════════════════════════════════
# CARGAR DATOS DE CONOCIMIENTO
# ═══════════════════════════════════════════════════════════════════════════

def cargar_json(ruta):
    """Carga un archivo JSON con manejo de errores"""
    try:
        with open(ruta, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error cargando {ruta}: {e}")
        return {}

# Cargar datos
casa_data = cargar_json("conocimiento/casa_abuelos.json")
disponibilidad = cargar_json("conocimiento/disponibilidad.json")
politicas = open("conocimiento/politicas.txt", 'r', encoding='utf-8').read() if Path("conocimiento/politicas.txt").exists() else ""
propiedad = open("conocimiento/propiedad.txt", 'r', encoding='utf-8').read() if Path("conocimiento/propiedad.txt").exists() else ""

# ═══════════════════════════════════════════════════════════════════════════
# CREAR AGENTES
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "="*80)
print("🎯 TEST INTERACTIVO - Casa Abuelos IA")
print("="*80)

# Verificar Ollama
ollama_disponible = verificar_ollama_disponible()
print(f"\n📡 Estado Ollama: {'✅ Disponible' if ollama_disponible else '⚠️ No disponible (usará Gemini)'}")
print(f"🤖 Usando: {'Ollama (Mistral Nemo)' if ollama_disponible else 'Google Gemini 1.5-flash'}")

# Inicializar DB
inicializar_db()
print("💾 Base de datos inicializada")

# Crear LLMs con fallback
llm_vendedor = get_llm_vendedor()
llm_auditor = get_llm_auditor()

# Convertir datos a strings para pasar a agentes
casa_abuelos_str = json.dumps(casa_data, indent=2, ensure_ascii=False)
disponibilidad_str = json.dumps(disponibilidad, indent=2, ensure_ascii=False)

# Crear Agentes (incluyendo Auditor para respuestas completas)
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

print("✅ Agentes creados\n")

# ═══════════════════════════════════════════════════════════════════════════
# FUNCIÓN DE PROCESAMIENTO - 3 AGENTES CON COORDINACIÓN
# ═══════════════════════════════════════════════════════════════════════════

cliente_id = str(uuid.uuid4())[:8]
historial_lista = []
metricas = Metricas()

def procesar_consulta(pregunta: str) -> str:
    """Procesa una consulta a través de los 3 agentes con coordinación"""
    global historial_lista, metricas
    
    try:
        # Sanitizar entrada
        pregunta_limpia = sanitizar_pregunta(pregunta)
        if not pregunta_limpia:
            return "❌ Pregunta vacía o inválida"
        
        # Agregar al historial
        historial_lista = agregar_al_historial(
            historial_lista, 
            {'rol': 'cliente', 'contenido': pregunta_limpia},
            MAX_CONTEXT_MESSAGES
        )
        
        # Convertir historial para los agentes
        historial_str = convertir_historial_lista_a_string(historial_lista)
        
        print(f"⏳ Procesando consulta... ", end="", flush=True)
        inicio = time.time()
        
        # Crear tareas con datos COMPLETOS (no truncados) y contexto
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
        
        # Ejecutar crew CON 3 AGENTES Y COORDINACIÓN
        crew = Crew(
            agents=[agente_concierge, agente_logistica, agente_auditor],
            tasks=[tarea_concierge, tarea_logistica, tarea_auditor],
            process=Process.sequential,
            verbose=False
        )
        
        # Ejecutar con inputs templated
        inputs_cliente = {
            'historial': historial_str,
            'pregunta': pregunta_limpia,
            'propiedad_info': casa_abuelos_str,
            'disponibilidad_info': disponibilidad_str
        }
        
        resultado = crew.kickoff(inputs=inputs_cliente)
        tiempo = time.time() - inicio
        
        # Obtener respuesta completa (manejar diferentes formatos de CrewAI)
        if hasattr(resultado, 'raw'):
            respuesta_crudo = resultado.raw
        else:
            respuesta_crudo = str(resultado).strip()
        
        respuesta_final = limpiar_respuesta(respuesta_crudo) if respuesta_crudo else "No se pudo procesar la consulta"
        
        # Registrar en base de datos
        guardar_conversacion(
            cliente_id,
            pregunta_limpia,
            respuesta_final if respuesta_final else respuesta_crudo,
            modelo_usado="ollama/mistral-nemo" if ollama_disponible else "gemini-1.5-flash",
            tiempo_respuesta_segundos=tiempo,
            exitosa=True
        )
        
        # Actualizar lead
        crear_o_actualizar_lead(cliente_id, nombre="Usuario Test", estado="prospecto")
        
        # Actualizar métricas
        metricas.registrar_consulta(tiempo, "exitosa", 
                                   "ollama/mistral-nemo" if ollama_disponible else "gemini-1.5-flash")
        
        # Log
        log_consulta(cliente_id, pregunta_limpia, respuesta_final, tiempo)
        
        # Agregar respuesta al historial
        historial_lista = agregar_al_historial(
            historial_lista,
            {'rol': 'agente', 'contenido': respuesta_final[:500]},
            MAX_CONTEXT_MESSAGES
        )
        
        print(f"✅ ({tiempo:.2f}s)")
        return respuesta_final
        
    except Exception as e:
        error_msg = f"❌ Error procesando consulta: {str(e)}"
        log_error(cliente_id, pregunta, str(e))
        print(f"❌")
        return error_msg

# ═══════════════════════════════════════════════════════════════════════════
# INTERFAZ INTERACTIVA
# ═══════════════════════════════════════════════════════════════════════════

def mostrar_menu():
    """Muestra el menú de opciones"""
    print("\n" + "-"*80)
    print("📋 OPCIONES:")
    print("-"*80)
    print("  1. Hacer pregunta sobre disponibilidad")
    print("  2. Hacer pregunta sobre precios")
    print("  3. Hacer pregunta sobre amenidades")
    print("  4. Hacer pregunta personalizada")
    print("  5. Ver estadísticas del cliente")
    print("  6. Ver historial de consultas")
    print("  0. Salir")
    print("-"*80)

def main():
    """Función principal"""
    global cliente_id
    
    print(f"\n👤 ID de Cliente: {cliente_id}")
    print(f"⏰ Sesión iniciada: {datetime.now().strftime('%H:%M:%S')}")
    
    preguntas_rapidas = {
        "1": "¿Tienen disponible del 20 al 23 de marzo para 6 personas?",
        "2": "¿Cuánto cuesta por noche en mayo? ¿Hay descuentos por grupo?",
        "3": "¿Aceptan mascotas? ¿Tienen internet de buena calidad?",
    }
    
    while True:
        mostrar_menu()
        opcion = input("Elige una opción: ").strip()
        
        if opcion == "0":
            print("\n👋 ¡Gracias por usar Casa Abuelos IA!")
            print(f"📊 Métricas de sesión:")
            print(f"   - Consultas: {metricas.total_consultas}")
            print(f"   - Tiempo promedio: {metricas.tiempo_promedio():.2f}s")
            print(f"   - Tasa de éxito: {metricas.tasa_exito():.1f}%")
            break
            
        elif opcion in ["1", "2", "3"]:
            pregunta = preguntas_rapidas[opcion]
            print(f"\n🎤 Pregunta: {pregunta}")
            respuesta = procesar_consulta(pregunta)
            print(f"\n🤖 Respuesta:")
            print(f"{'-'*80}")
            print(respuesta)
            print(f"{'-'*80}")
            
        elif opcion == "4":
            pregunta = input("\n🎤 Ingresa tu pregunta: ").strip()
            if pregunta:
                respuesta = procesar_consulta(pregunta)
                print(f"\n🤖 Respuesta:")
                print(f"{'-'*80}")
                print(respuesta)
                print(f"{'-'*80}")
            else:
                print("❌ Pregunta vacía")
                
        elif opcion == "5":
            print(f"\n📊 Estadísticas del cliente {cliente_id}:")
            stats = obtener_estadisticas_cliente(cliente_id)
            print(f"   - Consultas totales: {stats.get('total_consultas', 0)}")
            print(f"   - Consultas exitosas: {stats.get('consultas_exitosas', 0)}")
            print(f"   - Tiempo promedio: {stats.get('tiempo_promedio', 0):.2f}s")
            
        elif opcion == "6":
            print(f"\n📝 Historial (últimas 5 consultas):")
            for i, msg in enumerate(historial_lista[-10:], 1):
                rol = msg.get('rol', 'unknown').upper()
                contenido = msg.get('contenido', '')[:70]
                print(f"  [{i}] {rol}: {contenido}...")
        else:
            print("❌ Opción inválida")

# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Sesión interrumpida por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
