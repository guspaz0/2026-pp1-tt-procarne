"""Módulo II — Trazabilidad Comercial (ROCCA).

Encapsula la inyección de dependencias del módulo: crea el DAO,
el servicio y el controlador (router).

Uso::

    from modulos.trazabilidad_comercial.trazabilidad_comercial import TrazabilidadComercialModulo

    modulo = TrazabilidadComercialModulo(db_dao)
    modulo.registrar(app)
"""

from __future__ import annotations

from fastapi import FastAPI

from configs.dao import DatabaseDAO

from .controlador import crear_router
from .dao import RegistroTrazabilidadDAO
from .servicio import TrazabilidadComercialService


class TrazabilidadComercialModulo:
    """Módulo II: Trazabilidad Comercial.

    Encapsula:
    - El DAO del registro de trazabilidad
    - El servicio de negocio
    - El controlador (router)

    Args:
        db_dao: DAO de base de datos (SQLite o PostgreSQL).
    """

    def __init__(self, db_dao: DatabaseDAO) -> None:
        self.trazabilidad_dao = RegistroTrazabilidadDAO(db_dao.obtener_sesion)
        self.trazabilidad_service = TrazabilidadComercialService(self.trazabilidad_dao)
        self.router = crear_router(trazabilidad_service=self.trazabilidad_service)

    def registrar(self, app: FastAPI) -> None:
        """Registra el router del módulo en la aplicación.

        Args:
            app: Instancia de :class:`FastAPI`.
        """
        app.include_router(self.router)
