"""Enumeraciones del módulo genérico."""

from __future__ import annotations

from enum import Enum


class TipoPersona(str, Enum):
    """Tipo de persona del registro.

    - PF: Persona Física
    - PJ: Persona Jurídica
    """

    PF = "PF"
    PJ = "PJ"
