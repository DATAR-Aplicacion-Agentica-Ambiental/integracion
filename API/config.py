"""
Configuración para DATAR API - Proyecto Integrado
Estructura Ecológica Principal de Bogotá
"""

import os
from pathlib import Path
from typing import Optional, List

from dotenv import load_dotenv

# Rutas del proyecto
API_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = API_DIR.parent
DATAR_DIR = PROJECT_ROOT / "DATAR"
WEB_DIR = PROJECT_ROOT / "WEB"

# Cargar variables de entorno
# Prioridad: variables del sistema > .env del proyecto
load_dotenv(API_DIR / ".env", override=False)
load_dotenv(PROJECT_ROOT / ".env", override=False)

# ============= CONFIGURACIÓN DE API KEYS =============

OPENROUTER_API_KEY: Optional[str] = os.getenv("OPENROUTER_API_KEY")
GOOGLE_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

# ============= CONFIGURACIÓN DEL SERVIDOR =============

API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
# Cloud Run usa PORT, si no está disponible usa API_PORT, si no usa 8000
API_PORT: int = int(os.getenv("PORT", os.getenv("API_PORT", "8000")))
API_ENV: str = os.getenv("API_ENV", "development")
DEBUG: bool = API_ENV == "development"

# CORS - Orígenes permitidos
ALLOWED_ORIGINS: List[str] = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:3000",
    "*"  # En desarrollo, permitir todos
]

# Logging
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

# ============= CONFIGURACIÓN DE AGENTES =============

AGENT_MODEL: str = os.getenv("AGENT_MODEL", "gemini-2.5-flash")
AGENT_NAME: str = os.getenv("AGENT_NAME", "root_agent")

# ============= LÍMITES Y VALIDACIÓN =============

# Mensajes
MAX_MESSAGE_LENGTH: int = int(os.getenv("MAX_MESSAGE_LENGTH", "2000"))
MIN_MESSAGE_LENGTH: int = int(os.getenv("MIN_MESSAGE_LENGTH", "1"))
MAX_RESPONSE_LENGTH: int = int(os.getenv("MAX_RESPONSE_LENGTH", "10000"))

# Rate limiting (futuro)
RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "False").lower() == "true"
RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
RATE_LIMIT_PERIOD: int = int(os.getenv("RATE_LIMIT_PERIOD", "60"))

# ============= VALIDACIÓN DE CONFIGURACIÓN =============

def validate_config():
    """Valida que la configuración sea correcta y muestra advertencias"""
    issues = []
    warnings = []

    # Validar API Keys
    if not GOOGLE_API_KEY and not OPENROUTER_API_KEY:
        issues.append("❌ Se requiere al menos GOOGLE_API_KEY o OPENROUTER_API_KEY")
    elif OPENROUTER_API_KEY:
        print("✅ OPENROUTER_API_KEY configurada - Usando MiniMax para root_agent")
    elif GOOGLE_API_KEY:
        warnings.append("⚠️  Solo GOOGLE_API_KEY disponible - Todos los agentes usarán Gemini")

    # Validar entorno
    if API_ENV not in ["development", "production", "testing"]:
        issues.append(f"❌ API_ENV debe ser 'development', 'production' o 'testing', no '{API_ENV}'")

    # Validar puerto
    if API_PORT < 1 or API_PORT > 65535:
        issues.append(f"❌ API_PORT debe estar entre 1 y 65535, no {API_PORT}")

    # Validar límites
    if MAX_MESSAGE_LENGTH < 1:
        issues.append(f"❌ MAX_MESSAGE_LENGTH debe ser mayor que 0")

    if MAX_RESPONSE_LENGTH < 1:
        issues.append(f"❌ MAX_RESPONSE_LENGTH debe ser mayor que 0")

    # Validar rutas
    if not DATAR_DIR.exists():
        issues.append(f"❌ Directorio DATAR no encontrado en {DATAR_DIR}")

    if not WEB_DIR.exists():
        warnings.append(f"⚠️  Directorio WEB no encontrado en {WEB_DIR} - Frontend no disponible")

    # Mostrar resultados
    if issues:
        print("\n❌ ERRORES DE CONFIGURACIÓN:")
        for issue in issues:
            print(f"   {issue}")
        print()
        return False

    if warnings:
        print("\n⚠️  ADVERTENCIAS:")
        for warning in warnings:
            print(f"   {warning}")
        print()

    # Configuración válida
    print("✅ Configuración validada correctamente")
    print(f"   • Entorno: {API_ENV}")
    print(f"   • Servidor: {API_HOST}:{API_PORT}")
    print(f"   • DATAR: {DATAR_DIR}")
    if WEB_DIR.exists():
        print(f"   • Frontend: {WEB_DIR}")
    print()

    return True


# Ejecutar validación al importar
if __name__ != "__main__":
    if not validate_config():
        import sys
        print("⚠️  La configuración tiene errores. Verifica tus variables de entorno.")
        if API_ENV == "production":
            print("❌ Deteniendo inicio en modo producción debido a errores de configuración")
            sys.exit(1)
