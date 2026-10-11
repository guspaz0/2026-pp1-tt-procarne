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

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from configs.dao import DATABASE_URL, crear_dao
from modulos.remitos_carnicos.remitos_carnicos import RemitosCarnicosModulo


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

        # 2. DAO de base de datos (SQLite o PostgreSQL según la URL)
        url = database_url or DATABASE_URL
        self.db_dao = crear_dao(url)
        self.db_dao.crear_tablas()

        # 3. Módulos de negocio (cada uno inyecta sus propias dependencias)
        self.remitos_carnicos = RemitosCarnicosModulo(self.db_dao)
        self.remitos_carnicos.registrar(self.app)

        # 4. Health check
        self._registrar_health_check()

        # 5. Frontend estático
        self._registrar_frontend()

    # ------------------------------------------------------------------
    # Health check
    # ------------------------------------------------------------------

    def _registrar_health_check(self) -> None:
        """Registra el endpoint de health check."""

        @self.app.get("/api/health")
        def health() -> dict:
            return {"status": "ok"}

    # ------------------------------------------------------------------
    # Frontend estático
    # ------------------------------------------------------------------

    def _registrar_frontend(self) -> None:
        """Registra el montaje del frontend estático y el SPA fallback."""
        default_static = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
        static_dir = Path(os.environ.get("ROCCA_STATIC_DIR", default_static))

        if static_dir.exists():
            self.app.mount("/static", StaticFiles(directory=static_dir / "static"), name="static")

        @self.app.get("/{path:path}")
        def frontend_fallback(path: str) -> FileResponse:
            """SPA fallback: toda ruta no-API y no-estática sirve index.html."""
            return FileResponse(static_dir / "index.html")

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
