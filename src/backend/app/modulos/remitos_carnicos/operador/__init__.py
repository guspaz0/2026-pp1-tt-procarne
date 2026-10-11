"""Módulo del operador de la cadena cárnica."""

from .entidad import Operador, ParticipanteRemito, Titular, Depositario, Destinatario, Transportista
from .dao import Operador as OperadorORM, OperadorDAO
from .categoria import (
    Actividad,
    ActividadDAO,
    CategoriaAfip,
    CategoriaAfipDAO,
    CategoriaOperador,
    CategoriaOperadorDAO,
)
from .schema import OperadorIn, OperadorOut
from .servicio import OperadorError, OperadorService

__all__ = [
    "Operador",
    "ParticipanteRemito",
    "Titular",
    "Depositario",
    "Destinatario",
    "Transportista",
    "OperadorORM",
    "OperadorDAO",
    "Actividad",
    "ActividadDAO",
    "CategoriaAfip",
    "CategoriaAfipDAO",
    "CategoriaOperador",
    "CategoriaOperadorDAO",
    "OperadorIn",
    "OperadorOut",
    "OperadorService",
    "OperadorError",
]
