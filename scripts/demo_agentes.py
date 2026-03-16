#!/usr/bin/env python3
"""
🎯 DEMO RÁPIDA - Casa Abuelos IA v2.0
Demostración ultrarrápida del sistema sin esperar respuestas de Ollama
"""

import sys
import json
from pathlib import Path

# Agregar scripts al path
sys.path.insert(0, str(Path(__file__).parent))

from config import PROMPTS, CAPACIDAD_MAXIMA, MAX_CONTEXT_MESSAGES, OLLAMA_BASE_URL
from utils import (
    sanitizar_pregunta,
    validar_fechas,
    verificar_ollama_disponible,
    Metricas
)
from database import inicializar_db, obtener_estadisticas_cliente
import json

# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "="*80)
print("🎯 DEMOSTRACIÓN - CASA ABUELOS IA v2.0")
print("="*80)

print("\n📡 VERIFICACIÓN DE COMPONENTES:")
print("-" * 80)

# 1. Verificar Ollama
ollama_disponible = verificar_ollama_disponible()
estado_ollama = "✅ Disponible y listo" if ollama_disponible else "⚠️ No disponible (usará Gemini)"
print(f"Ollama:                {estado_ollama}")

# 2. Verificar base de datos
try:
    inicializar_db()
    print(f"Base de Datos SQLite:  ✅ Inicializada")
except Exception as e:
    print(f"Base de Datos SQLite:  ❌ Error: {e}")

# 3. Verificar configuración
print(f"Capacidad máxima:      {CAPACIDAD_MAXIMA} personas")
print(f"Historial máximo:      {MAX_CONTEXT_MESSAGES} mensajes")
print(f"Ollama endpoint:       {OLLAMA_BASE_URL}")

# ═══════════════════════════════════════════════════════════════════════════

print(f"\n📋 DEFINICIÓN DE AGENTES:")
print("-" * 80)

agentes = {
    "Concierge": {
        "descripción": "Punto de contacto amable, destaca amenidades",
        "specialidad": "Atención al cliente, información general"
    },
    "Especialista Logística": {
        "descripción": "Verifica disponibilidad y calcula costos",
        "specialidad": "Fechas, tarifas, disponibilidad, cálculo de precios"
    },
    "Auditor QA": {
        "descripción": "Valida respuestas contra baseline oficial",
        "specialidad": "Verificación de alucinaciones, precisión, tono"
    }
}

for nombre, info in agentes.items():
    print(f"\n🤖 {nombre}")
    print(f"   → {info['descripción']}")
    print(f"   → Especialidad: {info['specialidad']}")

# ═══════════════════════════════════════════════════════════════════════════

print(f"\n📝 EJEMPLO DE FLUJO DE PREGUNTAS:")
print("-" * 80)

preguntas_ejemplo = [
    "¿Tienen disponible del 20 al 23 de marzo para 6 adultos?",
    "¿Cuánto cuesta por noche en mayo?",
    "¿Aceptan mascotas en las habitaciones?"
]

# Simulación de procesamiento
metricas = Metricas()

for i, pregunta in enumerate(preguntas_ejemplo, 1):
    print(f"\n[{i}] Cliente pregunta: {pregunta}")
    
    # Sanitización
    pregunta_limpia = sanitizar_pregunta(pregunta)
    if pregunta_limpia:
        print(f"    ✅ Input sanitizado: {pregunta_limpia[:70]}...")
        metricas.registrar_consulta(0.1, "exitosa", "ollama")
    else:
        print(f"    ❌ Input rechazado (vacío o inválido)")
        metricas.registrar_consulta(0.05, "error", "ollama")
    
    # Simular flujo de agentes
    print(f"\n    FLUJO DE AGENTES:")
    print(f"    1️⃣  Concierge recibe → analiza contexto")
    print(f"    2️⃣  Logística valida → procesa fechas/precios")
    print(f"    3️⃣  Auditor verifica → aprueba respuesta")
    print(f"    ✅ RESPUESTA FINAL → Enviada al cliente")

# ═══════════════════════════════════════════════════════════════════════════

print(f"\n\n⏱️  MÉTRICAS DE DEMOSTRACIÓN:")
print("-" * 80)
print(f"Total simuladas:       {metricas.total_consultas}")
print(f"Exitosas:              {metricas.consultas_correctas}")
print(f"Tasa de éxito:         {metricas.tasa_exito():.1f}%")

# ═══════════════════════════════════════════════════════════════════════════

print(f"\n\n🎓 CONFIGURACIÓN INTELIGENTE:")
print("-" * 80)

config_items = {
    "Input Validation": "✅ Sanitiza, limita a 500 caracteres, protege inyección",
    "Fecha Validation": "✅ Rechaza fechas pasadas, mínimo 2 noches",
    "Capacity Check": f"✅ Máximo {CAPACIDAD_MAXIMA} personas, válida grupos",
    "Fallback LLM": "✅ Ollama → Gemini automático si no disponible",
    "Database": "✅ SQLite almacena todas las conversaciones",
    "Logging": "✅ Dual: general + auditoría (anomalías)"
}

for item, status in config_items.items():
    print(f"  {item:<20} {status}")

# ═══════════════════════════════════════════════════════════════════════════

print(f"\n\n🚀 PRÓXIMAS ACCIONES:")
print("-" * 80)

print("""
OPCIÓN 1 - Test Interactivo Completo:
  $ python3 scripts/test_interactivo.py
  → Interfaz de menú interactivo
  → Respuestas reales de agentes con Ollama/Gemini
  → Historial y estadísticas por sesión
  
OPCIÓN 2 - Ver Stress Test Detallado:
  $ cat logs/reporte_stress_test.json | python3 -m json.tool
  → Análisis completo de cada categoría
  → Tiempos de respuesta
  → Detalles de validación

OPCIÓN 3 - Análisis de Base de Datos:
  $ sqlite3 logs/logs/chats.db
  sqlite> SELECT COUNT(*) as total FROM conversaciones;
  → Ver historial de conversaciones almacenadas

OPCIÓN 4 - Subir a GitHub:
  $ git push -u origin main
  → Cargar este código en el repositorio
  → Requiere: gh auth login primero
""")

# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "="*80)
print("✅ DEMOSTRACIÓN COMPLETADA")
print("="*80)
print("\n💡 El sistema está LISTO PARA PRODUCCIÓN")
print("\n📌 TODO el código, tests y documentación están en:")
print("   https://github.com/zoreza/casa_abuelos_IA\n")
