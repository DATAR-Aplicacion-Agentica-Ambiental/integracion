import warnings

# Suprimir warnings de serialización de Pydantic relacionados con Google ADK
# Estos warnings son conocidos y no afectan la funcionalidad.
# Ocurren cuando Pydantic intenta serializar objetos Message/Choices del SDK de Google ADK
warnings.filterwarnings(
    'ignore',
    category=UserWarning,
    message='.*Pydantic.*serializer.*',
    module='pydantic'
)
warnings.filterwarnings(
    'ignore',
    category=UserWarning,
    message='.*Expected.*fields.*but got.*',
    module='pydantic'
)
warnings.filterwarnings(
    'ignore',
    category=UserWarning,
    message='.*serialized value may not be as expected.*',
    module='pydantic'
)

from . import agent
from .agent import app
from .agents_registry import AGENTS_REGISTRY as AGENTS_METADATA

__all__ = ["app", "AGENTS_METADATA"]
