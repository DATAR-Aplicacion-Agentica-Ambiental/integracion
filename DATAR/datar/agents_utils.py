import os
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Suprimir warnings de serialización de Pydantic relacionados con Google ADK
# Estos warnings son conocidos y no afectan la funcionalidad.
# Ocurren cuando Pydantic intenta serializar objetos Message/Choices del SDK de Google ADK
# que tienen estructuras ligeramente diferentes a las esperadas por Pydantic.
warnings.filterwarnings(
    'ignore',
    category=UserWarning,
    message='.*Pydantic.*serializer.*',
)
warnings.filterwarnings(
    'ignore',
    category=UserWarning,
    message='.*Expected.*fields.*but got.*',
)
warnings.filterwarnings(
    'ignore',
    category=UserWarning,
    message='.*serialized value may not be as expected.*',
)


OPENROUTER_API_KEY_ENV = "OPENROUTER_API_KEY"
OPENROUTER_API_BASE_DEFAULT = "https://openrouter.ai/api/v1"


@dataclass
class OpenRouterConfig:
    api_key: str
    api_base: str = OPENROUTER_API_BASE_DEFAULT


class ConfigError(RuntimeError):
    """Error de configuración de entorno para los agentes DATAR."""


def load_env_if_needed() -> None:
    """
    Carga variables de entorno desde un archivo .env si existe.

    Esta función es segura de llamar múltiples veces; load_dotenv
    solo complementa lo que ya está en el entorno sin sobrescribir
    valores existentes por defecto.
    
    Siempre busca el archivo .env en la raíz del proyecto DATAR
    (donde está el directorio 'datar').
    """
    # Busca el .env en la raíz del proyecto DATAR
    # Navega desde datar/agents_utils.py hacia arriba hasta encontrar DATAR/
    current_file = Path(__file__).resolve()
    datar_root = current_file.parent.parent  # Sube de datar/agents_utils.py a DATAR/
    env_file = datar_root / ".env"
    
    if env_file.exists():
        load_dotenv(dotenv_path=env_file, override=False)
    else:
        # Si no existe, intenta también en el directorio padre (por si DATAR está dentro de otro proyecto)
        parent_env = datar_root.parent / ".env"
        if parent_env.exists():
            load_dotenv(dotenv_path=parent_env, override=False)


def get_openrouter_config(
    *,
    require_key: bool = True,
    api_base: Optional[str] = None,
) -> OpenRouterConfig:
    """
    Obtiene y valida la configuración necesaria para usar OpenRouter.

    - Intenta cargar variables desde .env si está disponible.
    - Verifica que exista la API key requerida.

    Args:
        require_key: Si es True, lanza un ConfigError si falta la API key.
        api_base: Permite sobreescribir la URL base; si no se da, usa el valor por defecto.

    Returns:
        OpenRouterConfig con api_key y api_base válidos.

    Raises:
        ConfigError: Si require_key es True y la API key no está definida.
    """
    load_env_if_needed()

    key = os.getenv(OPENROUTER_API_KEY_ENV) or ""
    # Eliminar espacios en blanco al inicio y final
    key = key.strip()
    base = api_base or OPENROUTER_API_BASE_DEFAULT

    if require_key:
        # Determinar dónde se buscó el .env para el mensaje de error
        current_file = Path(__file__).resolve()
        datar_root = current_file.parent.parent
        env_file = datar_root / ".env"
        
        if not key:
            error_msg = (
                f"No se encontró la variable de entorno {OPENROUTER_API_KEY_ENV}. "
                f"Configura tu clave de OpenRouter en un archivo .env en: {env_file} "
                "o en el entorno antes de iniciar los agentes DATAR."
            )
            raise ConfigError(error_msg)

    return OpenRouterConfig(api_key=key, api_base=base)




