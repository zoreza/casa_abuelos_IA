#!/bin/bash
# 🚀 DEPLOY SCRIPT - Telegram Bot Casa Abuelos IA
# Este script configura y lanza el bot de Telegram

set -e

echo ""
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║  🚀 DEPLOY - TELEGRAM BOT - CASA ABUELOS IA                                ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 1. Verificar que estamos en el directorio correcto
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ Archivo .env no encontrado. Asegúrate de estar en /home/oficina_ia/oficina_abuelos${NC}"
    exit 1
fi

echo -e "${BLUE}📁 Directorio: $(pwd)${NC}"
echo ""

# 2. Verificar si el token está configurado
TELEGRAM_TOKEN=$(grep "TELEGRAM_BOT_TOKEN=" .env | cut -d'=' -f2)

if [[ "$TELEGRAM_TOKEN" == "your-telegram-bot-token-here" ]] || [[ -z "$TELEGRAM_TOKEN" ]]; then
    echo -e "${YELLOW}⚠️  TELEGRAM_BOT_TOKEN no está configurado${NC}"
    echo ""
    echo -e "${BLUE}📱 INSTRUCCIONES PARA OBTENER EL TOKEN:${NC}"
    echo ""
    echo "  1. Abre Telegram en tu teléfono o web (web.telegram.org)"
    echo "  2. Busca a ${BLUE}@BotFather${NC}"
    echo "  3. Escribe: ${BLUE}/newbot${NC}"
    echo "  4. Sigue las instrucciones (nombre de bot, username único)"
    echo "  5. Copia el token (formato: 123456:ABC-DEF1234...)"
    echo ""
    echo -e "${YELLOW}✏️  Luego ejecuta:${NC}"
    echo ""
    echo "  cd /home/oficina_ia/oficina_abuelos"
    echo "  sed -i 's/your-telegram-bot-token-here/TU_TOKEN_AQUI/' .env"
    echo ""
    echo "  Donde TU_TOKEN_AQUI es el token de @BotFather"
    echo ""
    exit 1
fi

echo -e "${GREEN}✅ Token de Telegram configurado${NC}"
echo ""

# 3. Verificar dependencias
echo -e "${BLUE}🔍 Verificando dependencias...${NC}"
python3 -c "import telegram; print('✅ python-telegram-bot disponible')" || {
    echo -e "${RED}❌ python-telegram-bot no está instalado${NC}"
    echo "   Instala con: pip3 install --break-system-packages python-telegram-bot"
    exit 1
}

python3 -c "from crewai import Agent; print('✅ CrewAI disponible')" || {
    echo -e "${RED}❌ CrewAI no está instalado${NC}"
    exit 1
}

echo ""

# 4. Verificar base de datos
echo -e "${BLUE}🗄️  Verificando base de datos...${NC}"
cd /home/oficina_ia/oficina_abuelos/scripts
python3 -c "from database import inicializar_db; inicializar_db(); print('✅ Base de datos lista')" || {
    echo -e "${RED}❌ Error con la base de datos${NC}"
    exit 1
}
cd /home/oficina_ia/oficina_abuelos

echo ""

# 5. Verificar Ollama
echo -e "${BLUE}📡 Verificando Ollama...${NC}"
cd /home/oficina_ia/oficina_abuelos/scripts
python3 << 'PYTHON_EOF'
from utils import verificar_ollama_disponible
if verificar_ollama_disponible():
    print('✅ Ollama disponible')
else:
    print('⚠️  Ollama no disponible (usará Gemini)')
PYTHON_EOF
cd /home/oficina_ia/oficina_abuelos

echo ""

# 6. Listo para iniciar
echo -e "${GREEN}🚀 BOT LISTO PARA INICIAR...${NC}"
echo ""
echo -e "${BLUE}📱 Para usar el bot en Telegram:${NC}"
echo "  1. Abre Telegram"
echo "  2. Busca a tu bot por username (@TuUsername)"
echo "  3. Escribe /start para comenzar"
echo "  4. Haz tus preguntas sobre Casa de los Abuelos"
echo ""
echo -e "${YELLOW}📝 COMANDOS DISPONIBLES:${NC}"
echo "  /start     - Mensaje de bienvenida"
echo "  /help      - Guía de comandos"
echo "  /stats     - Ver tus estadísticas"
echo "  /historial - Ver últimas consultas"
echo "  /nuevo     - Iniciar nueva sesión"
echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""
echo -e "${GREEN}✅ VERIFICACIONES COMPLETADAS - BOT LISTA A EJECUTARSE${NC}"
echo ""
echo -e "${BLUE}🚀 PARA INICIAR EL BOT, EJECUTA:${NC}"
echo ""
echo "   cd /home/oficina_ia/oficina_abuelos/scripts"
echo "   python3 telegram_bot.py"
echo ""
echo "   O simplemente:"
echo "   python3 /home/oficina_ia/oficina_abuelos/scripts/telegram_bot.py"
echo ""
echo -e "${YELLOW}⏸️  Para detener el bot, presiona Ctrl+C${NC}"
echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""
echo -e "${GREEN}✨ Deploy completado exitosamente${NC}"
