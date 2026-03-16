import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from config import GOOGLE_API_KEY
from logger_config import logger

print("🚀 Iniciando búnker de emergencia...")
print("="*60)

if not GOOGLE_API_KEY or GOOGLE_API_KEY == 'your-google-api-key-here':
    print("❌ GOOGLE_API_KEY no configurada en .env")
    print("\nConfigura tu API key primero:")
    print("1. Abre .env")
    print("2. Reemplaza el placeholder con tu API key")
    print("3. Guarda el archivo")
    sys.exit(1)

try:
    import google.generativeai as genai
    genai.configure(api_key=GOOGLE_API_KEY)
    
    modelos = ['gemini-1.5-flash', 'gemini-1.5-pro']
    
    for modelo_id in modelos:
        try:
            print(f"\n🔍 Probando {modelo_id}...", end=" ")
            model = genai.GenerativeModel(modelo_id)
            response = model.generate_content("¿Estás ahí?")
            print(f"✅ ¡ÉXITO!")
            print(f"\n✨ Usa en config.py: {modelo_id}")
            logger.info(f"✅ Gemini {modelo_id} disponible")
            break
        except Exception as e:
            print(f"❌ Falló: {type(e).__name__}")

except Exception as e:
    print(f"❌ Error inesperado: {e}")
    logger.error(f"Error en búnker: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("✅ Búnker configurado correctamente")