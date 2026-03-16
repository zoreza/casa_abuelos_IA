# 🚀 GUÍA DE INICIO RÁPIDO

## ⚡ 5 Pasos para Iniciar (5 minutos)

### Paso 1: Verificar Python ✅
```bash
python3 --version
# Output: Python 3.9+ (recomendado 3.10+)
```

### Paso 2: Instalar Dependencias ✅
```bash
cd /home/oficina_ia/oficina_abuelos
pip install -r requirements.txt
```

### Paso 3: Configurar Variables (IMPORTANTE!) ⚠️
```bash
# Editar .env
nano .env

# Completa MÍNIMO esto:
GOOGLE_API_KEY=your-actual-api-key-here  # OPCIONAL si tienes Ollama
OLLAMA_BASE_URL=http://localhost:11434    # Tu URL local

# CTRL+O, Enter, CTRL+X para guardar en nano
```

### Paso 4: Verificar Sistema ✅
```bash
python scripts/debug_ia.py

# Debería mostrar:
# ✅ CHECK 1: Configuración de API Key
# ✅ CHECK 2: Disponibilidad de Ollama
# ✅ CHECK 3: Estructura de directorios
# ✅ CHECK 4: Archivos de conocimiento
# ✅ CHECK 5: Base de datos
# ✅ CHECK 6: Sistema de logging
# ✅ CHECK 7: Sistema de métricas
```

### Paso 5: Ejecutar! 🚀
```bash
python scripts/oficina_nueva.py

# Output esperado:
# 📚 Cargando base de conocimiento...
# ✅ Base de conocimiento cargada
# 🤖 Inicializando agentes...
# ✅ Agentes configurados
# ═══════════════════════════════════════════════════════════════════
# 🤖 Servidor de La Casa de los Abuelos INICIADO (v2.0)
# Escribe 'salir' para apagar el bot.
# ═══════════════════════════════════════════════════════════════════
#
# 👤 Cliente: _
```

---

## 💬 Ejemplo de Uso

Una vez iniciado el server:

```
👤 Cliente: ¿Cuáles son las amenidades principales?

⏳ Procesando (Concierge -> Logística -> QA)...

🤖 Bot: La Casa de los Abuelos ofrece varias amenidades destacadas:

- Starlink de 200 MB/s para internet de alta velocidad
- Aire acondicionado en todas las habitaciones
- 3 habitaciones con capacidad para 11 personas
- TV 4K con acceso a streaming
- Cocina equipada con cafetera, estufa y refrigerador
- Estacionamiento privado para hasta 10 vehículos

Estamos ubicados a solo 2 cuadras de la playa (12 minutos a pie). 
¿Le gustaría conocer más sobre disponibilidad o hacer una reserva?

─────────────────────────────────────────────────────────────────

👤 Cliente: ¿Cuánto cuesta si voy del 20 al 25 de abril?

⏳ Procesando (Concierge -> Logística -> QA)...

🤖 Bot: Para una estancia del 20 al 25 de abril (5 noches):

📅 Fechas: 20/04/2026 - 25/04/2026
🏠 Noches: 5
💰 Tarifa: $3,500 MXN por noche (Temporada Baja)
🧮 Costo Total: $17,500 MXN
📋 Apartado (1 noche): $3,500 MXN

Las fechas están disponibles. Para proceder con la reserva, 
por favor contacte a nuestro especialista de logística.

─────────────────────────────────────────────────────────────────

👤 Cliente: salir

🔌 Apagando el servidor...

═════════════════════════════════════════════════════════════════════
📊 RESUMEN DE SESIÓN
═════════════════════════════════════════════════════════════════════
{
  "total_consultas": 2,
  "consultas_correctas": 2,
  "consultas_error": 0,
  "tiempo_promedio_respuesta": 2.35,
  "tasa_exito_porcentaje": 100.0,
  "modelos_usados": {
    "ollama": 2,
    "gemini": 0
  },
  "tiempo_ejecucion_total_minutos": 3.25
}

✅ Servidor apagado correctamente
```

---

## 📂 Estructura Archivos Clave

```
scripts/
├── oficina_nueva.py          ⭐ PRINCIPAL - Ejecutar esto
├── config.py                 🔧 Configuración (@importar)
├── utils.py                  🛠️  Utilidades (@importar)
├── database.py               💾 Base de datos (@importar)
├── logger_config.py          📝 Logging (@importar)
├── test_oficina.py           🧪 Tests (@ejecutar)
├── debug_ia.py               🔍 Verificación (@ejecutar)
└── bunker_2026.py            🚂 Prueba Gemini (@ejecutar)

conocimiento/
├── casa_abuelos.json         📋 Info de la propiedad
├── disponibilidad.json       📅 Calendario y tarifas
└── (politicas.txt, propiedad.txt)

logs/
├── oficina.log               📄 Log principal
├── auditoria.log             🔍 Log de auditoría
├── chats.db                  💾 Base de datos SQLite
└── metricas.json             📊 Métricas

.env                          🔐 Variables (NO COMMITEAR)
.env.example                  📝 Plantilla para .env
requirements.txt              📦 Dependencias
README.md                      📖 Documentación completa
OPTIMIZACIONES_REALIZADAS.md  ✨ Detalles de cambios
```

