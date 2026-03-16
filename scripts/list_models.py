import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from config import GOOGLE_API_KEY
from logger_config import logger

print("📋 Buscando modelos de Google Gemini...")
print("="*60)

if not GOOGLE_API_KEY or GOOGLE_API_KEY == 'your-google-api-key-here':
    print("❌ GOOGLE_API_KEY no configurada en .env")
    print("\nConfigura tu API key:")
    print("1. Ve a https://ai.google.dev/")
    print("2. Crea una API key")
    print("3. Ponla en .env")
    sys.exit(1)

try:
    import google.generativeai as genai
    genai.configure(api_key=GOOGLE_API_KEY)
    
    print("\n🔍 Modelos disponibles:\n")
    
    modelos = []
    for model in genai.list_models():
        if hasattr(model, 'supported_generation_methods'):
            if 'generateContent' in model.supported_generation_methods:
                modelos.append(model)
                print(f"  • {model.name}")
    
    if modelos:
        print(f"\n✅ {len(modelos)} modelos encontrados")
        print("\n💡 Usa en config.py:")
        print("   GEMINI_MODEL=gemini-1.5-flash")
    else:
        print("\n⚠️  No hay modelos disponibles")

except Exception as e:
    print(f"❌ Error: {e}")
    logger.error(f"Error listando modelos: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("✅ Búsqueda completada")