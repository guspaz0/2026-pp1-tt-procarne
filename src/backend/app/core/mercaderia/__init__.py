"""Submódulo de la mercadería (catálogo genérico de productos)."""

from .dao import Mercaderia as MercaderiaORM
from .dao import MercaderiaDAO
from .entidad import Mercaderia
from .schema import MercaderiaIn, MercaderiaOut
from .servicio import MercaderiaError, MercaderiaService

__all__ = [
    "Mercaderia",
    "MercaderiaORM",
    "MercaderiaDAO",
    "MercaderiaIn",
    "MercaderiaOut",
    "MercaderiaService",
    "MercaderiaError",
]
