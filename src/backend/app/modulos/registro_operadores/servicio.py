"""Shim de compatibilidad — servicio del módulo I.

El servicio antiguo (``OperadorService`` monolítico) fue desarmado en
servicios por entidad. Este archivo mantiene:

- ``OperadorError`` — error de negocio compartido (vive en
  :mod:`modulos.registro_operadores.operador.servicio`).
- ``OperadorService`` — fachada delegadora para no romper importaciones
  antiguas (tests). Sus métodos delegan en los servicios por entidad.
- ``REQUISITOS_*`` — constantes del catálogo de requisitos (viven en
  :mod:`modulos.registro_operadores.requisito_inscripcion.servicio`).
"""

from __future__ import annotations

from modulos.registro_operadores.operador.servicio import (
    OperadorError,
    OperadorService as _OperadorService,
)
from modulos.registro_operadores.requisito_inscripcion.servicio import (
    REQUISITOS_ADJUNTO_PERSONA,
    REQUISITOS_ESPECIFICOS_POR_CATEGORIA,
    REQUISITOS_GENERALES,
)

__all__ = [
    "REQUISITOS_ADJUNTO_PERSONA",
    "REQUISITOS_ESPECIFICOS_POR_CATEGORIA",
    "REQUISITOS_GENERALES",
    "OperadorError",
    "OperadorService",
]


# Alias: la API pública del servicio antiguo es la del servicio de operador.
# Los casos de uso de las demás entidades tienen su propio servicio:
#   - HabilitacionService (habilitacion/servicio.py)
#   - InscripcionService (inscripcion/servicio.py)
#   - CertificadoService (certificado/servicio.py)
#   - DomicilioOperativoService (domicilio_operativo/servicio.py)
#   - RequisitoInscripcionService (requisito_inscripcion/servicio.py)
#   - AdjuntoOperadorService (adjunto_operador/servicio.py)
OperadorService = _OperadorService
