"""Composición de la aplicación ROCCA.

Crea la instancia de FastAPI, configura CORS y registra los routers
de todos los módulos.

Uso::

    from app.app import crear_app
    app = crear_app()
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from configs.dao import crear_dao
from core.mercaderia.dao import MercaderiaDAO
from core.mercaderia.servicio import MercaderiaService
from core.persona.dao import PersonaDAO
from core.persona.servicio import PersonaService
from modulos.fiscalizacion.fiscalizacion import FiscalizacionModulo
from modulos.registro_operadores.registro_operadores import RegistroOperadoresModulo
from modulos.remitos_carnicos.remitos_carnicos import RemitosCarnicosModulo
from modulos.trazabilidad_comercial.trazabilidad_comercial import (
    TrazabilidadComercialModulo,
)


class RoccaApp:
    """Aplicación FastAPI compuesta por todos los módulos de ROCCA.

    Responsabilidad única: orquestar la creación de la aplicación,
    configurar el middleware y registrar los routers de cada módulo.
    """

    def __init__(self) -> None:
        self.app = FastAPI(
            title="ROCCA — Registro de Operadores de la Cadena Cárnica",
            description=(
                "API de gestión de la cadena cárnica: registro de operadores, "
                "remitos electrónicos, trazabilidad comercial y fiscalización."
            ),
            version="1.0.0",
        )
        self._configurar_cors()

    def _configurar_cors(self) -> None:
        """Configura el middleware CORS (abierto para desarrollo)."""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def _montar_frontend(self) -> None:
        """Monta el build de React (dist) como archivos estáticos en la raíz.

        El directorio se genera con `pnpm build` en el frontend y se emite
        en app/static/. Se monta DESPUÉS de los routers /api/* para que
        las rutas de la API tengan prioridad.
        """
        static_dir = Path(__file__).resolve().parent / "static"
        if static_dir.is_dir():
            self.app.mount(
                "/",
                StaticFiles(directory=str(static_dir), html=True),
                name="frontend",
            )

    def registrar_modulos(self) -> None:
        """Registra los routers de todos los módulos en la aplicación."""
        # DAO compartido (inyección de dependencias)
        db_dao = crear_dao()
        db_dao.crear_tablas()  # Asegura que las tablas existan (desarrollo)

        # Endpoint de salud
        @self.app.get("/api/health")
        def health():
            return {"status": "ok"}

        # Catálogos genéricos compartidos (core)
        persona_dao = PersonaDAO(db_dao.obtener_sesion)
        persona_service = PersonaService(persona_dao)
        mercaderia_dao = MercaderiaDAO(db_dao.obtener_sesion)
        mercaderia_service = MercaderiaService(mercaderia_dao)

        # Módulo I — Registro Provincial de Operadores
        registro = RegistroOperadoresModulo(
            db_dao,
            persona_dao=persona_dao,
            persona_service=persona_service,
        )
        registro.registrar(self.app)

        # Módulo — Remitos Electrónicos Cárnicos
        remitos = RemitosCarnicosModulo(
            db_dao,
            persona_dao=persona_dao,
            persona_service=persona_service,
            mercaderia_dao=mercaderia_dao,
            mercaderia_service=mercaderia_service,
        )
        remitos.registrar(self.app)

        # Módulo II — Trazabilidad Comercial
        trazabilidad = TrazabilidadComercialModulo(db_dao)
        trazabilidad.registrar(self.app)

        # Módulo III — Fiscalización
        fiscalizacion = FiscalizacionModulo(db_dao)
        fiscalizacion.registrar(self.app)

    def crear(self) -> FastAPI:
        """Compone la aplicación completa y la devuelve lista para servir."""
        self.registrar_modulos()
        self._montar_frontend()
        return self.app


def crear_app() -> FastAPI:
    """Factory: crea la aplicación ROCCA con todos los módulos registrados."""
    return RoccaApp().crear()
