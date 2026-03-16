import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from config import GOOGLE_API_KEY, OLLAMA_BASE_URL
from utils import verificar_ollama_disponible
from logger_config import logger

print("🔍 Verificación de sistema...")
print("="*60)

print("\n✓ CHECK 1: Configuración de API Key")
if GOOGLE_API_KEY and GOOGLE_API_KEY != 'your-google-api-key-here':
    print("✅ Google API Key está configurada")
else:
    print("⚠️  Google API Key no configurada. Agrega a .env")

print("\n✓ CHECK 2: Disponibilidad de Ollama")
if verificar_ollama_disponible():
    print(f"✅ Ollama disponible en {OLLAMA_BASE_URL}")
else:
    print(f"⚠️  Ollama no disponible en {OLLAMA_BASE_URL}")

print("\n" + "="*60)
print("✅ Verificación completada")
print("\n📖 Próximos pasos:")
print("   1. Completa GOOGLE_API_KEY en .env si deseas usar Gemini como fallback")
print("   2. Ejecuta: python scripts/oficina_nueva.py")