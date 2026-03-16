#!/usr/bin/env python3
"""
🔍 DEBUG - Ver qué retorna crew.kickoff()
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from config import PROMPTS
from utils import get_llm_vendedor, get_llm_auditor, verificar_ollama_disponible
from crewai import Agent, Task, Crew, Process
import json

# Cargar datos
with open("conocimiento/casa_abuelos.json", 'r', encoding='utf-8') as f:
    casa_data = json.load(f)
with open("conocimiento/disponibilidad.json", 'r', encoding='utf-8') as f:
    disponibilidad = json.load(f)

print("🔍 DEBUG - Retorno de crew.kickoff()\n")
print("="*80)

# Crear LLMs
llm_vendedor = get_llm_vendedor()
llm_auditor = get_llm_auditor()

# Crear agentes
agente_concierge = Agent(
    role="Concierge",
    goal="Proporcionar atención al cliente",
    backstory=PROMPTS["concierge"],
    llm=llm_vendedor,
    verbose=False
)

agente_logistica = Agent(
    role="Especialista Logística",
    goal="Verificar disponibilidad y costos",
    backstory=PROMPTS["logistica"],
    llm=llm_vendedor,
    verbose=False
)

agente_auditor = Agent(
    role="Auditor QA",
    goal="Validar respuestas",
    backstory=PROMPTS["auditor"],
    llm=llm_auditor,
    verbose=False
)

# Pregunta simple
pregunta = "¿Cuánto cuesta por noche?"

# Crear tareas
tarea_concierge = Task(
    description=f"Responde a: {pregunta}",
    expected_output="Respuesta sobre comodidades",
    agent=agente_concierge,
    output_file=None
)

tarea_logistica = Task(
    description=f"Verifica costos para: {pregunta}",
    expected_output="Información de precios",
    agent=agente_logistica,
    output_file=None
)

tarea_auditor = Task(
    description=f"Valida la respuesta sobre: {pregunta}",
    expected_output="Respuesta validada",
    agent=agente_auditor,
    output_file=None
)

print("\n📡 Ejecutando crew.kickoff()...\n")

crew = Crew(
    agents=[agente_concierge, agente_logistica, agente_auditor],
    tasks=[tarea_concierge, tarea_logistica, tarea_auditor],
    process=Process.sequential,
    verbose=False
)

resultado = crew.kickoff()

print("\n" + "="*80)
print("📊 ANÁLISIS DEL RESULTADO:\n")

print(f"Tipo de resultado: {type(resultado)}")
print(f"Clase: {resultado.__class__.__name__}")
print()

# Try different ways to extract the response
print("1️⃣  resultado directo:")
print(f"   {str(resultado)[:200]}")
print()

# Check if it has attributes
print("2️⃣  Atributos disponibles:")
attrs = [attr for attr in dir(resultado) if not attr.startswith('_')]
for attr in attrs[:15]:
    try:
        val = getattr(resultado, attr)
        if not callable(val):
            print(f"   .{attr} = {str(val)[:100]}...")
    except:
        pass
print()

# Try to get raw output
print("3️⃣  Intentando acceder a raw_output:")
if hasattr(resultado, 'raw_output'):
    print(f"   {str(resultado.raw_output)[:300]}")
else:
    print("   No existe raw_output")
print()

# Convert to string with different methods
print("4️⃣  str(resultado):")
print(f"   {str(resultado)}")
print()

print("5️⃣  repr(resultado):")
print(f"   {repr(resultado)[:300]}")
print()

print("="*80)
print("\n💡 RECOMENDACIÓN:")
print("   Usar el atributo correcto para obtener la respuesta completa")
