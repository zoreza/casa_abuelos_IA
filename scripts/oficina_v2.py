import os
import json
from datetime import datetime
from crewai import Agent, Task, Crew, Process, LLM

# 1. Carga de Conocimiento Dual
base_path = os.path.dirname(os.path.abspath(__file__))
info_path = os.path.join(base_path, '..', 'conocimiento', 'casa_abuelos.json')
cal_path = os.path.join(base_path, '..', 'conocimiento', 'disponibilidad.json')

with open(info_path, 'r', encoding='utf-8') as f:
    info_casa = json.dumps(json.load(f), indent=2, ensure_ascii=False)

with open(cal_path, 'r', encoding='utf-8') as f:
    info_calendario = json.dumps(json.load(f), indent=2, ensure_ascii=False)

# 2. Inteligencia Local (Xenia-Mario GPU)
inteligencia_local = LLM(
    model="ollama/gemma2:9b", 
    base_url="http://localhost:11434"
)

# 3. Agente 1: El Concierge (Ventas e Información)
concierge = Agent(
    role='Concierge de La Casa de los Abuelos',
    goal='Enamorar al huésped con la información de la casa.',
    backstory=f"Eres experto en hospitalidad. Datos de la casa: {info_casa}",
    llm=inteligencia_local,
    allow_delegation=False,
    verbose=True
)

# 4. Agente 2: El Especialista de Calendario (Logística)
calendar_agent = Agent(
    role='Especialista en Reservas y Calendario',
    goal='Validar disponibilidad de fechas y calcular costos.',
    backstory=f"""Eres un auditor estricto. Tu ÚNICA prioridad es revisar la lista de 
    'fechas_ocupadas' en este JSON: {info_calendario}.
    
    REGLA DE ORO: Si una sola de las fechas que pide el usuario coincide con la lista 
    de 'fechas_ocupadas', debes decir 'NO ESTÁ DISPONIBLE' de forma tajante. 
    No te dejes influenciar por la amabilidad del Concierge. Sé un robot de logística.""",
    llm=inteligencia_local,
    allow_delegation=False,
    verbose=True
)

# 5. Entrada del Huésped
print("\n" + "="*40)
pregunta_huesped = input("🤔 ¿Qué desea el huésped?: ")
print("="*40 + "\n")

# 6. Tareas Coordinadas
tarea_venta = Task(
    description=f"Responde amablemente a: '{pregunta_huesped}'. Habla de las amenidades.",
    expected_output="Una respuesta vendedora y amable.",
    agent=concierge
)

tarea_logistica = Task(
    description="Revisa si las fechas mencionadas están libres y calcula el costo total.",
    expected_output="Confirmación de disponibilidad y presupuesto total en MXN.",
    agent=calendar_agent,
    context=[tarea_venta] # Toma lo que dijo el concierge para dar seguimiento
)

# 7. Ejecución de la Oficina
oficina = Crew(
    agents=[concierge, calendar_agent],
    tasks=[tarea_venta, tarea_logistica],
    process=Process.sequential # Primero uno, luego el otro
)

resultado = oficina.kickoff()

# 8. Reporte en Pantalla
print("\n" + "#"*40)
print("## RESPUESTA FINAL DE LA OFICINA ##")
print("#"*40 + "\n")
print(resultado)