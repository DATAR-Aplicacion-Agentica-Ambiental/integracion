"""
Orquestador de Agentes para DATAR - Proyecto Integrado
Coordina la interacción entre los diferentes agentes del sistema
Adaptado de adk-prueba-main para la nueva estructura integrada
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from google.adk.runners import InMemoryRunner
from google.genai.types import Part, Content

# Añadir el directorio raíz del proyecto al path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Importar los agentes desde DATAR
from DATAR.agents.sub_agents import Gente_Montaña
from DATAR.agents.sub_agents.agentHierba.agent import root_agent as PastoBogotano
from DATAR.agents.sub_agents.datar_a_gente.agent import root_agent as DiarioIntuitivo
from DATAR.agents.sub_agents.GuatilaM.agent import root_agent as SequentialPipelineAgent
from DATAR.agents.sub_agents.LinaPuerto.agent import root_agent as agente_bosque
from DATAR.agents.sub_agents.Sebastian1022.agent import root_agent as agente_sonido
from DATAR.agents.sub_agents.ZolsemiYa.agent import root_agent as horaculo

# Diccionario de agentes disponibles con metadata
AGENTES = {
    "gente_montana": {
        "nombre": "Gente Montaña",
        "descripcion": "Un agente que siempre saluda desde la Montaña",
        "agente": Gente_Montaña,
        "color": "#8B4513",
        "emoji": "🏔️"
    },
    "pasto_bogotano": {
        "nombre": "PastoBogotano",
        "descripcion": "Agente especializado en pastos y vegetación",
        "agente": PastoBogotano,
        "color": "#90EE90",
        "emoji": "🌿"
    },
    "diario_intuitivo": {
        "nombre": "Diario Intuitivo",
        "descripcion": "Crea visualizaciones intuitivas y diarios emocionales",
        "agente": DiarioIntuitivo,
        "color": "#FF69B4",
        "emoji": "📔"
    },
    "guatila_m": {
        "nombre": "GuatilaM",
        "descripcion": "Pipeline secuencial con respuestas normales y emoji",
        "agente": SequentialPipelineAgent,
        "color": "#FFD700",
        "emoji": "🥒"
    },
    "agente_bosque": {
        "nombre": "Agente Bosque",
        "descripcion": "Especialista en ecosistemas forestales y PDF",
        "agente": agente_bosque,
        "color": "#228B22",
        "emoji": "🌲"
    },
    "agente_sonido": {
        "nombre": "Agente Sonido (Sebastian1022)",
        "descripcion": "Genera representaciones biocéntricas: Turtle, ASCII/Morse, NumPy audio",
        "agente": agente_sonido,
        "color": "#4169E1",
        "emoji": "🎵"
    },
    "horaculo": {
        "nombre": "Oráculo",
        "descripcion": "Agente oráculo con perspectivas profundas",
        "agente": horaculo,
        "color": "#9370DB",
        "emoji": "🔮"
    }
}


class AgentOrchestrator:
    """
    Orquestador que coordina la interacción entre múltiples agentes.
    Permite seleccionar agentes específicos y mantener sesiones separadas.
    """

    def __init__(self):
        """Inicializa el orquestador con todos los agentes disponibles"""
        self.agentes = AGENTES
        self.agente_activo = None  # ID del agente actualmente seleccionado
        self.historial_conversacion = []  # Historial global de conversaciones

        # Crear runners para cada agente
        self.runners: Dict[str, InMemoryRunner] = {}
        self.sessions: Dict[str, Any] = {}  # Sesiones por agente

        print("🔧 Inicializando orquestador de agentes...")
        for agente_id, agente_info in self.agentes.items():
            if agente_info["agente"] is not None:
                try:
                    self.runners[agente_id] = InMemoryRunner(agent=agente_info["agente"])
                    print(f"   ✅ Runner creado para: {agente_info['nombre']}")
                except Exception as e:
                    print(f"   ⚠️ Error al crear runner para {agente_id}: {e}")

        print(f"✅ Orquestador listo con {len(self.runners)} agentes activos\n")

    def obtener_lista_agentes(self) -> List[Dict[str, Any]]:
        """
        Retorna la lista de agentes disponibles con su metadata

        Returns:
            Lista de diccionarios con info de cada agente
        """
        return [
            {
                "id": key,
                "nombre": value["nombre"],
                "descripcion": value["descripcion"],
                "color": value["color"],
                "emoji": value.get("emoji", "🤖"),
                "disponible": key in self.runners
            }
            for key, value in self.agentes.items()
        ]

    def seleccionar_agente(self, agente_id: str) -> Dict[str, Any]:
        """
        Selecciona un agente específico para la conversación

        Args:
            agente_id: ID del agente a seleccionar

        Returns:
            Diccionario con información sobre la selección
        """
        if agente_id not in self.agentes:
            return {
                "exitoso": False,
                "error": f"Agente '{agente_id}' no encontrado. Agentes disponibles: {', '.join(self.agentes.keys())}"
            }

        if agente_id not in self.runners:
            return {
                "exitoso": False,
                "error": f"Agente '{agente_id}' no está disponible (runner no inicializado)"
            }

        self.agente_activo = agente_id
        agente_info = self.agentes[agente_id]

        # Mensaje de bienvenida personalizado según el agente
        mensaje_bienvenida = f"¡Hola! Soy {agente_info['nombre']}. {agente_info['descripcion']}. ¿En qué puedo ayudarte?"

        return {
            "exitoso": True,
            "agente": agente_info["nombre"],
            "agente_id": agente_id,
            "descripcion": agente_info["descripcion"],
            "mensaje": mensaje_bienvenida,
            "color": agente_info["color"],
            "emoji": agente_info.get("emoji", "🤖")
        }

    async def procesar_mensaje(self, mensaje: str, agente_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Procesa un mensaje y lo enruta al agente apropiado

        Args:
            mensaje: Mensaje del usuario
            agente_id: ID del agente específico (opcional, usa el activo si no se especifica)

        Returns:
            Respuesta del agente con metadata
        """
        try:
            # Determinar qué agente usar
            if agente_id:
                target_agent = agente_id
            elif self.agente_activo:
                target_agent = self.agente_activo
            else:
                return {
                    "exitoso": False,
                    "error": "No hay ningún agente seleccionado. Por favor, selecciona un agente primero usando el endpoint /select-agent."
                }

            if target_agent not in self.agentes:
                return {
                    "exitoso": False,
                    "error": f"Agente '{target_agent}' no encontrado"
                }

            if target_agent not in self.runners:
                return {
                    "exitoso": False,
                    "error": f"Agente '{target_agent}' no está disponible (runner no inicializado)"
                }

            # Obtener el agente y su runner
            agente_info = self.agentes[target_agent]
            runner = self.runners[target_agent]

            # Crear o recuperar sesión para este agente específico
            if target_agent not in self.sessions:
                try:
                    self.sessions[target_agent] = await runner.session_service.create_session(
                        app_name=runner.app_name,
                        user_id="default_user"
                    )
                    print(f"📝 Sesión creada para {agente_info['nombre']}")
                except Exception as e:
                    print(f"⚠️ Error creando sesión para {target_agent}: {e}")
                    return {
                        "exitoso": False,
                        "error": f"Error al crear sesión para el agente: {str(e)}"
                    }

            session = self.sessions[target_agent]

            # INYECTAR INSTRUCCIÓN DEL SISTEMA EN CADA MENSAJE
            # Prefijamos el mensaje del usuario con la instrucción del agente
            agente_obj = agente_info["agente"]
            mensaje_completo = mensaje

            if hasattr(agente_obj, 'instruction') and agente_obj.instruction:
                # Solo añadir instrucción en el primer mensaje de la sesión
                # o si el historial está vacío
                session_history = await runner.session_service.get_history(
                    user_id=session.user_id,
                    session_id=session.id
                )

                if not session_history or len(session_history.turns) == 0:
                    # Es el primer mensaje, incluir instrucción completa
                    mensaje_completo = f"{agente_obj.instruction}\n\n---\n\nUsuario: {mensaje}"
                    print(f"🎭 Inyectando instrucción del sistema para {agente_info['nombre']}")

            # Crear el contenido del mensaje
            content = Content(parts=[Part(text=mensaje_completo)], role="user")

            # Ejecutar el agente y recolectar la respuesta
            respuesta_texto = ""
            try:
                for event in runner.run(
                    user_id=session.user_id,
                    session_id=session.id,
                    new_message=content
                ):
                    # Extraer el texto de la respuesta
                    if hasattr(event, 'content') and hasattr(event.content, 'parts'):
                        for part in event.content.parts:
                            if hasattr(part, 'text') and part.text:
                                respuesta_texto += part.text
            except Exception as e:
                print(f"❌ Error ejecutando agente {target_agent}: {e}")
                return {
                    "exitoso": False,
                    "error": f"Error al ejecutar el agente: {str(e)}"
                }

            # Si no hay respuesta, usar un mensaje por defecto
            if not respuesta_texto or not respuesta_texto.strip():
                respuesta_texto = f"[{agente_info['nombre']}] procesó tu mensaje, pero no generó una respuesta de texto."

            # Construir la respuesta
            respuesta = {
                "exitoso": True,
                "agente": agente_info["nombre"],
                "agente_id": target_agent,
                "mensaje": respuesta_texto.strip(),
                "color": agente_info["color"],
                "emoji": agente_info.get("emoji", "🤖")
            }

            # Guardar en historial
            self.historial_conversacion.append({
                "agente": target_agent,
                "agente_nombre": agente_info["nombre"],
                "usuario": mensaje,
                "respuesta": respuesta_texto.strip()
            })

            return respuesta

        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"❌ Error detallado al procesar mensaje: {error_detail}")
            return {
                "exitoso": False,
                "error": f"Error al procesar mensaje: {str(e)}"
            }

    def obtener_historial(self) -> List[Dict[str, Any]]:
        """Retorna el historial de conversaciones"""
        return self.historial_conversacion

    def limpiar_historial(self):
        """Limpia el historial de conversaciones y sesiones"""
        self.historial_conversacion = []
        self.agente_activo = None
        # Limpiar las sesiones para reiniciar las conversaciones
        self.sessions = {}
        print("🧹 Historial y sesiones limpiados")

    def obtener_agente_activo(self) -> Optional[Dict[str, Any]]:
        """
        Retorna información sobre el agente actualmente activo

        Returns:
            Diccionario con info del agente o None si no hay agente activo
        """
        if not self.agente_activo:
            return None

        if self.agente_activo not in self.agentes:
            return None

        agente_info = self.agentes[self.agente_activo]
        return {
            "id": self.agente_activo,
            "nombre": agente_info["nombre"],
            "descripcion": agente_info["descripcion"],
            "color": agente_info["color"],
            "emoji": agente_info.get("emoji", "🤖")
        }


# Crear instancia global del orquestador (singleton)
_orchestrator = None

def get_orchestrator() -> AgentOrchestrator:
    """
    Retorna la instancia singleton del orquestador

    Returns:
        Instancia del AgentOrchestrator
    """
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AgentOrchestrator()
    return _orchestrator
