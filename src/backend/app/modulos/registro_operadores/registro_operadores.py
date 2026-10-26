"""Composición del Módulo I — Registro Provincial de Operadores.

Clase que inyecta las dependencias (DAO, servicios) y registra el
router en la aplicación FastAPI.
"""

from __future__ import annotations

from fastapi import FastAPI

from core.contracts import PersonaDAO as PersonaDAOProtocol
from core.persona.servicio import PersonaService
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
    ) -> None:
        self._db_dao = db_dao
        self._persona_dao = persona_dao
        self._persona_service = persona_service
        self._dao = ROCCAOperadorDAO(db_dao.obtener_sesion)
        self._servicio = ROCCAOperadorService(self._dao)

    def registrar(self, app: FastAPI) -> None:
        """Registra el router del módulo en la aplicación."""
        router = crear_router(self._servicio)
        app.include_router(router)
