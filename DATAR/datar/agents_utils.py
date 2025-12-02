import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv


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
    """
    load_dotenv(override=False)


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
    base = api_base or OPENROUTER_API_BASE_DEFAULT

    if require_key and not key:
        raise ConfigError(
            f"No se encontró la variable de entorno {OPENROUTER_API_KEY_ENV}. "
            "Configura tu clave de OpenRouter en un archivo .env o en el entorno "
            "antes de iniciar los agentes DATAR."
        )

    return OpenRouterConfig(api_key=key, api_base=base)




