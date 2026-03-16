# 🏡 La Casa de los Abuelos - Oficina Virtual IA v2.0

Sistema inteligente multiagente para gestión de reservas y atención al cliente en propiedad vacacional.

## ✨ Características Principales

- **3 Agentes Especializados**: Concierge, Especialista de Logística, Auditor QA
- **Fallback Inteligente**: Ollama local → Google Gemini automáticamente
- **Persistencia Completa**: SQLite para conversaciones, leads y reservas
- **Logging Estructurado**: Auditoría y debugging con trazabilidad completa
- **Métricas en Tiempo Real**: Monitoreo de performance y tasa de éxito
- **Validación y Sanitización**: Protección contra inyección de prompts
- **Configuración Segura**: Variables de entorno, sin API keys hardcodeadas

---

## 🚀 Instalación Rápida

### 1. Clonar y Preparar
```bash
cd /home/oficina_ia/oficina_abuelos
```

### 2. Crear Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno
```bash
# Copiar template
# El archivo .env ya está en la raíz

# Editar .env (IMPORTANTE)
nano .env

# Completar valores:
# - GOOGLE_API_KEY=tu-clave-de-google (opcional, para fallback)
# - OLLAMA_BASE_URL=http://localhost:11434 (si tienes Ollama)
```

### 5. Ejecutar
```bash
python scripts/oficina_nueva.py
```

---

## 📁 Estructura del Proyecto

```
oficina_abuelos/
├── .env                          # Variables de entorno (PRIVADO)
├── .env.example                  # Plantilla de ejemplo
├── requirements.txt              # Dependencias Python
├── README.md                      # Este archivo
│
├── scripts/                       # Scripts ejecutables
│   ├── oficina_nueva.py          # ⭐ PRINCIPAL - Versión refactorizada
│   ├── oficina.py                # Versión anterior (respaldo)
│   ├── config.py                 # Configuración centralizada
│   ├── utils.py                  # Utilidades (sanitización, fallback, etc)
│   ├── database.py               # Gestión de SQLite
│   ├── logger_config.py          # Sistema de logging
│   ├── test_oficina.py           # Tests automatizados
│   ├── debug_ia.py               # Verificación de sistema (segura)
│   ├── bunker_2026.py            # Prueba modelos Gemini (segura)
│   ├── list_models.py            # Lista modelos disponibles (segura)
│   ├── stress_test.py            # Testing de carga
│   └── oficina_v2.py             # Experimental (respaldo)
│
├── conocimiento/                 # Base de datos de propiedades
│   ├── casa_abuelos.json         # Info completa de la casa
│   ├── disponibilidad.json       # Calendario y tarifas
│   ├── politicas.txt             # Políticas de estancia
│   └── propiedad.txt             # Resumen de característica
│
├── logs/                         # Directorio de logs y datos
│   ├── oficina.log              # Log principal
│   ├── auditoria.log            # Log de auditoría (errores)
│   ├── chats.db                 # Base de datos SQLite
│   ├── reporte_stress_test.json # Resultados de stress test
│   └── metricas.json            # Métricas agregadas
│
├── leads/                        # Gestión de clientes potenciales
├── salidas/                      # Reportes y exports
└── venv/                         # Virtual environment
```

---

## 🔒 Seguridad

### ✅ Mejoras Implementadas

1. **API Keys Seguras**
   - ❌ Antes: Hardcodeadas en archivos Python
   - ✅ Ahora: Variables de entorno en `.env`
   - ✅ Archivos limpios sin credenciales

2. **Sanitización de Entradas**
   ```python
   # Sanitiza automáticamente:
   - Espacios en blanco
   - Caracteres de control
   - Inyección de prompts (básica)
   - Límite de longitud (500 caracteres)
   ```

3. **Control de Acceso a Datos**
   - Base de datos con SQLite (local)
   - Logs con información sensible limitada
   - Auditoría separada de errors

4. **Validación de Fechas**
   - No permite fechas pasadas
   - Valida mínimo de noches
   - Verifica formato correcto

### 🔐 .gitignore Recomendado

```
.env
*.log
*.db
logs/
venv/
__pycache__/
.pytest_cache/
```

---

## 📊 Módulos Destacados

### config.py
Configuración centralizada. Cargar desde `.env`:

```python
from config import GOOGLE_API_KEY, OLLAMA_BASE_URL, CAPACIDAD_MAXIMA
```

**Variables principales:**
- `GOOGLE_API_KEY` - API de Google Gemini
- `OLLAMA_BASE_URL` - URL local de Ollama
- `MAX_CONTEXT_MESSAGES` - Mensajes a mantener en memoria
- `CAPACIDAD_MAXIMA` - Máximo de personas (11)
- `MINIMO_NOCHES` - Estancia mínima (2 noches)

---

### utils.py
Utilidades compartidas:

```python
from utils import (
    sanitizar_pregunta,          # Limpia entrada del usuario
    validar_fechas,              # Valida rango de fechas
    get_llm_vendedor,            # LLM con fallback automático
    get_llm_auditor,             # LLM auditor con fallback
    Metricas                     # Clase para tracking de performance
)
```

---

### database.py
Operaciones de Base de Datos:

```python
from database import (
    guardar_conversacion,        # Guarda chat en DB
    obtener_historial,           # Obtiene últimas conversaciones
    crear_o_actualizar_lead,     # Gestiona leads/prospectos
    guardar_reserva,             # Guarda reserva exitosa
    guardar_metricas             # Guarda métricas del período
)
```

