"""Shim de compatibilidad — DAO de adjuntos de operador.

El modelo y DAO ahora viven en
:mod:`modulos.registro_operadores.adjunto_operador.dao`.
"""

from modulos.registro_operadores.adjunto_operador.dao import (
    AdjuntoOperador,
    AdjuntoOperadorDAO,
)

__all__ = ["AdjuntoOperador", "AdjuntoOperadorDAO"]
