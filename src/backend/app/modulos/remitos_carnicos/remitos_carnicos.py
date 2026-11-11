"""Composición del módulo de Remitos Electrónicos Cárnicos.

Clase que inyecta las dependencias (DAOs, servicios) y registra el
router en la aplicación FastAPI.
"""

from __future__ import annotations

from fastapi import FastAPI

from core.contracts import MercaderiaDAO as MercaderiaDAOProtocol
from core.contracts import PersonaDAO as PersonaDAOProtocol
from core.mercaderia.servicio import MercaderiaService
from core.persona.servicio import PersonaService
from modulos.remitos_carnicos.controlador import crear_router
from modulos.remitos_carnicos.operador.dao import RemitoOperadorDAO
from modulos.remitos_carnicos.operador.servicio import RemitoOperadorService
from modulos.remitos_carnicos.remito.dao import RemitoCarnicoDAO
from modulos.remitos_carnicos.remito.servicio import RemitoCarnicoService


class RemitosCarnicosModulo:
    """Módulo de Remitos Electrónicos Cárnicos.

    Responsabilidad única: componer el módulo (DAOs + servicios + router)
    y registrar sus endpoints en la aplicación.
    """

    def __init__(
        self,
        db_dao,
        persona_dao: PersonaDAOProtocol | None = None,
        persona_service: PersonaService | None = None,
        mercaderia_dao: MercaderiaDAOProtocol | None = None,
        mercaderia_service: MercaderiaService | None = None,
    ) -> None:
        self._db_dao = db_dao
        self._persona_dao = persona_dao
        self._persona_service = persona_service
        self._mercaderia_dao = mercaderia_dao
        self._mercaderia_service = mercaderia_service

        # DAOs del módulo
        self._operador_dao = RemitoOperadorDAO(db_dao.obtener_sesion)
        self._remito_dao = RemitoCarnicoDAO(db_dao.obtener_sesion)

        # Servicios del módulo
        self._operador_service = RemitoOperadorService(self._operador_dao)
        self._remito_service = RemitoCarnicoService(
            self._remito_dao,
            self._operador_dao,
            self._mercaderia_dao,
        )

    def registrar(self, app: FastAPI) -> None:
        """Registra el router del módulo en la aplicación."""
        router = crear_router(self._remito_service)
        app.include_router(router)
