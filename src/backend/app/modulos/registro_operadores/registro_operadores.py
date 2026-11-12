"""Composición del Módulo I — Registro Provincial de Operadores.

Clase que inyecta las dependencias (DAOs por entidad, servicios, storage)
y registra el router compuesto en la aplicación FastAPI.
"""

from __future__ import annotations

from fastapi import FastAPI

from core.contracts import PersonaDAO as PersonaDAOProtocol
from core.persona.dao import PersonaDAO
from core.persona.servicio import PersonaService
from core.storage.insforge import InsforgeStorage
from modulos.registro_operadores.asociaciones import (  # noqa: F401  (registrar modelos N:M)
    CertificadoActividad,
    OperadorActividad,
)
from modulos.registro_operadores.adjunto_operador.dao import AdjuntoOperadorDAO
from modulos.registro_operadores.adjunto_operador.servicio import AdjuntoOperadorService
from modulos.registro_operadores.actividad_economica.dao import CatalogoActividadesDAO
from modulos.registro_operadores.certificado.dao import CertificadoDAO
from modulos.registro_operadores.certificado.servicio import CertificadoService
from modulos.registro_operadores.controlador import crear_router
from modulos.registro_operadores.operador.dao import OperadorDAO
from modulos.registro_operadores.operador.servicio import OperadorService
from modulos.registro_operadores.requisito_inscripcion.dao import RequisitoInscripcionDAO
from modulos.registro_operadores.requisito_inscripcion.servicio import (
    RequisitoInscripcionService,
)


class RegistroOperadoresModulo:
    """Módulo I — Registro Provincial de Operadores.

    Responsabilidad única: componer el módulo (DAOs por entidad + servicios
    + router) y registrar sus endpoints en la aplicación.
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

        # DAOs por entidad
        self._operador_dao = OperadorDAO(db_dao.obtener_sesion)
        self._catalogo_dao = CatalogoActividadesDAO(db_dao.obtener_sesion)
        self._certificado_dao = CertificadoDAO(db_dao.obtener_sesion)
        self._requisito_dao = RequisitoInscripcionDAO(db_dao.obtener_sesion)
        self._adjunto_dao = adjunto_dao or AdjuntoOperadorDAO(db_dao.obtener_sesion)

        # Servicios por entidad
        self._certificado_service = CertificadoService(self._certificado_dao)
        self._requisito_service = RequisitoInscripcionService(self._requisito_dao)
        self._adjunto_service = AdjuntoOperadorService(
            self._adjunto_dao,
            storage=storage,
            operador_dao=self._operador_dao,
            requisito_service=self._requisito_service,
        )
        self._operador_service = OperadorService(
            self._operador_dao,
            persona_service=self._persona_service,
            requisito_service=self._requisito_service,
            certificado_service=self._certificado_service,
            catalogo_actividades_dao=self._catalogo_dao,
        )

    def registrar(self, app: FastAPI) -> None:
        """Registra el router del módulo en la aplicación."""
        router = crear_router(
            operador_service=self._operador_service,
            catalogo_actividades_dao=self._catalogo_dao,
            certificado_service=self._certificado_service,
            requisito_service=self._requisito_service,
            adjunto_service=self._adjunto_service,
        )
        app.include_router(router)
