import os
import json
from datetime import datetime
from crewai import Agent, Task, Crew, Process, LLM

# 1. Configuración de Rutas y Carga de Conocimiento
base_path = os.path.dirname(os.path.abspath(__file__))
def load_json(name):
    path = os.path.join(base_path, '..', 'conocimiento', name)
    with open(path, 'r', encoding='utf-8') as f:
        return json.dumps(json.load(f), indent=2, ensure_ascii=False)

info_casa = load_json('casa_abuelos.json')
info_calendario = load_json('disponibilidad.json')

# 2. Configuración Mistral NeMo (Motor Local RTX 3070)
llm_vendedor = LLM(
    model="ollama/mistral-nemo", 
    base_url="http://localhost:11434",
    temperature=0.7, 
    config={"num_ctx": 4096} 
)

llm_auditor  = LLM(
    model="ollama/mistral-nemo", 
    base_url="http://localhost:11434",
    temperature=0.1, 
    config={"num_ctx": 4096} 
)

# --- AGENTES ---
prompt_backstory_concierge = f"""
Eres el Concierge y primer punto de contacto de 'La Casa de los Abuelos' en Punta Pérula.
Tienes dos misiones principales:
1. Prospectos: Entusiasmar a los clientes potenciales destacando nuestras amenidades (como Starlink de 200MB/s, A/C en las habitaciones y cercanía a la playa).
2. Huéspedes: Brindar soporte rápido sobre logística, accesos y reglas durante su estancia.

REGLAS ESTRICTAS E INQUEBRANTABLES:
- TU ÚNICA FUENTE DE VERDAD ES ESTE JSON: {info_casa}
- CERO ALUCINACIONES: Tienes estrictamente prohibido inventar o asumir características, vistas (NO hay vista al mar desde la terraza), servicios, amenidades o reglas que no estén en el JSON.
- PROTOCOLO DE INCERTIDUMBRE: Si el cliente pregunta algo que NO está en el JSON, responde textualmente: 'No tengo esa información disponible en este momento, lo consulto con Mario o Elia y regreso con usted'.
- LÍMITE DE ROL (FECHAS Y COSTOS): Tienes ESTRICTAMENTE PROHIBIDO hablar de fechas disponibles, meses, o hacer cotizaciones. Si el cliente pregunta por disponibilidad, tu respuesta debe ser enfocada a las amenidades y añadir: 'En un momento nuestro especialista de logística le confirmará los espacios libres'.
- TONO: Sé cálido, profesional, servicial y claro. 
"""

concierge = Agent(
    role='Concierge de Ventas',
    goal='Atender dudas y entusiasmar al cliente ÚNICAMENTE con las amenidades y reglas.',
    backstory=prompt_backstory_concierge,
    llm=llm_vendedor,
    verbose=True
)

fecha_actual = datetime.now().strftime("%Y-%m-%d")

prompt_backstory_logistica = f"""
Eres el Especialista de Disponibilidad, Cotización y Logística para 'La Casa de los Abuelos'.
Tu objetivo es interpretar solicitudes de fechas, verificar disponibilidad y calcular costos.

FECHA ACTUAL: {fecha_actual}. Utiliza esta fecha como punto de partida.

REGLAS DE NEGOCIO ESTRICTAS:
1. CAPACIDAD: Máximo 11 personas en total. Si excede 11, informa que la capacidad máxima ha sido superada.
2. ESTANCIA MÍNIMA: 2 noches obligatorias.
3. TARIFAS: Revisa 'temporada_alta_rangos' en el calendario. Si ALGUNA de las fechas solicitadas cae entre el 'inicio' y 'fin' de una temporada alta, aplica tarifa de $4,500 MXN por noche. Si las fechas NO están en esos rangos, aplica tarifa de Temporada baja: $3,500 MXN por noche. El costo es fijo hasta 11 personas.
4. CÁLCULO DE COSTO: Multiplica estrictamente (Número de noches) x (Tarifa). El apartado siempre es el costo de 1 noche.

INSTRUCCIONES DE OPERACIÓN:
- DISPONIBILIDAD: Revisa el calendario: {info_calendario}. Si las fechas cruzan con 'fechas_no_disponibles', tu respuesta debe ser negativa para esas fechas, pero ofrece las fechas libres más cercanas en ese mes.
- ÉXITO: Si hay disponibilidad, desglosa la cantidad de noches, el costo total matemático y el monto de apartado.
- FUERA DE DOMINIO: Si el mensaje del cliente NO incluye preguntas sobre fechas o disponibilidad, responde ÚNICA Y ESTRICTAMENTE con la palabra: 'NO_APLICA'. Sin saludos ni texto adicional.
"""

especialista_cal = Agent(
    role='Especialista de Disponibilidad, Cotización y Logística',
    goal='Interpretar fechas, validar calendario sin errores y calcular cotizaciones exactas o filtrar peticiones.',
    backstory=prompt_backstory_logistica,
    llm=llm_vendedor, 
    verbose=True
)

