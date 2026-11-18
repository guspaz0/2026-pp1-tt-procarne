"""Shim de compatibilidad — servicio del módulo I.

El servicio antiguo (``OperadorService`` monolítico) fue desarmado en
servicios por entidad. Este archivo mantiene:

- ``OperadorError`` — error de negocio compartido (vive en
  :mod:`modulos.registro_operadores.operador.servicio`).
- ``OperadorService`` — fachada delegadora para no romper importaciones
  antiguas (tests).
"""

from __future__ import annotations

from modulos.registro_operadores.operador.servicio import (
    OperadorError,
    OperadorService as _OperadorService,
)

__all__ = [
    "OperadorError",
    "OperadorService",
]


# Alias: la API pública del servicio antiguo es la del servicio de operador.
OperadorService = _OperadorService
