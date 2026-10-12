"""Módulo III — Fiscalización (ROCCA).

Encapsula la inyección de dependencias del módulo: crea el DAO,
el servicio y el controlador (router).

Uso::

    from modulos.fiscalizacion.fiscalizacion import FiscalizacionModulo

    modulo = FiscalizacionModulo(db_dao)
    modulo.registrar(app)
"""

from __future__ import annotations

from fastapi import FastAPI

from configs.dao import DatabaseDAO

from .controlador import crear_router
from .dao import FiscalizacionDAO
from .servicio import FiscalizacionService


class FiscalizacionModulo:
    """Módulo III: Fiscalización.

    Encapsula:
    - El DAO de fiscalización (inspecciones, actas, decomisos,
      infracciones, sanciones, reincidencias)
    - El servicio de negocio
    - El controlador (router)

    Args:
        db_dao: DAO de base de datos (SQLite o PostgreSQL).
    """

    def __init__(self, db_dao: DatabaseDAO) -> None:
        self.fiscalizacion_dao = FiscalizacionDAO(db_dao.obtener_sesion)
        self.fiscalizacion_service = FiscalizacionService(self.fiscalizacion_dao)
        self.router = crear_router(fiscalizacion_service=self.fiscalizacion_service)

    def registrar(self, app: FastAPI) -> None:
        """Registra el router del módulo en la aplicación.

        Args:
            app: Instancia de :class:`FastAPI`.
        """
        app.include_router(self.router)
