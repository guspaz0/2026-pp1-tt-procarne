"""Enumeraciones compartidas por todos los módulos de ROCCA."""

from __future__ import annotations

from enum import Enum


class TipoPersona(str, Enum):
    """Tipo de persona en el registro."""

    FISICA = "FISICA"
    JURIDICA = "JURIDICA"
