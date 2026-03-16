import subprocess
import json
import time
from datetime import datetime

# --- CONFIGURACIÓN DEL TEST ---
DURACION_TEST_MINUTOS = 30
ARCHIVO_LOG = "logs/reporte_stress_test.json"

CASOS_PRUEBA = [
    "¿Tienen disponible del 20 al 23 de marzo? Somos 6 adultos.",
    "¿Cuánto cuesta la noche en mayo? ¿Tienen internet para videollamadas?",
    "Me dijeron que tienen vista al mar, ¿es cierto? Quiero ir este fin de semana.",
    "Somos un grupo de 15 personas para abril, ¿cabemos todos?",
    "¿Aceptan perros dentro de las habitaciones? Mi perro es pequeño.",
    "¿Tienen microondas y licuadora? Necesito cocinar para mis hijos.",
    "¿Cuál es el costo total del 7 al 10 de mayo? ¿Hay descuento si soy de IBM?",
    "¿Cómo llego desde Guadalajara? ¿La ruta por Autlán es segura?",
    "¿Tienen TV con Netflix? ¿Hay aire acondicionado en todos los cuartos?",
    "Quiero reservar pero solo por una noche el sábado, ¿se puede?"
]

resultados = []

print(f"🚀 Iniciando S&R Stress Test...")
start_time = time.time()
iteracion = 1

try:
    while (time.time() - start_time) < (DURACION_TEST_MINUTOS * 60):
        for query in CASOS_PRUEBA:
            if (time.time() - start_time) >= (DURACION_TEST_MINUTOS * 60):
                break
                
            print(f" [{iteracion}] Probando: {query[:50]}...")
            
            # Ejecución del proceso
            proc_start = time.time()
            process = subprocess.Popen(
                ['python3', 'scripts/oficina.py'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(input=query)
            proc_end = time.time()
            
            # Registro de datos
            resultados.append({
                "iteracion": iteracion,
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "query": query,
                "output_raw": stdout,
                "error": stderr,
                "latencia": round(proc_end - proc_start, 2)
            })
            
            # Guardado incremental
            with open(ARCHIVO_LOG, 'w', encoding='utf-8') as f:
                json.dump(resultados, f, indent=2, ensure_ascii=False)
            
            iteracion += 1
            time.sleep(2) # Respiro para la GPU

except KeyboardInterrupt:
    print("\n Test interrumpido por el usuario.")

print(f"🏁 Test finalizado. Archivo generado: {ARCHIVO_LOG}")