"""Submódulo de la mercadería (catálogo genérico de productos)."""

from .entidad import Mercaderia
from .dao import Mercaderia as MercaderiaORM, MercaderiaDAO
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
