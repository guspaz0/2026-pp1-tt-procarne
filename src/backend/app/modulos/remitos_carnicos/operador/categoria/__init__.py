"""Submódulo de categorías del operador (RFOCB).

Contiene:
- :class:`Actividad` — actividad ganadera (Bovino/Bubalino, Porcino, ...)
- :class:`CategoriaAfip` — catálogo de categorías por actividad
- :class:`CategoriaOperador` — inscripción de un operador en una categoría
"""

from .actividad import Actividad, ActividadDAO
from .categoria_afip import CategoriaAfip, CategoriaAfipDAO
from .operador_categoria import CategoriaOperador, CategoriaOperadorDAO

__all__ = [
    "Actividad",
    "ActividadDAO",
    "CategoriaAfip",
    "CategoriaAfipDAO",
    "CategoriaOperador",
    "CategoriaOperadorDAO",
]
