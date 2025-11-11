#!/usr/bin/env python3
"""
Script de verificación simple: Comprueba que todos los agentes se cargan correctamente
"""

import sys
import os
from pathlib import Path

# Agregar el directorio del proyecto al path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Configurar API key manualmente para el test
os.environ['GOOGLE_API_KEY'] = 'AIzaSyCpSJSt_dW8EOm6TESor5SGt0P3e5YWfKg'

print("=" * 70)
print("VERIFICACIÓN DE CARGA DE AGENTES DATAR")
print("=" * 70)
print()

# Verificar API keys disponibles
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
GOOGLE_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

print("📋 Configuración de API Keys:")
print(f"  OPENROUTER_API_KEY: {'✅ Configurada' if OPENROUTER_KEY else '❌ No disponible'}")
print(f"  GOOGLE_API_KEY: {'✅ Configurada' if GOOGLE_KEY else '❌ No disponible'}")
print()

# Intentar cargar el root_agent
print("🔄 Cargando root_agent...")
try:
    from DATAR.datar.agent import root_agent
    if root_agent is None:
        print("❌ ERROR: root_agent no pudo ser inicializado")
        sys.exit(1)
    print(f"✅ root_agent cargado correctamente")
    print(f"   Nombre: {root_agent.name}")
    print()
except Exception as e:
    print(f"❌ ERROR al cargar root_agent: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Verificar cada sub-agente
print("🔄 Verificando sub-agentes individuales...")
print()

sub_agents_info = [
    ("Gente_Montaña", "DATAR.datar.sub_agents.Gente_Montaña.agent"),
    ("Gente_Pasto", "DATAR.datar.sub_agents.Gente_Pasto.agent"),
    ("Gente_Intuitiva", "DATAR.datar.sub_agents.Gente_Intuitiva.agent"),
    ("Gente_Interpretativa", "DATAR.datar.sub_agents.Gente_Interpretativa.agent"),
    ("Gente_Bosque", "DATAR.datar.sub_agents.Gente_Bosque.agent"),
    ("Gente_Sonora", "DATAR.datar.sub_agents.Gente_Sonora.agent"),
    ("Gente_Horaculo", "DATAR.datar.sub_agents.Gente_Horaculo.agent"),
]

success_count = 0
failed_agents = []

for agent_name, module_path in sub_agents_info:
    try:
        print(f"  {agent_name}...", end=" ")
        module = __import__(module_path, fromlist=['root_agent'])
        agent = getattr(module, 'root_agent')

        if agent is None:
            print(f"❌ FALLÓ")
            failed_agents.append(agent_name)
        else:
            # Verificar el modelo configurado
            model_info = "?"
            if hasattr(agent, 'model'):
                if isinstance(agent.model, str):
                    model_info = agent.model
                elif hasattr(agent.model, 'model'):
                    model_info = agent.model.model

            print(f"✅ OK (modelo: {model_info})")
            success_count += 1
    except Exception as e:
        print(f"❌ ERROR: {str(e)[:50]}")
        failed_agents.append(agent_name)

print()
print("=" * 70)
print(f"✅ {success_count}/{len(sub_agents_info)} agentes cargados correctamente")

if failed_agents:
    print(f"❌ Agentes con errores: {', '.join(failed_agents)}")
    sys.exit(1)
else:
    print("🎉 Todos los agentes funcionan correctamente!")
    sys.exit(0)
