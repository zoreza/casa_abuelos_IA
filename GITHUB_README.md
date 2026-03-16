# La Casa de los Abuelos - Oficina Virtual IA

Un sistema inteligente multiagente para gestión de reservas y atención al cliente de la propiedad vacacional "La Casa de los Abuelos" en Punta Pérula, Jalisco.

## ✨ Características

- **3 Agentes Especializados**: Concierge, Especialista de Logística, Auditor QA
- **Fallback Inteligente**: Ollama local → Google Gemini automáticamente
- **Persistencia Completa**: SQLite para conversaciones, leads y reservas
- **Logging Estructurado**: Auditoría y debugging con trazabilidad completa
- **Métricas en Tiempo Real**: Monitoreo de performance
- **Validación y Sanitización**: Protección contra inyección de prompts
- **Configuración Segura**: Variables de entorno, sin API keys hardcodeadas

## 🚀 Inicio Rápido

```bash
# 1. Clonar
git clone https://github.com/zoreza/casa_abuelos_IA.git
cd casa_abuelos_IA

# 2. Instalar
pip install -r requirements.txt

# 3. Configurar
cp .env.example .env
nano .env  # Agregar GOOGLE_API_KEY y OLLAMA_BASE_URL

# 4. Ejecutar
python scripts/oficina_nueva.py
```

## 📁 Estructura

```
├── scripts/
│   ├── oficina_nueva.py      ⭐ Principal
│   ├── config.py             🔧 Configuración
│   ├── utils.py              🛠️  Utilidades
│   ├── database.py           💾 Base de datos
│   └── logger_config.py      📝 Logging
├── conocimiento/             📋 Datos de propiedad
├── logs/                     📊 Logs y datos
└── requirements.txt          📦 Dependencias
```

## 📖 Documentación

- [INICIO_RAPIDO.md](INICIO_RAPIDO.md) - Guía rápida (5 minutos)
- [README.md](README.md) - Documentación completa
- [OPTIMIZACIONES_REALIZADAS.md](OPTIMIZACIONES_REALIZADAS.md) - Detalles técnicos
- [ANTES_Y_DESPUES.md](ANTES_Y_DESPUES.md) - Comparación antes/después

## 🔒 Seguridad

✅ API keys en variables de entorno (`.env`)  
✅ No hay credenciales en código  
✅ Sanitización de entrada  
✅ Validación de fechas  
✅ Auditoría de anomalías

## 🧪 Testing

```bash
pytest scripts/test_oficina.py -v
```

## 📊 Stack Tecnológico

- **Python 3.9+**
- **CrewAI** - Orquestación multiagente
- **Ollama** - LLM local (Mistral Nemo)
- **Google Gemini** - LLM fallback
- **SQLite** - Base de datos
- **Pytest** - Testing

## 📝 Licencia

Privado - La Casa de los Abuelos (2026)

---

**Versión**: 2.0 Optimizada  
**Estado**: ✅ Production-Ready
