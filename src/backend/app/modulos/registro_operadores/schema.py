"""Shim de compatibilidad — DTOs (schemas Pydantic) del módulo I.

Cada entidad ahora tiene su propio ``dto.py`` en su carpeta. Este archivo
solo re-exports los nombres para no romper importaciones existentes
(tests y otros módulos).
"""

from modulos.registro_operadores.adjunto_operador.dto import AdjuntoOperadorOut
from modulos.registro_operadores.actividad_economica.dto import (
    ActividadEconomicaOut,
    GrupoActividadOut,
    SubgrupoActividadOut,
)
from modulos.registro_operadores.certificado.dto import (
    CertificadoIn,
    CertificadoOut,
    CertificadoSuspenderIn,
)
from modulos.registro_operadores.operador.dto import OperadorIn, OperadorOut
from modulos.registro_operadores.requisito_inscripcion.dto import (
    RequisitoInscripcionIn,
    RequisitoInscripcionOut,
)

__all__ = [
    "ActividadEconomicaOut",
    "AdjuntoOperadorOut",
    "CertificadoIn",
    "CertificadoOut",
    "CertificadoSuspenderIn",
    "GrupoActividadOut",
    "RequisitoInscripcionIn",
    "RequisitoInscripcionOut",
    "OperadorIn",
    "OperadorOut",
    "SubgrupoActividadOut",
]
