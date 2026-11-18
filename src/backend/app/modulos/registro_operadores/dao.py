"""Shim de compatibilidad — DAOs y modelos ORM del módulo I.

El código antiguo importaba todos los modelos y DAOs desde este módulo.
Ahora cada entidad vive en su propia carpeta (patrón DAO modular):

- :mod:`modulos.registro_operadores.operador`
- :mod:`modulos.registro_operadores.actividad_economica`
- :mod:`modulos.registro_operadores.certificado`

Este archivo solo re-exports los nombres para no romper importaciones
existentes (tests, módulo de remitos, alembic).
"""

from modulos.registro_operadores.actividad_economica.dao import (
    ActividadEconomica,
    CatalogoActividadesDAO,
    GrupoActividad,
    SubgrupoActividad,
)
from modulos.registro_operadores.certificado.dao import Certificado, CertificadoDAO
from modulos.registro_operadores.operador.dao import Operador, OperadorDAO

__all__ = [
    "ActividadEconomica",
    "CatalogoActividadesDAO",
    "Certificado",
    "CertificadoDAO",
    "GrupoActividad",
    "Operador",
    "OperadorDAO",
    "SubgrupoActividad",
]
