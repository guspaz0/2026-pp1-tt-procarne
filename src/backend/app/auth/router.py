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
        """Alta de usuario (siempre crea un operador).

        **Requisito**: Debe proporcionar un CUIT o DNI. Si no, se rechaza con 422.

        Flujo (happy path):
        1. Validar formato del documento (CUIT/DNI) → 422.
        2. Pre-checks: email no asignado a otra Persona → 409.
        3. Signup en InsForge → 409 si email ya existe.
        4. Crear/Resolver Persona.
        5. Actualizar ``user_metadata`` con ``persona_id`` (siempre).

        **Resultado**: Todos los usuarios creados por signup tienen rol ``operador``
        (porque siempre tienen ``persona_id`` en ``user_metadata``).

        Compensaciones:
        - Si el signup en InsForge falla → no se crea Persona (nada que revertir).
        - Si la Persona falla → se elimina el usuario de InsForge.
        """
        from fastapi import HTTPException
        from core.cuit.validator import CuitError, CuitValidator, validar_formato_cuit
        from core.persona.schema import PersonaIn

        # 0) RECHAZAR si no se provee CUIT o DNI.
        if not payload.cuit:
            raise HTTPException(
                status_code=422,
                detail="Debes proporcionar un CUIT o DNI para registrarte.",
            )

        # Normalizar el tipo de documento (mayúsculas).
        tipo_doc = (payload.tipo_documento or "CUIT").upper()

        # 1) Validar el documento ANTES de crear el usuario en InsForge.
        identificador_norm = payload.cuit
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

        # 2) Pre-checks: verificar que el email no esté ya asignado a otra
        #    Persona. Si está, se rechaza ANTES de crear el usuario.
        persona_id: int | None = None
        persona_creada_en_signup = False  # Flag para compensación.
        persona_service = _persona_service()
        if persona_service is None:
            raise HTTPException(
                status_code=503,
                detail="PersonaService no disponible: no se puede verificar la Persona.",
            )
        persona_por_email = persona_service.obtener_por_email(payload.email)
        if persona_por_email is not None:
            raise HTTPException(
                status_code=409,
                detail="Ese email ya está registrado con otra persona.",
            )
        existente = persona_service.obtener_por_documento(
            tipo_doc, identificador_norm
        )
        if existente is not None:
            persona_id = existente.id

        # 3) Signup en InsForge.
        metadata = dict(payload.user_metadata or {})
        if persona_id is not None:
            metadata["persona_id"] = persona_id
        try:
            session = await auth.signup(
                payload.email,
                payload.password,
                response,
                name=payload.name,
                metadata=metadata,
            )
        except AuthError as e:
            # Si el signup falla, no se creó Persona → nada que revertir.
            raise HTTPException(status_code=e.status_code, detail=e.detail)

        # 4) Crear la Persona (solo si no existía) y vincular.
        if persona_id is None:
            try:
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
                persona_creada_en_signup = True
            except Exception:
                # COMPENSACIÓN: la Persona falló → eliminar el usuario de InsForge.
                user_id = (
                    session["user"].get("id") if isinstance(session.get("user"), dict) else None
                )
                if user_id:
                    try:
                        await auth.delete_user(user_id)
                    except AuthError:
                        pass  # Loggear: queda usuario huérfano sin Persona.
                raise HTTPException(
                    status_code=500,
                    detail="No se pudo crear la Persona. El usuario fue eliminado.",
                )

        # 5) Actualizar el payload con el rol correcto.
        #    auth.signup() ya devolvió el payload (dict); solo hay que
        #    sobrescribir rol/persona_id con los valores resueltos de la DB.
        if isinstance(session, dict):
            session.setdefault("user", {})["rol"] = "operador"
            session["user"]["persona_id"] = persona_id
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
    async def me(
        user: schemas.UserOut = Depends(require_user),
        auth: AuthService = Depends(get_auth_service),
    ):
        """Datos del usuario autenticado (ruta protegida).

        El rol se resuelve consultando la tabla ``personas`` por email:
        si existe una persona con ese email → ``operador``; si no → ``admin``.
        """
        rol, persona_id = auth._resolver_rol(user.email)
        return {
            "id": user.id,
            "email": user.email,
            "rol": rol,
            "persona_id": persona_id,
            "must_change_password": False,
        }

    @router.post("/change-password", status_code=200)
    async def change_password(
        payload: schemas.ChangePasswordRequest,
        user: schemas.UserOut = Depends(require_user),
        auth: AuthService = Depends(get_auth_service),
    ):
        """Cambia la contraseña del usuario autenticado.

        Después del cambio, se elimina el flag ``must_change_password``
        de la ``user_metadata`` para que no se pida el cambio en el
        próximo login.
        """
        from fastapi import HTTPException

        if not user.id:
            raise HTTPException(status_code=401, detail="Usuario no identificado")

        try:
            await auth.change_password(user.id, payload.new_password)
        except AuthError as e:
            raise HTTPException(status_code=e.status_code, detail=e.detail)

        # Quitar el flag must_change_password (si existía).
        try:
            await auth.update_user_metadata(user.id, {"must_change_password": False})
        except AuthError:
            pass  # No fatal: se pedirá el cambio en el próximo login.

        return {"detail": "Contraseña actualizada correctamente."}

    return router
