"""Router de autenticación de ROCCA (BFF → InsForge).

Endpoints (todos bajo ``/api/auth``):
- ``POST /api/auth/login``    → login por email+contraseña, fija cookies HttpOnly.
- ``POST /api/auth/signup``   → alta de usuario (con API key admin), fija cookies.
- ``POST /api/auth/refresh``  → renueva la sesión con el refresh token.
- ``POST /api/auth/logout``   → cierra sesión en InsForge y limpia cookies.
- ``GET  /api/auth/me``       → datos del usuario autenticado (ruta protegida).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request, Response
from starlette.status import HTTP_401_UNAUTHORIZED

from auth import schemas
from auth.dependencies import require_user
from auth.service import AuthError, AuthService


_persona_service_holder: dict = {}


def _persona_service():
    """Devuelve el ``PersonaService`` (fijado por :func:`set_persona_service`)."""
    return _persona_service_holder.get("service")


def set_persona_service(service) -> None:
    """Fija el ``PersonaService`` para que el signup pueda crear/vincular Personas."""
    _persona_service_holder["service"] = service


def crear_router(get_auth_service) -> APIRouter:
    """Crea el router de autenticación.

    :param get_auth_service: callable que devuelve el ``AuthService`` (Depends).
    """
    router = APIRouter(prefix="/api/auth", tags=["Autenticación"])

    @router.post("/login", response_model=schemas.SessionOut)
    async def login(
        payload: schemas.LoginRequest,
        response: Response,
        auth: AuthService = Depends(get_auth_service),
    ):
        from fastapi import HTTPException

        try:
            print(payload)
            return await auth.login(payload.email, payload.password, response)
        except AuthError as e:
            raise HTTPException(status_code=e.status_code, detail=e.detail)

    @router.post("/signup", response_model=schemas.SessionOut, status_code=201)
    async def signup(
        payload: schemas.SignupRequest,
        response: Response,
        auth: AuthService = Depends(get_auth_service),
    ):
        """Alta de usuario.

        Flujo:
        1. **Validar el documento** (solo si es CUIT): formato local + padrón
           público (IDFiscal). Si no es válido, se rechaza con ``422`` **antes**
           de crear el usuario en InsForge (no queda ningún usuario huérfano).
        2. Crear el usuario en InsForge (signup).
        3. **Solo si el signup tuvo éxito** y el payload trae documento:
           resolver/crear la ``Persona`` y vincular su id al usuario en
           ``user_metadata`` (InsForge lo expone en el JWT).
        """
        from fastapi import HTTPException
        from core.cuit.validator import CuitError, CuitValidator, validar_formato_cuit
        from core.persona.schema import PersonaIn

        # Normalizar el tipo de documento (mayúsculas).
        tipo_doc = (payload.tipo_documento or "CUIT").upper()

        # 1) Validar el documento ANTES de crear el usuario en InsForge.
        identificador_norm = payload.cuit or ""
        if payload.cuit:
            if tipo_doc == "CUIT":
                # Validar formato (11 dígitos + dígito verificador) y padrón.
                try:
                    identificador_norm = validar_formato_cuit(payload.cuit)
                    validator = CuitValidator()
                    await validator.validar(payload.cuit)
                except CuitError as e:
                    raise HTTPException(status_code=e.status_code, detail=e.detail)
            elif tipo_doc == "DNI":
                # DNI: solo validamos el formato (8 dígitos). No se consulta
                # el padrón (la API de IDFiscal solo valida CUIT).
                dni_digits = "".join(ch for ch in payload.cuit if ch.isdigit())
                if len(dni_digits) != 8:
                    raise HTTPException(
                        status_code=422, detail="El DNI debe tener 8 dígitos."
                    )
                identificador_norm = dni_digits
            else:
                raise HTTPException(
                    status_code=422,
                    detail=f"Tipo de documento no soportado: {tipo_doc}",
                )

        # 2) Signup en InsForge (sin metadata de persona todavía).
        try:
            session = await auth.signup(
                payload.email,
                payload.password,
                response,
                name=payload.name,
                metadata=dict(payload.user_metadata or {}),
            )
        except AuthError as e:
            raise HTTPException(status_code=e.status_code, detail=e.detail)

        # 3) Persona: solo después de que el signup haya sido exitoso.
        if payload.cuit:
            persona_service = _persona_service()
            if persona_service is None:
                # El usuario ya existe en InsForge; no lo borramos. Solo
                # reportamos que no se pudo vincular la Persona.
                raise HTTPException(
                    status_code=503,
                    detail="PersonaService no disponible: el usuario se creó pero la Persona no se vinculó",
                )
            existente = persona_service.obtener_por_documento(
                tipo_doc, identificador_norm
            )
            if existente is not None:
                persona_id = existente.id
            else:
                # CUIT → persona jurídica (PJ); DNI → persona física (PF).
                tipo_persona = "PJ" if tipo_doc == "CUIT" else "PF"
                creada = persona_service.crear_persona(
                    PersonaIn(
                        tipo=tipo_persona,
                        tipo_documento=tipo_doc,
                        identificador=identificador_norm,
                        nombre=payload.name or identificador_norm,
                        email=payload.email,
                    )
                )
                persona_id = creada.id

            # 4) Vincular persona_id al usuario en InsForge (user_metadata).
            #    InsForge lo expone en el JWT de la próxima sesión.
            try:
                user_id = (
                    session.user.get("id") if isinstance(session.user, dict) else None
                )
                if user_id:
                    await auth.update_user_metadata(user_id, {"persona_id": persona_id})
            except AuthError:
                # No es fatal: la Persona ya existe y el cliente puede
                # re-vincularla en el próximo login/refresh.
                pass

        return session

    @router.post("/refresh", response_model=schemas.SessionOut)
    async def refresh(
        request: Request,
        response: Response,
        auth: AuthService = Depends(get_auth_service),
    ):
        from auth.service import COOKIE_REFRESH

        token = request.cookies.get(COOKIE_REFRESH) or ""
        try:
            return await auth.refresh(token, response)
        except AuthError as e:
            from fastapi import HTTPException

            raise HTTPException(status_code=e.status_code, detail=e.detail)

    @router.post("/logout")
    async def logout(
        request: Request,
        response: Response,
        auth: AuthService = Depends(get_auth_service),
    ):
        from auth.service import COOKIE_REFRESH

        token = request.cookies.get(COOKIE_REFRESH)
        return await auth.logout(response, refresh_token=token)

    @router.get("/me")
    async def me(user: schemas.UserOut = Depends(require_user)):
        """Datos del usuario autenticado (ruta protegida)."""
        return user

    return router
