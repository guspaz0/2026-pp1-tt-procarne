"""Módulo de la mercadería (catálogo de códigos AFIP)."""

from .entidad import Mercaderia, MercaderiaConHueso, MercaderiaSinHueso, MercaderiaPorcina
from .dao import Mercaderia as MercaderiaORM, MercaderiaDAO
from .schema import MercaderiaIn, MercaderiaOut
from .servicio import MercaderiaError, MercaderiaService

__all__ = [
    "Mercaderia",
    "MercaderiaConHueso",
    "MercaderiaSinHueso",
    "MercaderiaPorcina",
    "MercaderiaORM",
    "MercaderiaDAO",
    "MercaderiaIn",
    "MercaderiaOut",
    "MercaderiaService",
    "MercaderiaError",
]
