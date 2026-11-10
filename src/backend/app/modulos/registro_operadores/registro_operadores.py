"""Composición del Módulo I — Registro Provincial de Operadores.

Clase que inyecta las dependencias (DAO, servicios) y registra el
router en la aplicación FastAPI.
"""

from __future__ import annotations

from fastapi import FastAPI

from core.contracts import PersonaDAO as PersonaDAOProtocol
from core.persona.dao import PersonaDAO
from core.persona.servicio import PersonaService
from core.storage.insforge import InsforgeStorage
from modulos.registro_operadores.adjunto_dao import AdjuntoOperadorDAO
from modulos.registro_operadores.controlador import crear_router
from modulos.registro_operadores.dao import ROCCAOperadorDAO
from modulos.registro_operadores.servicio import ROCCAOperadorService


class RegistroOperadoresModulo:
    """Módulo I — Registro Provincial de Operadores.

    Responsabilidad única: componer el módulo (DAO + servicio + router)
    y registrar sus endpoints en la aplicación.
    """

    def __init__(
        self,
        db_dao,
        persona_dao: PersonaDAOProtocol | None = None,
        persona_service: PersonaService | None = None,
        adjunto_dao: AdjuntoOperadorDAO | None = None,
        storage: InsforgeStorage | None = None,
    ) -> None:
        self._db_dao = db_dao
        self._persona_dao = persona_dao or PersonaDAO(db_dao.obtener_sesion)
        self._persona_service = persona_service or PersonaService(self._persona_dao)
        self._dao = ROCCAOperadorDAO(db_dao.obtener_sesion)
        self._adjunto_dao = adjunto_dao or AdjuntoOperadorDAO(db_dao.obtener_sesion)
        self._servicio = ROCCAOperadorService(
            self._dao,
            persona_service=self._persona_service,
            adjunto_dao=self._adjunto_dao,
            storage=storage,
        )

    def registrar(self, app: FastAPI) -> None:
        """Registra el router del módulo en la aplicación."""
        router = crear_router(self._servicio)
        app.include_router(router)
