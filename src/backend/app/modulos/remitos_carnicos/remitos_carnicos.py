"""Módulo de Remitos Electrónicos Cárnicos.

Encapsula la inyección de dependencias del módulo: crea los DAOs,
servicios y el controlador (router).

Uso::

    from modulos.remitos_carnicos.remitos_carnicos import RemitosCarnicosModulo

    modulo = RemitosCarnicosModulo(db_dao)
    app.include_router(modulo.router)
"""

from __future__ import annotations

from fastapi import FastAPI

from configs.dao import DatabaseDAO
from modulos.genericos.mercaderia.dao import MercaderiaDAO
from modulos.genericos.mercaderia.servicio import MercaderiaService
from .operador.dao import OperadorDAO
from .operador.servicio import OperadorService
from .remito.dao import RemitoCarnicoDAO
from .remito.servicio import RemitoCarnicoService
from .controlador import crear_router


class RemitosCarnicosModulo:
    """Módulo de Remitos Electrónicos Cárnicos.

    Encapsula:
    - Los DAOs por entidad (operador, mercadería, remito)
    - Los servicios de negocio
    - El controlador (router)

    Args:
        db_dao: DAO de base de datos (SQLite o PostgreSQL).
    """

    def __init__(self, db_dao: DatabaseDAO) -> None:
        # DAOs por entidad
        self.operador_dao = OperadorDAO(db_dao.obtener_sesion)
        self.mercaderia_dao = MercaderiaDAO(db_dao.obtener_sesion)
        self.remito_dao = RemitoCarnicoDAO(db_dao.obtener_sesion)

        # Servicios de negocio
        self.operador_service = OperadorService(self.operador_dao)
        self.mercaderia_service = MercaderiaService(self.mercaderia_dao)
        self.remito_service = RemitoCarnicoService(
            remito_dao=self.remito_dao,
            operador_dao=self.operador_dao,
            mercaderia_dao=self.mercaderia_dao,
        )

        # Controlador (router del módulo)
        self.router = crear_router(
            operador_service=self.operador_service,
            mercaderia_service=self.mercaderia_service,
            remito_service=self.remito_service,
        )

    def registrar(self, app: FastAPI) -> None:
        """Registra el router del módulo en la aplicación.

        Args:
            app: Instancia de :class:`FastAPI`.
        """
        app.include_router(self.router)
