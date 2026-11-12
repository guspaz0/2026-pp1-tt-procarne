"""Controlador (router API) raíz del Módulo I — Registro Provincial de Operadores.

Compone los routers por entidad DAO. Cada router hijo recibe el prefijo
``/api/registro-operadores`` para que las rutas queden en el mismo espacio
que antes (``/api/registro-operadores/{operador_id}/...``).

- :mod:`...operador.controlador` — CRUD + ciclo de vida del operador.
- :mod:`...actividad_economica.controlador` — catálogo de actividades (solo DAO).
- :mod:`...certificado.controlador` — certificados F102 + PDF.
- :mod:`...requisito_inscripcion.controlador` — requisitos + catálogo.
- :mod:`...adjunto_operador.controlador` — adjuntos (documentos) de operador.
"""

from __future__ import annotations

from fastapi import APIRouter

from modulos.registro_operadores.adjunto_operador.controlador import (
    crear_router as crear_router_adjuntos,
)
from modulos.registro_operadores.actividad_economica.controlador import (
    crear_router as crear_router_catalogo_actividades,
)
from modulos.registro_operadores.certificado.controlador import (
    crear_router as crear_router_certificados,
)
from modulos.registro_operadores.operador.controlador import (
    crear_router as crear_router_operadores,
)
from modulos.registro_operadores.requisito_inscripcion.controlador import (
    crear_router as crear_router_requisitos,
)

PREFIX = "/api/registro-operadores"


def crear_router(
    operador_service,
    catalogo_actividades_dao,
    certificado_service,
    requisito_service,
    adjunto_service,
) -> APIRouter:
    """Crea el router API del módulo de registro de operadores.

    Recibe las dependencias ya compuestas por
    :class:`modulos.registro_operadores.registro_operadores.RegistroOperadoresModulo`.
    """
    router = APIRouter()

    router.include_router(
        crear_router_catalogo_actividades(catalogo_actividades_dao, prefix=PREFIX)
    )
    router.include_router(
        crear_router_operadores(operador_service, prefix=PREFIX)
    )
    router.include_router(
        crear_router_certificados(
            certificado_service,
            operador_service=operador_service,
            prefix=PREFIX,
        )
    )
    router.include_router(
        crear_router_requisitos(requisito_service, prefix=PREFIX)
    )
    router.include_router(
        crear_router_adjuntos(adjunto_service, prefix=PREFIX)
    )

    return router
