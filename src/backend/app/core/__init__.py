"""Núcleo de dominio compartido por todos los módulos de ROCCA.

Contiene:
- :mod:`base` — clase base abstracta para entidades.
- :mod:`contracts` — protocolos (interfaces) para inyección de
  dependencias entre módulos.
- :mod:`enums` — enumeraciones compartidas (tipo de persona).
- :mod:`persona` — submódulo de la persona (física o jurídica).
- :mod:`mercaderia` — submódulo de la mercadería (catálogo genérico).
"""

from .base import Entidad
from .contracts import DatabaseDAO as DatabaseDAOProtocol
from .contracts import PersonaDAO as PersonaDAOProtocol
from .contracts import PersonaRef
from .enums import TipoPersona
# ``mercaderias_genericas`` aún no está implementado (Módulo II/III). Se
# descomenta al reactivar el módulo; mientras tanto NO se importa el ORM para
# que Alembic no detecte la tabla como "a agregar".
# from .mercaderia import (
#     Mercaderia,
#     Mercaderia as MercaderiaORM,
#     MercaderiaDAO,
#     MercaderiaError,
#     MercaderiaIn,
#     MercaderiaOut,
#     MercaderiaService,
# )
from .persona import (
    Persona,
    Persona as PersonaORM,
    PersonaDAO,
    PersonaError,
    PersonaFisica,
    PersonaIn,
    PersonaJuridica,
    PersonaOut,
    PersonaService,
)

__all__ = [
    "Entidad",
    "TipoPersona",
    "Persona",
    "PersonaFisica",
    "PersonaJuridica",
    "PersonaORM",
    "PersonaDAO",
    "PersonaIn",
    "PersonaOut",
    "PersonaService",
    "PersonaError",
    "DatabaseDAOProtocol",
    "PersonaDAOProtocol",
    "PersonaRef",
]
