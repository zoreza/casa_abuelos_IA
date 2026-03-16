# 🤖 TELEGRAM BOT - Casa Abuelos IA

Sistema de consultas interactivo para Casa de los Abuelos vía Telegram.

## 🚀 **Quick Start (5 minutos)**

### **Paso 1: Obtener Token de Telegram**

1. Abre **[Telegram](https://web.telegram.org)** (web o móvil)
2. Busca: **`@BotFather`**
3. Escribe: `/newbot`
4. Sigue las instrucciones:
   - **Nombre**: p.ej. "Casa Abuelos Bot"
   - **Username**: p.ej. "casa_abuelos_bot" (debe ser único)
5. **Copia el token** que te devuelve (formato: `123456789:ABCDefGHIJKlmnoPQRSTuvWXYZabcdefgh`)

### **Paso 2: Configurar Token en .env**

```bash
cd /home/oficina_ia/oficina_abuelos

# Editar .env y reemplazar el token
sed -i 's/your-telegram-bot-token-here/TU_TOKEN_AQUI/' .env

# O editar manualmente:
# Abre .env y cambia:
# TELEGRAM_BOT_TOKEN=your-telegram-bot-token-here
# Por:
# TELEGRAM_BOT_TOKEN=123456789:ABCDefGHIJKlmnoPQRSTuvWXYZabcdefgh
```

### **Paso 3: Lanzar el Bot**

```bash
cd /home/oficina_ia/oficina_abuelos
bash deploy_telegram.sh
```

O directamente:

```bash
python3 scripts/telegram_bot.py
```

---

## 📱 **Usando el Bot**

### **En Telegram:**

1. Busca tu bot por @username (p.ej. @casa_abuelos_bot)
2. Escribe `/start` para comenzar
3. Haz tus preguntas normalmente

### **Comandos Disponibles:**

| Comando | Descripción |
|---------|------------|
| `/start` | Mensaje de bienvenida e instrucciones |
| `/help` | Guía de comandos |
| `/stats` | Ver tus estadísticas de consultas |
| `/historial` | Ver últimas 5 consultas realizadas |
| `/nuevo` | Iniciar nueva sesión (limpiar historial) |

### **Ejemplos de Preguntas:**

- ✅ "¿Tienen disponible del 20 al 23 de marzo para 6 personas?"
- ✅ "¿Cuánto cuesta por noche en mayo?"
- ✅ "¿Aceptan mascotas en las habitaciones?"
- ✅ "¿Qué amenidades tiene la casa?"
- ✅ "¿A cuántos minutos está la playa?"

---

## 🔧 **Características Técnicas**

### **Arquitectura**

```
┌─ Telegram Bot (polling)
│  └─ Usuario envía pregunta
│     ├─ Sanitización de entrada
│     ├─ Agent 1: Concierge (Amenidades)
│     ├─ Agent 2: Logística (Fechas/Costos)
│     └─ Agent 3: Auditor (Validación)
│        └─ Respuesta final integrada
│           └─ Guardada en BD + Logger
└─ Respuesta enviada a Telegram en 2-3 minutos
```

### **Flujo de Datos**

1. **Usuario** → Escribe pregunta en Telegram
2. **Bot** → Recibe vía polling (sin necesidad de IP pública)
3. **Sanitización** → Validación de entrada
4. **Crew AI** → 3 agentes procesan en paralelo:
   - Concierge busca información general
   - Logística verifica disponibilidad y calcula costos
   - Auditor valida y ensambla respuesta final
5. **BD** → Conversación guardada para historial
6. **Telegram** → Respuesta enviada al usuario

### **Datos Almacenados**

- Usuario ID
- Pregunta + Respuesta
- Timestamp
- Tiempo de procesamiento
- Modelo usado
- Éxito/Error

---

## 📊 **Información de la Propiedad**

El bot tiene acceso a:

- **Amenidades**: Starlink 200MB/s, A/C, TV 4K, internet
- **Capacidad**: Máximo 11 personas
- **Tarifas**: $3,500 (baja) / $4,500 (alta temporada)
- **Disponibilidad**: Últimas actualizaciones de disponibilidad.json
- **Políticas**: Reglas, cancelaciones, mascotas

---

## 🛠️ **Troubleshooting**

### **"Token error" o no conecta**

```bash
# Verificar que el token está correcto en .env
grep TELEGRAM_BOT_TOKEN .env

# Probar que python-telegram-bot está instalado
python3 -c "import telegram; print('OK')"
```

### **Bot no responde**

1. Verifica que `deploy_telegram.sh` está executándose
2. Revisa logs: `tail -f logs/telegram_bot.log`
3. Verifica que Ollama está disponible: `python3 -c "from scripts.utils import verificar_ollama_disponible; print(verificar_ollama_disponible())"`

### **Respuestas lentas (2-3 minutos)**

Normal. El sistema procesa 3 agentes en paralelo:
- Espera es causada por Ollama/LLM generando respuesta
- Tiempo típico: 120-180 segundos
- Se optimizará en futuras versiones

### **Respuesta truncada**

Si Telegram trunca la respuesta:
1. Es un límite de Telegram (4096 caracteres por mensaje)
2. El bot divide automáticamente en múltiples mensajes
3. Usa `/historial` para ver la conversación completa

---

## 🐛 **Logs y Debugging**

### **Ver logs del bot**

```bash
tail -f /home/oficina_ia/oficina_abuelos/logs/telegram_bot.log
```

### **Ver logs del programa**

```bash
tail -f /home/oficina_ia/oficina_abuelos/logs/oficina.log
```

### **Ver base de datos de conversaciones**

```bash
sqlite3 /home/oficina_ia/oficina_abuelos/logs/chats.db "SELECT * FROM conversaciones LIMIT 5;"
```

---

## 🔐 **Seguridad**

- ✅ Token guardado en `.env` (no en código)
- ✅ Usuario ID aislado (no se mezclan datos)
- ✅ Historial persistente por usuario
- ✅ Logs almacenados localmente
- ✅ Sin API keys expuestas

---

## 📈 **Monitoreo**

### **Ver estadísticas en el bot**

Comando `/stats` muestra:
- Total de consultas
- Consultas exitosas
- Tiempo promedio
- Tasa de éxito

### **Histórico de conversaciones**

Comando `/historial` muestra:
- Últimas 5 consultas
- Timestamps
- Preguntas originales

---

## 🚀 **Deployment a Producción**

### **Opción 1: Screen (Simple, para desarrollo)**

```bash
cd /home/oficina_ia/oficina_abuelos
screen -S telegram_bot python3 scripts/telegram_bot.py
# Ctrl+A luego D para detener
```

### **Opción 2: Systemd (Producción)**

Crear archivo `/etc/systemd/system/telegram-bot.service`:

```ini
[Unit]
Description=Casa Abuelos Telegram Bot
After=network.target

[Service]
Type=simple
User=oficina_ia
WorkingDirectory=/home/oficina_ia/oficina_abuelos
ExecStart=/usr/bin/python3 /home/oficina_ia/oficina_abuelos/scripts/telegram_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Luego:

```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
sudo systemctl status telegram-bot
```

### **Opción 3: Supervisor**

```bash
pip3 install supervisor
# Configurar /etc/supervisor/conf.d/telegram-bot.conf
supervisorctl reload
supervisorctl start telegram-bot
```

---

## 📞 **Soporte**

Para issues o preguntas:
- Revisa los logs: `tail -f logs/telegram_bot.log`
- Verifica que el token es correcto en `.env`
- Asegúrate de que Ollama está funcionando
- Prueba `/help` en Telegram

---

**Versión**: 2.0  
**Última actualización**: Marzo 16, 2026  
**Estado**: ✅ Producción Lista
