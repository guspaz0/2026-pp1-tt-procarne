"""Composición de la aplicación ROCCA.

Crea la instancia de FastAPI, configura CORS y registra los routers
de todos los módulos.

Uso::

    from app.app import crear_app
    app = crear_app()
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from configs.dao import crear_dao
from core.persona.dao import PersonaDAO
from core.persona.servicio import PersonaService
from modulos.registro_operadores.registro_operadores import RegistroOperadoresModulo

# Sprint actual: solo Módulo I (Registro de Operadores)
# Los demás módulos se reactivan al ampliar el scope:
# from core.mercaderia.dao import MercaderiaDAO
# from core.mercaderia.servicio import MercaderiaService
# from modulos.fiscalizacion.fiscalizacion import FiscalizacionModulo
# from modulos.remitos_carnicos.remitos_carnicos import RemitosCarnicosModulo
# from modulos.trazabilidad_comercial.trazabilidad_comercial import TrazabilidadComercialModulo


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
        """Sirve el build de React (dist) y el fallback SPA (BrowserRouter).

        El directorio se genera con `pnpm build` en el frontend y se emite
        en app/static/. Se registra DESPUÉS de los routers /api/* para que
        las rutas de la API tengan prioridad.

        - Los assets con extensión (js, css, imágenes, fuentes) se sirven
          directamente del build.
        - Cualquier otra ruta (p. ej. /modulo-vi) devuelve index.html para
          que react-router resuelva el cliente.
        """
        static_dir = Path(__file__).resolve().parent / "static"
        if not static_dir.is_dir():
            return

        index_file = static_dir / "index.html"
        static_root = str(static_dir.resolve())

        def responder_index():
            if index_file.is_file():
                return FileResponse(index_file)
            raise HTTPException(status_code=404, detail="Frontend no construido")

        @self.app.get("/{ruta:path}", include_in_schema=False)
        def servir_spa(ruta: str):
            # Asset con extensión: servir el archivo estático si existe.
            nombre = ruta.rsplit("/", 1)[-1]
            if "." in nombre:
                archivo = (static_dir / ruta).resolve()
                if str(archivo).startswith(static_root) and archivo.is_file():
                    return FileResponse(archivo)
            # Sino: fallback SPA → index.html.
            return responder_index()

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

        # Módulo I — Registro Provincial de Operadores
        registro = RegistroOperadoresModulo(
            db_dao,
            persona_dao=persona_dao,
            persona_service=persona_service,
        )
        registro.registrar(self.app)

        # --- Módulos fuera del scope del sprint actual (comentados) ---
        # mercaderia_dao = MercaderiaDAO(db_dao.obtener_sesion)
        # mercaderia_service = MercaderiaService(mercaderia_dao)
        #
        # remitos = RemitosCarnicosModulo(
        #     db_dao,
        #     persona_dao=persona_dao,
        #     persona_service=persona_service,
        #     mercaderia_dao=mercaderia_dao,
        #     mercaderia_service=mercaderia_service,
        # )
        # remitos.registrar(self.app)
        #
        # trazabilidad = TrazabilidadComercialModulo(db_dao)
        # trazabilidad.registrar(self.app)
        #
        # fiscalizacion = FiscalizacionModulo(db_dao)
        # fiscalizacion.registrar(self.app)

    def crear(self) -> FastAPI:
        """Compone la aplicación completa y la devuelve lista para servir."""
        self.registrar_modulos()
        self._montar_frontend()
        return self.app


def crear_app() -> FastAPI:
    """Factory: crea la aplicación ROCCA con todos los módulos registrados."""
    return RoccaApp().crear()
