#!/usr/bin/env python3
"""
🚀 STRESS TEST OPTIMIZADO - Casa Abuelos IA v2.0
Prueba de carga para oficina_nueva.py con análisis detallado de rendimiento
"""

import sys
import json
import time
import statistics
from datetime import datetime
from pathlib import Path

# Agregar scripts al path
sys.path.insert(0, str(Path(__file__).parent))

from config import CAPACIDAD_MAXIMA, MAX_HISTORIAL_LENGTH
from utils import sanitizar_pregunta, validar_fechas, Metricas, verificar_ollama_disponible
from database import inicializar_db, guardar_conversacion, crear_o_actualizar_lead

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════════════════════

ARCHIVO_REPORTE = "logs/reporte_stress_test.json"
ARCHIVO_RESULTADOS = "logs/stress_test_results.json"

# Casos de prueba categorizados
CASOS_DISPONIBILIDAD = [
    "¿Tienen disponible del 20 al 23 de marzo? Somos 6 adultos.",
    "¿Hay cuartos libres en abril del 5 al 8? Somos 4 personas.",
    "Quiero reservar para el 1 de mayo, pero solo 2 noches.",
]

CASOS_COSTOS = [
    "¿Cuánto cuesta la noche en mayo? ¿Tienen descuento grupal?",
    "¿Cuál es el costo total del 7 al 10 de mayo?",
    "Si vamos 10 personas, ¿hacen descuento en la tarifa?",
]

CASOS_AMENIDADES = [
    "¿Aceptan perros dentro de las habitaciones? Mi perro es pequeño.",
    "¿Tienen microondas y licuadora? Necesito cocinar.",
    "¿Tienen TV con Netflix? ¿Hay aire acondicionado?",
    "¿Tienen conexión a internet de calidad? Trabajo remoto.",
]

CASOS_INFO_GENERAL = [
    "Me dijeron que tienen vista al mar, ¿es cierto?",
    "¿Cómo llego desde Guadalajara?",
    "¿Cuáles son sus políticas de cancelación?",
]

CASOS_EDGE = [
    "",  # Input vacío
    "¿" * 100,  # Input muy largo
    "abc123!@#$%",  # Caracteres especiales
    "¿Disponible 15-14 de marzo?",  # Fechas invertidas
]

# Agrupar todos los casos
TODOS_LOS_CASOS = {
    "disponibilidad": CASOS_DISPONIBILIDAD,
    "costos": CASOS_COSTOS,
    "amenidades": CASOS_AMENIDADES,
    "info_general": CASOS_INFO_GENERAL,
    "edge_cases": CASOS_EDGE,
}

# ═══════════════════════════════════════════════════════════════════════════
# FUNCIONES DE UTILIDAD
# ═══════════════════════════════════════════════════════════════════════════

def procesar_consulta_simple(pregunta: str) -> tuple:
    """
    Procesa una consulta de forma simple para testing.
    Retorna: (respuesta_simulada, tiempo_ms, tipo_resultado)
    """
    start_time = time.time()
    
    try:
        # Validación básica
        pregunta_limpia = sanitizar_pregunta(pregunta)
        
        if not pregunta_limpia:
            resultado = ("Pregunta vacía o inválida", 0, "error")
        elif len(pregunta) > 500:
            resultado = ("Pregunta muy larga", 0, "error")
        elif "disponible" in pregunta.lower() or "fecha" in pregunta.lower():
            # Intenta validar fechas
            try:
                validar_fechas(pregunta)
                resultado = ("✓ Consulta de disponibilidad procesada", 1, "success")
            except ValueError as e:
                resultado = (f"❌ Fechas inválidas: {str(e)}", 0, "warning")
        else:
            resultado = ("✓ Consulta procesada", 1, "success")
            
    except Exception as e:
        resultado = (f"❌ Error: {str(e)}", 0, "error")
    
    tiempo_ms = (time.time() - start_time) * 1000
    return resultado[0], tiempo_ms, resultado[2]