---

## 🔧 Comandos Útiles

### Ejecutar la Aplicación
```bash
python scripts/oficina_nueva.py
```

### Verificar Sistema
```bash
python scripts/debug_ia.py
```

### Ejecutar Tests
```bash
pytest scripts/test_oficina.py -v
pytest scripts/test_oficina.py --cov  # Con cobertura
```

### Ver Logs
```bash
tail -f logs/oficina.log                    # Log principal
tail -f logs/auditoria.log                  # Auditoría
grep "ERROR" logs/auditoria.log             # Solo errores
```

### Inspeccionar Base de Datos
```bash
sqlite3 logs/chats.db

# Luego dentro de sqlite3:
.tables
SELECT COUNT(*) FROM conversaciones;
SELECT * FROM leads;
SELECT * FROM metricas ORDER BY fecha DESC;
.quit
```

### Ver Métricas
```bash
cat logs/metricas.json | jq
```

---

## ⚠️ Problemas Comunes

### "ModuleNotFoundError: No module named 'crewai'"
```bash
# Solución: Reinstalar dependencias
pip install -r requirements.txt --force-reinstall
```

### "ConnectionRefusedError: Ollama no disponible"
```bash
# Opción 1: Iniciar Ollama
ollama serve

# Opción 2: Usa Google Gemini como fallback
# Configura GOOGLE_API_KEY en .env
```

### "GOOGLE_API_KEY no configurada"
```bash
# 1. Ve a https://ai.google.dev/
# 2. Crea una API key
# 3. Abre .env y reemplaza:
GOOGLE_API_KEY=tu-clave-aqui
```

### "Base de datos corrompida"
```bash
# Solución: Recrear
rm logs/chats.db
python scripts/debug_ia.py  # Recrea automáticamente
```

---

## 📊 Monitoreo En Vivo

### Terminal 1: Ejecutar servidor
```bash
python scripts/oficina_nueva.py
```

### Terminal 2: Ver logs en tiempo real
```bash
tail -f logs/oficina.log
```

### Terminal 3: Revisar auditoría
```bash
tail -f logs/auditoria.log
```

---

## 🎯 Checklist de Configuración

- [ ] Python 3.9+ instalado
- [ ] `pip install -r requirements.txt` ejecutado
- [ ] `.env` completado (MÍNIMO GOOGLE_API_KEY)
- [ ] `python scripts/debug_ia.py` sin errores
- [ ] Ollama corriendo EN OTRA TERMINAL (opcional)
- [ ] Ejecutar `python scripts/oficina_nueva.py`
- [ ] Probar con preguntas simples
- [ ] Revisar `logs/oficina.log` para asegurar logging

---

## 📈 Próximos Pasos Después de Iniciar

### Corto Plazo
1. Ejecutar tests: `pytest scripts/test_oficina.py -v`
2. Revisar logs generados
3. Probar fallback (apagar Ollama, verificar Gemini funciona)
4. Inspeccionar base de datos con `sqlite3`

### Mediano Plazo
1. Exportar datos de leads
2. Crear reportes de métricas
3. Escalar a múltiples usuarios
4. Fine-tuning de prompts de agentes

### Largo Plazo
1. Migrar a API REST
2. Crear panel dashboard
3. Integración WhatsApp/Telegram
4. Machine Learning para predicciones

---

## 💡 Tips Importantes

1. **Nunca** commitees `.env` a Git (agregar a `.gitignore`)
2. **Siempre** usa `venv` para aislar dependencias
3. **Revisa** `logs/auditoria.log` regularmente
4. **Monitorea** tasa de éxito en `logs/metricas.json`
5. **Mantén** `.env.example` actualizado sin credenciales

---

## 🆘 Soporte

Si algo falla:

1. Ejecuta verificación: `python scripts/debug_ia.py`
2. Revisa logs: `tail -f logs/oficina.log`
3. Verifica .env completado
4. Prueba tests: `pytest scripts/test_oficina.py -v`
5. Si persiste, revisa README.md sección "Solucionar Problemas"

---

**¡Listo para iniciar! 🎉**  
**Versión**: 2.0 Optimizada  
**Estado**: ✅ Production-Ready
