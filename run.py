#!/usr/bin/env python3
"""
Script de inicio rápido para DATAR
Ejecuta el servidor con configuración optimizada

Uso:
    python run.py           # Modo producción
    python run.py --dev     # Modo desarrollo (auto-reload)
    python run.py --help    # Ayuda
"""

import sys
import argparse
from pathlib import Path

# Agregar API al path
API_DIR = Path(__file__).resolve().parent / "API"
sys.path.insert(0, str(API_DIR))


def main():
    parser = argparse.ArgumentParser(
        description="Inicia el servidor DATAR",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python run.py              Modo producción
  python run.py --dev        Modo desarrollo con auto-reload
  python run.py --port 9000  Cambiar puerto
        """
    )

    parser.add_argument(
        "--dev",
        action="store_true",
        help="Modo desarrollo con auto-reload"
    )

    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Puerto del servidor (default: 8000)"
    )

    parser.add_argument(
        "--host",
        type=str,
        default=None,
        help="Host del servidor (default: 0.0.0.0)"
    )

    args = parser.parse_args()

    # Importar después de parsear args para evitar errores de config
    try:
        from config import API_HOST, API_PORT
    except Exception as e:
        print(f"❌ Error al cargar configuración: {e}")
        print("💡 Asegúrate de tener un archivo .env con las API keys necesarias")
        sys.exit(1)

    # Usar valores de argumentos o defaults de config
    host = args.host or API_HOST
    port = args.port or API_PORT
    reload = args.dev

    print("=" * 60)
    print("🌱 DATAR - Sistema Agéntico Ambiental")
    print("    Estructura Ecológica Principal de Bogotá")
    print("=" * 60)
    print()
    print(f"📍 Servidor: http://{host}:{port}")
    print(f"📚 API Docs: http://localhost:{port}/docs")
    print(f"🎨 Frontend: http://localhost:{port}/static/index.html")
    print()
    if reload:
        print("⚡ Modo desarrollo: Auto-reload ACTIVADO")
    else:
        print("🚀 Modo producción")
    print()
    print("=" * 60)
    print()

    # Importar y ejecutar servidor
    import uvicorn

    try:
        uvicorn.run(
            "server:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\n👋 Servidor detenido")
    except Exception as e:
        print(f"\n❌ Error al iniciar servidor: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
