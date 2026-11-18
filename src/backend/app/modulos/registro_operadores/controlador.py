"""Controlador (router API) raíz del Módulo I — Registro Provincial de Operadores.

Compone los routers por entidad DAO. Cada router hijo recibe el prefijo
``/api/registro-operadores`` para que las rutas queden en el mismo espacio
que antes (``/api/registro-operadores/{operador_id}/...``).

- :mod:`...operador.controlador` — CRUD + ciclo de vida del operador.
- :mod:`...actividad_economica.controlador` — catálogo de actividades (solo DAO).
- :mod:`...certificado.controlador` — certificados F102 + PDF.
"""

from __future__ import annotations

from fastapi import APIRouter

from modulos.registro_operadores.actividad_economica.controlador import (
    crear_router as crear_router_catalogo_actividades,
)
from modulos.registro_operadores.certificado.controlador import (
    crear_router as crear_router_certificados,
)
from modulos.registro_operadores.categoria.controlador import (
    crear_router as crear_router_categorias,
)
from modulos.registro_operadores.operador.controlador import (
    crear_router as crear_router_operadores,
)

PREFIX = "/api/registro-operadores"


def crear_router(
    operador_service,
    catalogo_actividades_dao,
    certificado_service,
    categoria_service=None,
) -> APIRouter:
    """Crea el router API del módulo de registro de operadores."""
    router = APIRouter()

    # Las categorías se registran PRIMERO: su ruta ``/categorias`` debe
    # resolverse antes que ``/{operador_id}`` del router de operadores.
    if categoria_service is not None:
        router.include_router(
            crear_router_categorias(categoria_service, prefix=PREFIX)
        )
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

    return router