# ═══════════════════════════════════════════════════════════════════════════
# EJECUCIÓN DEL TEST
# ═══════════════════════════════════════════════════════════════════════════

def ejecutar_stress_test():
    """Ejecuta el stress test completo"""
    
    print("\n" + "="*80)
    print("🚀 STRESS TEST - Casa Abuelos IA v2.0")
    print("="*80)
    
    # Inicializar base de datos
    inicializar_db()
    
    # Verificar Ollama
    ollama_disponible = verificar_ollama_disponible()
    print(f"\n📡 Estado Ollama: {'✅ Disponible' if ollama_disponible else '⚠️ No disponible (usará Gemini)'}")
    
    resultados_por_categoria = {}
    todas_las_respuestas = []
    tiempos = []
    
    total_tests = sum(len(casos) for casos in TODOS_LOS_CASOS.values())
    test_actual = 0
    
    print(f"📊 Total de pruebas: {total_tests}\n")
    
    # Ejecutar pruebas por categoría
    for categoria, casos in TODOS_LOS_CASOS.items():
        print(f"\n{'─'*80}")
        print(f"📋 {categoria.upper()} ({len(casos)} tests)")
        print(f"{'─'*80}")
        
        resultados_categoria = {
            "categoria": categoria,
            "total": len(casos),
            "exitosas": 0,
            "errores": 0,
            "advertencias": 0,
            "tiempos_ms": [],
            "pruebas": []
        }
        
        for pregunta in casos:
            test_actual += 1
            
            # Mostrar progreso
            display_text = pregunta[:60] if pregunta else "[VACÍO]"
            print(f"  [{test_actual:2d}/{total_tests}] {display_text:60s} ", end="", flush=True)
            
            # Procesar
            respuesta, tiempo_ms, resultado_tipo = procesar_consulta_simple(pregunta)
            
            # Registrar
            tiempos.append(tiempo_ms)
            resultados_categoria["tiempos_ms"].append(tiempo_ms)
            
            # Contar resultados
            if resultado_tipo == "success":
                resultados_categoria["exitosas"] += 1
                simbolo = "✅"
            elif resultado_tipo == "warning":
                resultados_categoria["advertencias"] += 1
                simbolo = "⚠️"
            else:
                resultados_categoria["errores"] += 1
                simbolo = "❌"
            
            print(f"{simbolo} {tiempo_ms:6.2f}ms")
            
            # Guardar resultado detallado
            resultados_categoria["pruebas"].append({
                "pregunta": pregunta if pregunta else "[VACÍO]",
                "respuesta_corta": respuesta[:100],
                "tiempo_ms": round(tiempo_ms, 2),
                "tipo": resultado_tipo,
                "timestamp": datetime.now().isoformat()
            })
            
            todas_las_respuestas.append({
                "categoria": categoria,
                "pregunta": pregunta if pregunta else "[VACÍO]",
                "respuesta": respuesta,
                "tiempo_ms": round(tiempo_ms, 2),
                "tipo": resultado_tipo
            })
            
            time.sleep(0.1)  # Pequeña pausa entre requests
        
        resultados_por_categoria[categoria] = resultados_categoria
    
    # ═════════════════════════════════════════════════════════════════════════
    # GENERACIÓN DE MÉTRICAS
    # ═════════════════════════════════════════════════════════════════════════
    
    print(f"\n\n{'='*80}")
    print("📊 ANÁLISIS DE RESULTADOS")
    print(f"{'='*80}\n")
    
    total_exitosas = sum(r["exitosas"] for r in resultados_por_categoria.values())
    total_errores = sum(r["errores"] for r in resultados_por_categoria.values())
    total_advertencias = sum(r["advertencias"] for r in resultados_por_categoria.values())
    
    tasa_exito = (total_exitosas / total_tests * 100) if total_tests > 0 else 0
    
    print(f"✅ Exitosas:     {total_exitosas:3d}  ({tasa_exito:5.1f}%)")
    print(f"⚠️  Advertencias: {total_advertencias:3d}  ({total_advertencias/total_tests*100:5.1f}%)" if total_tests > 0 else "")
    print(f"❌ Errores:      {total_errores:3d}  ({total_errores/total_tests*100:5.1f}%)" if total_tests > 0 else "")
    
    print(f"\n⏱️  TIEMPOS (ms):")
    print(f"  Min:     {min(tiempos):.2f} ms")
    print(f"  Max:     {max(tiempos):.2f} ms")
    print(f"  Promedio: {statistics.mean(tiempos):.2f} ms")
    print(f"  Mediana: {statistics.median(tiempos):.2f} ms")
    if len(tiempos) > 1:
        print(f"  Std Dev: {statistics.stdev(tiempos):.2f} ms")
    
    print(f"\n📈 POR CATEGORÍA:")
    print(f"{'Categoría':<15} {'Exitosas':<12} {'Advertencias':<15} {'Errores':<10} {'T.Promedio':<15}")
    print(f"{'-'*70}")
    
    for categoria, datos in resultados_por_categoria.items():
        tiempo_prom = statistics.mean(datos["tiempos_ms"]) if datos["tiempos_ms"] else 0
        print(f"{categoria:<15} {datos['exitosas']:<12} {datos['advertencias']:<15} "
              f"{datos['errores']:<10} {tiempo_prom:>12.2f} ms")
    
    # ═════════════════════════════════════════════════════════════════════════
    # GUARDAR REPORTES
    # ═════════════════════════════════════════════════════════════════════════
    
    reporte_json = {
        "timestamp": datetime.now().isoformat(),
        "entorno": {
            "ollama_disponible": ollama_disponible,
            "capacidad_maxima_personas": CAPACIDAD_MAXIMA,
            "max_historial": MAX_HISTORIAL_LENGTH
        },
        "resumen": {
            "total_tests": total_tests,
            "exitosas": total_exitosas,
            "advertencias": total_advertencias,
            "errores": total_errores,
            "tasa_exito_pct": round(tasa_exito, 2)
        },
        "tiempos": {
            "min_ms": round(min(tiempos), 2),
            "max_ms": round(max(tiempos), 2),
            "promedio_ms": round(statistics.mean(tiempos), 2),
            "mediana_ms": round(statistics.median(tiempos), 2),
            "std_dev_ms": round(statistics.stdev(tiempos), 2) if len(tiempos) > 1 else 0
        },
        "por_categoria": resultados_por_categoria,
        "todas_las_pruebas": todas_las_respuestas
    }
    
    # Guardar reporte completo
    Path("logs").mkdir(exist_ok=True)
    with open(ARCHIVO_REPORTE, 'w', encoding='utf-8') as f:
        json.dump(reporte_json, f, indent=2, ensure_ascii=False)
    
    # Guardar resumen compacto
    resumen_compacto = {
        "timestamp": reporte_json["timestamp"],
        "resumen": reporte_json["resumen"],
        "tiempos": reporte_json["tiempos"],
        "categorias": {
            cat: {
                "total": datos["total"],
                "exitosas": datos["exitosas"],
                "tasa_exito_pct": round(datos["exitosas"]/datos["total"]*100, 2) if datos["total"] > 0 else 0,
                "tiempo_promedio_ms": round(statistics.mean(datos["tiempos_ms"]), 2) if datos["tiempos_ms"] else 0
            }
            for cat, datos in resultados_por_categoria.items()
        }
    }
    
    with open(ARCHIVO_RESULTADOS, 'w', encoding='utf-8') as f:
        json.dump(resumen_compacto, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*80}")
    print(f"✅ Reportes guardados:")
    print(f"   📄 Completo: {ARCHIVO_REPORTE}")
    print(f"   📋 Resumen:  {ARCHIVO_RESULTADOS}")
    print(f"{'='*80}\n")
    
    return reporte_json

# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    try:
        reporte = ejecutar_stress_test()
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrumpido por el usuario.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error durante el test: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)