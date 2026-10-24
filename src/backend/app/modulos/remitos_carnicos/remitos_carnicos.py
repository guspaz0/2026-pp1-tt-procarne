"""Módulo de Remitos Electrónicos Cárnicos.

Encapsula la inyección de dependencias del módulo: crea los DAOs,
servicios y el controlador (router).

El módulo **no** importa los DAOs/servicios concretos del catálogo
genérico de mercaderías: recibe sus contratos por inyección
(:class:`MercaderiaDAOProtocol` y :class:`MercaderiaServiceProtocol`),
de modo que la composición con el módulo genérico la resuelve el
orquestador de la aplicación.

Uso::

    from modulos.remitos_carnicos.remitos_carnicos import RemitosCarnicosModulo

    modulo = RemitosCarnicosModulo(db_dao, mercaderia_dao, mercaderia_service)
    app.include_router(modulo.router)
"""

from __future__ import annotations

from typing import Optional

from fastapi import FastAPI

from core import DatabaseDAO

from .operador.dao import OperadorDAO
from .operador.servicio import OperadorService
from .remito.dao import RemitoCarnicoDAO
from .remito.servicio import MercaderiaDAOProtocol, RemitoCarnicoService
from .controlador import MercaderiaServiceProtocol, crear_router


class RemitosCarnicosModulo:
    """Módulo de Remitos Electrónicos Cárnicos.

    Encapsula:
    - Los DAOs por entidad (operador, remito)
    - Los servicios de negocio
    - El controlador (router)

    Args:
        db_dao: DAO de base de datos (SQLite o PostgreSQL).
        mercaderia_dao: Contrato de consulta de mercaderías (catálogo
            genérico). Se inyecta desde el orquestador de la aplicación.
        mercaderia_service: Contrato del servicio de mercaderías.
    """

    def __init__(
        self,
        db_dao: DatabaseDAO,
        mercaderia_dao: Optional[MercaderiaDAOProtocol] = None,
        mercaderia_service: Optional[MercaderiaServiceProtocol] = None,
    ) -> None:
        # DAOs por entidad
        self.operador_dao = OperadorDAO(db_dao.obtener_sesion)
        self.remito_dao = RemitoCarnicoDAO(db_dao.obtener_sesion)
        self.mercaderia_dao = mercaderia_dao

        # Servicios de negocio
        self.operador_service = OperadorService(self.operador_dao)
        self.mercaderia_service = mercaderia_service
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
