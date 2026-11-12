"""Composición de la aplicación ROCCA.

Crea la instancia de FastAPI, configura CORS y registra los routers
de todos los módulos.

Uso::

    from app.app import crear_app
    app = crear_app()
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv

# Cargar .env desde la raíz del repo (o desde el directorio actual si existe).
# En producción (Vercel) las vars ya están en el entorno; esto solo ayuda en dev local.
_env_candidates = [
    Path(__file__).resolve().parents[3] / ".env",  # repo root
    Path.cwd() / ".env",
]
for _p in _env_candidates:
    if _p.exists():
        load_dotenv(_p, override=False)  # no sobreescribir vars ya definidas
        break

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from auth.middleware import InsForgeAuthMiddleware
from auth.router import crear_router as crear_router_auth
from auth.service import AuthService
from configs.dao import crear_dao
from core.insforge.client import InsforgeClient
from core.persona.adjunto_dao import AdjuntoPersonaDAO
from core.persona.controlador import crear_router as crear_router_persona
from core.persona.dao import PersonaDAO
from core.persona.servicio import PersonaService
from core.storage.insforge import InsforgeStorage
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
            lifespan=self._lifespan,
        )
        self._configurar_cors()
        # Middleware de autenticación (InsForge como IdP). Se registra antes que
        # CORS para que CORS procese las respuestas (incl. 401) correctamente.
        self.app.add_middleware(InsForgeAuthMiddleware, auth_service=self._auth_service)

    def _configurar_cors(self) -> None:
        """Configura el middleware CORS.

        Con cookies de sesión (credentials) NO se puede usar origin wildcard:
        se enumeran los orígenes reales del frontend. En desarrollo se toma
        ``ROCCA_CORS_ORIGINS`` (lista separada por comas) o un default.
        """
        origins = os.environ.get(
            "ROCCA_CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173,http://localhost:8000,http://127.0.0.1:8000",
        ).split(",")
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=[o.strip() for o in origins if o.strip()],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # ------------------------------------------------------------------
    # InsForge (IdP) + autenticación
    # ------------------------------------------------------------------

    def _crear_insforge(self) -> InsforgeClient:
        """Crea el cliente de InsForge a partir de las variables de entorno."""
        base_url = os.environ.get("INSFORGE_URL", "https://localhost:3000").rstrip("/")
        api_key = os.environ.get("INSFORGE_API_KEY", "")
        return InsforgeClient(base_url=base_url, api_key=api_key)

    @property
    def _auth_service(self) -> AuthService:
        """Servicio de autenticación (usa el cliente de InsForge del app.state).

        Si un test sobrescribió ``app.state.auth_service``, lo usamos; si no,
        creamos uno nuevo con el cliente de InsForge configurado.
        """
        # Si el lifespan ya fijó un auth_service en app.state, lo usamos.
        if hasattr(self.app, "state") and hasattr(self.app.state, "auth_service"):
            return self.app.state.auth_service
        # Si no, creamos uno nuevo (primer arranque).
        if not hasattr(self, "_insforge_client"):
            self._insforge_client = self._crear_insforge()
        if not hasattr(self, "_auth"):
            self._auth = AuthService(self._insforge_client)
        return self._auth

    def _crear_storage(self) -> InsforgeStorage:
        """Crea el cliente de storage de InsForge."""
        base_url = os.environ.get("INSFORGE_URL", "https://localhost:3000").rstrip("/")
        api_key = os.environ.get("INSFORGE_API_KEY", "")
        bucket = os.environ.get("INSFORGE_BUCKET", "rocca-documentos")
        return InsforgeStorage(base_url=base_url, api_key=api_key, bucket=bucket)

    @asynccontextmanager
    async def _lifespan(self, app: FastAPI):
        """Abre el cliente de InsForge al arrancar y lo cierra al detener."""
        client = self._auth_service._client
        # InsforgeClient no tiene estado persistente (http.client), así que
        # solo lo exponemos en app.state para que los tests lo sobrescriban.
        app.state.insforge = client
        app.state.auth_service = self._auth_service
        # Storage
        if not hasattr(app.state, "storage"):
            app.state.storage = self._crear_storage()
        try:
            yield
        finally:
            await client.close()

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

    def registrar_modulos(self, db_dao=None) -> None:
        """Registra los routers de todos los módulos en la aplicación.

        ``db_dao`` permite inyectar un DAO específico (p. ej. en tests con BD
        temporal); si es ``None`` se crea uno con la URL por defecto.
        """
        # DAO compartido (inyección de dependencias)
        db_dao = db_dao or crear_dao()
        db_dao.crear_tablas()  # Asegura que las tablas existan (desarrollo)

        # Endpoint de salud
        @self.app.get("/api/health")
        def health():
            return {"status": "ok"}

        # Handlers globales para errores de autenticación (convierten a JSON).
        from auth.service import AuthError
        from core.insforge.client import InsforgeError

        @self.app.exception_handler(AuthError)
        async def auth_error_handler(request: Request, exc: AuthError):
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail},
            )

        @self.app.exception_handler(InsforgeError)
        async def insforge_error_handler(request: Request, exc: InsforgeError):
            status = 503 if exc.status_code == 0 else exc.status_code
            return JSONResponse(
                status_code=status,
                content={"detail": exc.detail},
            )

        # Catálogos genéricos compartidos (core)
        persona_dao = PersonaDAO(db_dao.obtener_sesion)
        adjunto_persona_dao = AdjuntoPersonaDAO(db_dao.obtener_sesion)
        storage: InsforgeStorage | None = getattr(self.app.state, "storage", None)
        persona_service = PersonaService(
            persona_dao,
            adjunto_dao=adjunto_persona_dao,
            storage=storage,
        )

        # Autenticación (InsForge como IdP): login/signup/refresh/logout/me.
        # El frontend habla solo con FastAPI; FastAPI orquesta InsForge.
        self.app.include_router(crear_router_auth(lambda: self._auth_service))

        # Personas (adjuntos de persona: DNI, CUIT, IIBB)
        self.app.include_router(crear_router_persona(persona_service))

        # Módulo I — Registro Provincial de Operadores
        registro = RegistroOperadoresModulo(
            db_dao,
            persona_dao=persona_dao,
            storage=storage,
        )
        registro.registrar(self.app)

        # Endpoint F102 (fallback local: invoca Node.js subprocess).
        # En Vercel, el frontend llama directamente a la Serverless Function
        # /api/f102/:id (Node.js), así que este endpoint solo se usa en dev.
        @self.app.get("/api/f102")
        def generar_f102(id: int):
            import subprocess
            import json as json_mod
            import base64 as b64
            from datetime import datetime, timedelta

            backend_dir = Path(__file__).resolve().parents[1]
            script_path = backend_dir / "generar_f102.mjs"
            if not script_path.exists():
                raise HTTPException(status_code=500, detail=f"Script no encontrado: {script_path}")

            # --- Datos reales del operador (antes eran hardcodeados) ---
            from modulos.registro_operadores.operador.dao import Operador
            from modulos.registro_operadores.certificado.dao import Certificado
            from modulos.registro_operadores.asociaciones import (
                OperadorActividad, CertificadoActividad,
            )
            from modulos.registro_operadores.actividad_economica.dao import ActividadEconomica
            from core.persona.dao import Persona

            with db_dao.obtener_sesion() as session:
                op = session.get(Operador, id)
                if op is None:
                    raise HTTPException(status_code=404, detail=f"Operador {id} no encontrado")
                persona = session.get(Persona, op.persona_id) if op.persona_id else None

                # Certificado vigente (el más reciente activo)
                cert = (
                    session.query(Certificado)
                    .filter(Certificado.operador_id == id)
                    .order_by(Certificado.fecha_emision.desc())
                    .first()
                )

                # Actividades del operador (N:M) → [codigo, descripcion]
                ops = (
                    session.query(OperadorActividad, ActividadEconomica)
                    .join(ActividadEconomica, OperadorActividad.actividad_id == ActividadEconomica.id)
                    .filter(OperadorActividad.operador_id == id)
                    .order_by(ActividadEconomica.codigo)
                    .all()
                )
                actividades_op = [[a.codigo, a.descripcion] for _, a in ops]

                # Actividades del certificado (N:M), si existe
                actividades_cert: list[list[str]] = []
                if cert is not None:
                    cts = (
                        session.query(CertificadoActividad, ActividadEconomica)
                        .join(ActividadEconomica, CertificadoActividad.actividad_id == ActividadEconomica.id)
                        .filter(CertificadoActividad.certificado_id == cert.id)
                        .order_by(ActividadEconomica.codigo)
                        .all()
                    )
                    actividades_cert = [[a.codigo, a.descripcion] for _, a in cts]

            # F102 es el certificado: las actividades del formulario son las del
            # certificado vigente; si no hay certificado, las del operador.
            actividades = actividades_cert or actividades_op

            cuit = persona.identificador if persona else ""
            nombre = persona.nombre.upper() if persona else ""
            domicilio = op.domicilio_comercial or (persona.domicilio if persona else None) or ""
            tipo_carne = op.categoria or ""
            fecha_inscrip = (cert.fecha_emision if cert else op.alta_fecha) or datetime.now()
            fecha_venc = cert.fecha_vencimiento if (cert and cert.fecha_vencimiento) else None

            payload = {
                "numero_operador": str(100000 + id),
                "apellido_y_nombre": nombre,
                "nombre_establecimiento": op.razon_social or "",
                "razon_social": op.razon_social or "",
                "cuit": cuit,
                "domicilio": domicilio,
                "tipo_carne": tipo_carne,
                "fecha_inscripcion": fecha_inscrip.isoformat(),
                "fecha_vencimiento": fecha_venc.isoformat() if fecha_venc else None,
                "actividades": actividades,
                "inscripciones": [["PRINCIPAL", fecha_inscrip.strftime("%d/%m/%Y")]],
            }

            try:
                result = subprocess.run(
                    ["node", str(script_path)],
                    input=json_mod.dumps(payload, ensure_ascii=False).encode("utf-8"),
                    capture_output=True,
                    timeout=30,
                    cwd=str(backend_dir),
                )
            except subprocess.TimeoutExpired:
                raise HTTPException(status_code=500, detail="Timeout generando PDF F102")
            except FileNotFoundError:
                raise HTTPException(status_code=500, detail="Node.js no encontrado en PATH")

            if result.returncode != 0:
                stderr = result.stderr.decode("utf-8", errors="replace")[:500]
                raise HTTPException(status_code=500, detail=f"Error generando PDF: {stderr}")

            pdf_bytes = result.stdout
            if not pdf_bytes.startswith(b"%PDF"):
                raise HTTPException(status_code=500, detail="El script no devolvió un PDF válido")

            return {
                "fileContents": b64.b64encode(pdf_bytes).decode("ascii"),
                "contentType": "application/pdf",
                "fileDownloadName": f"F102-{100000 + id}.pdf",
                "lastModified": None,
                "entityTag": None,
                "enableRangeProcessing": False,
            }

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
        return self.app

    def crear(self) -> FastAPI:
        """Compone la aplicación completa y la devuelve lista para servir."""
        self.registrar_modulos()
        self._montar_frontend()
        return self.app


def crear_app() -> FastAPI:
    """Factory: crea la aplicación ROCCA con todos los módulos registrados."""
    return RoccaApp().crear()
