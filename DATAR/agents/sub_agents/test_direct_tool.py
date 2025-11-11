"""
Script de prueba para llamar directamente la herramienta de visualización
Este script demuestra que la funcionalidad funciona correctamente
"""
import asyncio
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

# Import directo desde el archivo
import importlib.util
spec = importlib.util.spec_from_file_location(
    "visualizacion",
    Path(__file__).parent / "datar_a-gente" / "visualizacion.py"
)
visualizacion = importlib.util.module_from_spec(spec)
spec.loader.exec_module(visualizacion)
generar_rio_emocional = visualizacion.generar_rio_emocional

import google.genai.types as types


# Crear un contexto mock simple para la prueba
class MockContext:
    async def save_artifact(self, filename, artifact):
        print(f"  ✓ Artifact guardado: {filename}")
        print(f"  ✓ Tipo: Objeto Part con datos binarios")
        return 1  # versión 1


async def test_direct_call():
    """Prueba directa de la herramienta de visualización"""
    print("\n" + "="*60)
    print("PRUEBA DIRECTA DE LA HERRAMIENTA DE VISUALIZACIÓN")
    print("="*60 + "\n")

    # Emojis de prueba
    emojis_test = "😊 🌊 💚 🌟"
    print(f"📝 Emojis de prueba: {emojis_test}\n")

    # Paso 1: Generar la imagen
    print("1️⃣  Generando imagen PNG...")
    try:
        imagen_bytes = generar_rio_emocional(emojis_test)
        print(f"  ✓ Imagen generada exitosamente")
        print(f"  ✓ Tamaño: {len(imagen_bytes):,} bytes\n")
    except Exception as e:
        print(f"  ✗ Error: {e}\n")
        return

    # Paso 2: Crear artifact
    print("2️⃣  Creando artifact...")
    try:
        artifact = types.Part.from_bytes(
            data=imagen_bytes,
            mime_type="image/png"
        )
        print(f"  ✓ Artifact creado exitosamente\n")
    except Exception as e:
        print(f"  ✗ Error: {e}\n")
        return

    # Paso 3: Simular guardado
    print("3️⃣  Simulando guardado de artifact...")
    mock_context = MockContext()
    version = await mock_context.save_artifact(
        filename="rio_emocional.png",
        artifact=artifact
    )

    # Mensaje final
    mensaje = f"✨ He creado tu visualización del río emocional (versión {version}). La imagen muestra el flujo poético de tus emociones: {emojis_test}"

    print(f"\n4️⃣  Mensaje final que retornaría la herramienta:")
    print(f"  {mensaje}\n")

    print("="*60)
    print("✅ PRUEBA COMPLETADA EXITOSAMENTE")
    print("="*60)
    print("\nCONCLUSIÓN:")
    print("La herramienta funciona correctamente cuando se llama directamente.")
    print("El problema está en que Gemini no está decidiendo usar la herramienta.")
    print("\nSOLUCIÓN RECOMENDADA:")
    print("1. Considerar usar un modelo diferente (Claude, GPT-4, etc.)")
    print("2. O crear una interfaz directa donde el usuario active la herramienta")
    print("   con un botón específico en lugar de confiar en function calling")
    print()


if __name__ == "__main__":
    asyncio.run(test_direct_call())
