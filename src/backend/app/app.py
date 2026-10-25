"""Punto de entrada de la aplicación ROCCA.

Clase :class:`RoccaApp` que encapsula la creación de la instancia de
:class:`FastAPI` y la inyección de los módulos.

Uso::

    from app.app import crear_app
    app = crear_app()
"""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from configs.dao import DATABASE_URL, crear_dao
from core.mercaderia.dao import MercaderiaDAO
from core.mercaderia.servicio import MercaderiaService
from modulos.registro_operadores.registro_operadores import RegistroOperadoresModulo
from modulos.remitos_carnicos.remitos_carnicos import RemitosCarnicosModulo
from modulos.trazabilidad_comercial.trazabilidad_comercial import TrazabilidadComercialModulo
from modulos.fiscalizacion.fiscalizacion import FiscalizacionModulo


class RoccaApp:
    """Aplicación ROCCA.

    Encapsula:
    - La instancia de :class:`FastAPI`
    - El DAO de base de datos (SQLite o PostgreSQL)
    - Los módulos de negocio (remitos_carnicos)
    - El health check y el frontend estático
    """

    def __init__(self, database_url: str | None = None) -> None:
        # 1. Instancia de FastAPI
        self.app = FastAPI(title="ROCCA", version="0.1.0")

        # 1b. CORS (el frontend vive en Netlify, la API en Render)
        allowed_origins = [
            o.strip()
            for o in os.environ.get(
                "ROCCA_CORS_ORIGINS",
                "http://localhost:5173",
            ).split(",")
            if o.strip()
        ]
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=allowed_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # 2. DAO de base de datos (SQLite o PostgreSQL según la URL)
        url = database_url or DATABASE_URL
        self.db_dao = crear_dao(url)
        self.db_dao.crear_tablas()

        # 3. Módulos de negocio (cada uno inyecta sus propias dependencias)
        self.registro_operadores = RegistroOperadoresModulo(self.db_dao)
        self.registro_operadores.registrar(self.app)

        # El catálogo genérico de mercaderías se compone aquí (orquestador):
        # el módulo de remitos depende solo de sus contratos (tipos).
        self.mercaderia_dao = MercaderiaDAO(self.db_dao.obtener_sesion)
        self.mercaderia_service = MercaderiaService(self.mercaderia_dao)

        self.remitos_carnicos = RemitosCarnicosModulo(
            self.db_dao,
            mercaderia_dao=self.mercaderia_dao,
            mercaderia_service=self.mercaderia_service,
        )
        self.remitos_carnicos.registrar(self.app)

        self.trazabilidad_comercial = TrazabilidadComercialModulo(self.db_dao)
        self.trazabilidad_comercial.registrar(self.app)

        self.fiscalizacion = FiscalizacionModulo(self.db_dao)
        self.fiscalizacion.registrar(self.app)

        # 4. Health check
        self._registrar_health_check()

        # 5. Manejador global de errores
        self._registrar_error_handlers()

        # 6. Frontend estático (comentado: el frontend vive en Netlify)
        # self._registrar_frontend()

    # ------------------------------------------------------------------
    # Health check
    # ------------------------------------------------------------------

    def _registrar_health_check(self) -> None:
        """Registra el endpoint de health check."""

        @self.app.get("/api/health")
        def health() -> dict:
            return {"status": "ok"}

    # ------------------------------------------------------------------
    # Manejador global de errores
    # ------------------------------------------------------------------

    def _registrar_error_handlers(self) -> None:
        """Registra manejadores globales de errores para respuestas JSON
        consistentes en todo el API."""

        @self.app.exception_handler(FastAPIHTTPException)
        async def http_exception_handler(request: Request, exc: FastAPIHTTPException) -> JSONResponse:
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "detail": exc.detail,
                    "status_code": exc.status_code,
                },
            )

        @self.app.exception_handler(Exception)
        async def global_error_handler(request: Request, exc: Exception) -> JSONResponse:
            import logging
            logging.getLogger("rocca").exception("Error no manejado en %s %s", request.method, request.url.path)
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Error interno del servidor",
                    "status_code": 500,
                },
            )

    # ------------------------------------------------------------------
    # Frontend estático (desactivado: el frontend se sirve desde Netlify)
    # ------------------------------------------------------------------

    # def _registrar_frontend(self) -> None:
    #     """Registra el montaje del frontend estático y el SPA fallback.
    #
    #     Desactivado: el frontend se sirve desde Netlify, no desde el backend.
    #     """
    #     from fastapi.responses import FileResponse
    #     from fastapi.staticfiles import StaticFiles
    #
    #     default_static = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
    #     static_dir = Path(os.environ.get("ROCCA_STATIC_DIR", default_static))
    #
    #     if static_dir.exists():
    #         self.app.mount("/static", StaticFiles(directory=static_dir / "static"), name="static")
    #
    #     @self.app.get("/{path:path}")
    #     def frontend_fallback(path: str) -> FileResponse:
    #         """SPA fallback: toda ruta no-API y no-estática sirve index.html."""
    #         return FileResponse(static_dir / "index.html")

    # ------------------------------------------------------------------
    # Ciclo de vida
    # ------------------------------------------------------------------

    def cerrar(self) -> None:
        """Cierra el DAO de base de datos y libera recursos."""
        self.db_dao.cerrar()


def crear_app(database_url: str | None = None) -> FastAPI:
    """Fábrica: crea una nueva instancia de la aplicación.

    Args:
        database_url: URL de la base de datos (opcional; por defecto usa
            la variable de entorno ``ROCCA_DATABASE_URL``).

    Returns:
        Instancia de :class:`FastAPI` con todos los módulos inyectados.
    """
    return RoccaApp(database_url=database_url).app