prompt_auditor = f"""
Eres el Auditor Final de Calidad (QA) y Veracidad para las comunicaciones de 'La Casa de los Abuelos'. 
Tu función es someter el borrador de respuesta generado a una prueba de validación estricta contra el Baseline oficial.

BASELINE DE VERDAD (Tu única fuente de datos permitida):
{info_casa}

REGLAS DE VALIDACIÓN CRÍTICA (Tolerancia Cero):
1. PRUEBA DE ALUCINACIONES: La propiedad está a 12 minutos caminando de la playa (o 3 en auto). NO tiene vista al mar. Si el borrador menciona esto, reescribe la oración para ajustarla a la realidad.
2. PRUEBA DE AMENIDADES: Confirma que no se prometan toallas de baño/playa, que el internet sea 'Starlink', y que las mascotas estén limitadas estrictamente al exterior.
3. PRUEBA FINANCIERA: Prohibido aprobar descuentos, promociones o alteraciones en los costos de apartado.
4. CONTROL DE RUIDO DEL SISTEMA: Si en el texto que recibes aparece la palabra 'NO_APLICA' o 'NO_APLICA.', elimínala por completo. Bajo ninguna circunstancia el cliente debe leer esa palabra.
5. CONTROL DE TONO: Elimina adjetivos exagerados ('majestuoso', 'paraíso'). Mantén el mensaje cálido pero basado en hechos comprobables.

INSTRUCCIÓN DE SALIDA:
Recibirás el texto de los agentes. Analízalo línea por línea contra el Baseline. Tu única respuesta debe ser el MENSAJE FINAL CORREGIDO Y APROBADO, listo para el cliente. NO incluyas notas de auditoría, simplemente entrega la versión limpia.
"""

auditor_qa = Agent(
    role='Auditor de Veracidad y Regresión (QA)',
    goal='Someter cada respuesta a una validación rigurosa contra el JSON y limpiar variables de sistema.',
    backstory=prompt_auditor,
    llm=llm_auditor,
    verbose=True
)

# --- FLUJO DE TRABAJO (TASKS) ---
# Importante: Las variables {historial} y {pregunta} serán inyectadas por CrewAI dinámicamente.

task_atencion = Task(
    description="""Historial de la conversación:
    {historial}
    
    Analiza la NUEVA consulta del cliente: '{pregunta}'. 
    Responde a las dudas sobre amenidades, servicios o reglas de la propiedad manteniendo el contexto anterior. IGNORA cualquier mención a fechas o presupuestos. Sé directo y ve al grano.""",
    expected_output="Un mensaje cálido pero conciso sobre las características de la casa, basado estrictamente en el JSON. Cero menciones a fechas o precios.",
    agent=concierge
)

task_calendario = Task(
    description="""Historial de la conversación:
    {historial}
    
    Analiza la NUEVA consulta del cliente: '{pregunta}'. 
    Extrae la intención de reserva. Si hay fechas o meses, verifica disponibilidad en el calendario y calcula el costo exacto. Si NO menciona fechas ni pide cotización, tu salida debe ser estrictamente la etiqueta 'NO_APLICA'.""",
    expected_output="El desglose matemático de la reserva (fechas, costo total, apartado), o la palabra 'NO_APLICA'. Sin saludos, sin preámbulos.",
    agent=especialista_cal
)

task_auditoria = Task(
    description="""Recibirás la respuesta del Concierge y la de Logística.
    INSTRUCCIONES DE ENSAMBLAJE:
    1. Si el texto de Logística es 'NO_APLICA', ignóralo. Pule solo el texto del Concierge.
    2. Si Logística tiene información, intégrala de manera fluida al final del mensaje del Concierge.
    3. REVISIÓN DE QA: Verifica rígidamente contra el JSON que no haya mentiras.
    4. Cero redundancias: Elimina saludos dobles.""",
    expected_output="Un solo mensaje final cohesionado, directo, veraz y amable para el cliente. Prohibido imprimir la palabra 'NO_APLICA'.",
    agent=auditor_qa,
    context=[task_atencion, task_calendario]
)

# --- CREW (LA OFICINA) ---

oficina = Crew(
    agents=[concierge, especialista_cal, auditor_qa],
    tasks=[task_atencion, task_calendario, task_auditoria],
    process=Process.sequential, 
    memory=False, 
    cache=False,  
    verbose=True  
)

# --- INICIO DEL SERVIDOR INTERACTIVO ---

historial_chat = ""

print("\n" + "═"*50)
print("🤖 Servidor de La Casa de los Abuelos INICIADO")
print("Escribe 'salir' para apagar el bot.")
print("═"*50 + "\n")

while True:
    pregunta_usuario = input("👤 Cliente: ")
    
    if pregunta_usuario.lower() in ['salir', 'exit', 'quit', 'apagar']:
        print("🔌 Apagando el servidor...")
        break

    print("⏳ Procesando (Concierge -> Logística -> QA)...")

    # Inyectamos la memoria y la nueva pregunta dinámicamente
    inputs_cliente = {
        'historial': historial_chat,
        'pregunta': pregunta_usuario
    }

    respuesta_final = oficina.kickoff(inputs=inputs_cliente)
    
    # Manejo robusto del output según la versión de CrewAI
    respuesta_texto = respuesta_final.raw if hasattr(respuesta_final, 'raw') else str(respuesta_final)
    
    print(f"\n🤖 Bot: {respuesta_texto}\n")
    print("-" * 50)

    # Actualización del historial
    historial_chat += f"Cliente: {pregunta_usuario}\nBot: {respuesta_texto}\n\n"
    
    # Corte de seguridad para evitar desborde de VRAM (mantiene los últimos ~2000 caracteres)
    if len(historial_chat) > 2000: 
        # Buscamos el último salto de línea doble para no cortar el texto a la mitad de una palabra
        corte = historial_chat.find("\n\n", len(historial_chat) - 2000)
        historial_chat = historial_chat[corte + 2:] if corte != -1 else historial_chat[-2000:]