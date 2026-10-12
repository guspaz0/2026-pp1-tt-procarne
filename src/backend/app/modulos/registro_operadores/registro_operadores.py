"""Módulo I — Registro Provincial de Operadores (ROCCA).

Encapsula la inyección de dependencias del módulo: crea el DAO,
el servicio y el controlador (router).

Uso::

    from modulos.registro_operadores.registro_operadores import RegistroOperadoresModulo

    modulo = RegistroOperadoresModulo(db_dao)
    modulo.registrar(app)
"""

from __future__ import annotations

from fastapi import FastAPI

from configs.dao import DatabaseDAO

from .controlador import crear_router
from .dao import ROCCAOperadorDAO
from .servicio import ROCCAOperadorService


class RegistroOperadoresModulo:
    """Módulo I: Registro Provincial de Operadores.

    Encapsula:
    - El DAO del operador (con sus habilitaciones, inscripciones y
      domicilios operativos)
    - El servicio de negocio
    - El controlador (router)

    Args:
        db_dao: DAO de base de datos (SQLite o PostgreSQL).
    """

    def __init__(self, db_dao: DatabaseDAO) -> None:
        self.operador_dao = ROCCAOperadorDAO(db_dao.obtener_sesion)
        self.operador_service = ROCCAOperadorService(self.operador_dao)
        self.router = crear_router(operador_service=self.operador_service)

    def registrar(self, app: FastAPI) -> None:
        """Registra el router del módulo en la aplicación.

        Args:
            app: Instancia de :class:`FastAPI`.
        """
        app.include_router(self.router)