**Tablas:**
- `conversaciones` - Chat histor
- `leads` - Gestión de prospectos
- `reservas` - Reservas confirmadas
- `metricas` - Métricas diarias

---

### logger_config.py
Logging estructurado:

```python
from logger_config import logger, log_consulta, log_error, log_evento

# Registra automáticamente:
# - Cada consulta procesada
# - Errores y excepciones
# - Fallbacks a modelos alternos
# - Eventos del sistema
```

**Archivos generados:**
- `logs/oficina.log` - Log principal
- `logs/auditoria.log` - Detecta anomalías

---

## 🧪 Testing

### Tests Unitarios
```bash
# Instalar pytest si no está
pip install pytest pytest-cov

# Ejecutar todos los tests
pytest scripts/test_oficina.py -v

# Con cobertura
pytest scripts/test_oficina.py --cov
```

### Tests Disponibles
- Sanitización de entrada
- Validación de fechas
- Extracción de fechas en texto
- Limpieza de respuestas
- Métricas y contadores
- Reglas de negocio

---

## 🔧 Solucionar Problemas

### "Ollama no disponible"
```bash
# Asegúrate que Ollama esté corriendo
ollama serve

# O verifica la URL en .env
OLLAMA_BASE_URL=http://localhost:11434
```

### "GOOGLE_API_KEY no configurada"
```bash
# 1. Obtén una API key en https://ai.google.dev/
# 2. Abre .env y reemplaza:
GOOGLE_API_KEY=your-actual-api-key-here

# 3. Luego el fallback funcionará automáticamente
```

### "Error de base de datos"
```bash
# Verifica permisos en /logs
ls -la logs/

# O elimina y recrea la DB
rm logs/chats.db
python scripts/debug_ia.py  # Recrea DB
```

### "ModuleNotFoundError: No module named 'crewai'"
```bash
# Reinstala dependencias
pip install -r requirements.txt --force-reinstall
```

---

## 📈 Monitoreo

### Ver Métricas
```bash
# Archivo de métricas
cat logs/metricas.json | jq

# Ver log principal
tail -f logs/oficina.log

# Ver auditoría específicamente
grep "ERROR\|ALUCINACIÓN" logs/auditoria.log
```

### Estadísticas de Base de Datos
```python
from database import obtener_estadisticas_cliente, obtener_metricas_periodo

# Estadísticas de un cliente
stats = obtener_estadisticas_cliente("cliente_abc123")
print(f"Consultas: {stats['total_consultas']}")
print(f"Exitosas: {stats['consultas_exitosas']}")

# Métricas últimos 7 días
metricas = obtener_metricas_periodo(dias=7)
for dia in metricas:
    print(f"{dia['fecha']}: {dia['tasa_exito']}% de éxito")
```

---

## 🎯 Flujo de Funcionamiento

```
Usuario Ingresa Pregunta
    ↓
[utils.py] Sanitización
    ↓
[oficina_nueva.py] Crew de CrewAI
    ├─ Task Concierge    (Información amenidades)
    ├─ Task Calendario   (Disponibilidad/Costo)
    └─ Task Auditor      (QA y limpieza)
    ↓
[utils.py] Limpieza de respuesta
    ↓
[database.py] Guardar en SQLite
    ↓
[logger_config.py] Log para auditoría
    ↓
Usuario Recibe Respuesta
```

---

## 📋 Optimizaciones Implementadas

| # | Optimización | Estado | Impacto |
|---|---|---|---|
| 1 | API Keys en variables de entorno | ✅ | 🔴 Crítica |
| 2 | Persistencia SQLite | ✅ | 🟠 Alta |
| 3 | Logging estructurado | ✅ | 🟠 Alta |
| 4 | Validación de entrada | ✅ | 🟠 Alta |
| 5 | Fallback inteligente | ✅ | 🟡 Media |
| 6 | Métricas y monitoreo | ✅ | 🟡 Media |
| 7 | Tests automatizados | ✅ | 🟡 Media |
| 8 | Consolidación de código | ✅ | 🟡 Media |

---

## 🚀 Próximas Mejoras Potenciales

### Corto Plazo
- [ ] Dashboard web (Flask/FastAPI + frontend)
- [ ] Webhook para notificaciones
- [ ] Caché de LLM para consultas repetidas
- [ ] Exportación de reportes (PDF/Excel)

### Mediano Plazo
- [ ] Integración con CRM (HubSpot/Salesforce)
- [ ] Bot de WhatsApp/Telegram
- [ ] API REST para terceros
- [ ] Multiidioma (en, fr, pt)

### Largo Plazo
- [ ] Análisis predictivo con ML
- [ ] Fine-tuning de modelo local
- [ ] Integración de pagos
- [ ] Analytics avanzado

---

## 📞 Soporte

Si encuentra problemas:

1. **Verificar el sistema**: `python scripts/debug_ia.py`
2. **Revisar logs**: `tail -f logs/oficina.log`
3. **Checks de auditoría**: `grep ERROR logs/auditoria.log`
4. **Tests**: `pytest scripts/test_oficina.py -v`

---

## 📄 Licencia

Proyecto privado para La Casa de los Abuelos (2026).

---

**Última actualización**: Marzo 16, 2026  
**Versión**: 2.0 (Refactorizada y Optimizada)  
**Estado**: ✅ Producción-Ready
