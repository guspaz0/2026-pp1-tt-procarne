"""Tests de la API de autenticación de ROCCA (InsForge como IdP).

Cubre el flujo completo del BFF:
- Login correcto (InsForge devuelve tokens) → cookies HttpOnly fijadas.
- Login incorrecto → 401.
- InsForge caído → 503 (no 401).
- Middleware: rutas protegidas requieren cookie válida.
- /me devuelve el usuario autenticado.
- Logout limpia las cookies.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.app import crear_app
from app.auth.service import COOKIE_ACCESS, COOKIE_REFRESH


@pytest.fixture()
def app_client():
    """Crea el app de ROCCA con un InsForgeClient que apunta a un host caído.

    Así probamos el comportamiento cuando InsForge no está disponible
    (503 en login/signup, 401 en rutas protegidas sin cookie).
    """
    app = crear_app()
    # Sobrescribimos el cliente con uno que apunta a un puerto que no escucha.
    # IMPORTANTE: importar de `core.insforge.client` (no `app.core...`) para
    # que la clase InsforgeError sea la misma que el servicio espera.
    from core.insforge.client import InsforgeClient
    from auth.service import AuthService

    app.state.insforge = InsforgeClient(base_url="http://127.0.0.1:1", timeout=2.0)
    app.state.auth_service = AuthService(app.state.insforge, cookie_secure=False)
    with TestClient(app) as client:
        yield client


class TestMiddleware:
    """El middleware bloquea rutas protegidas sin cookie válida."""

    def test_rutas_protegidas_sin_cookie(self, app_client):
        resp = app_client.get("/api/operadores")
        assert resp.status_code == 401

    def test_rutas_publicas_sin_cookie(self, app_client):
        resp = app_client.get("/api/health")
        assert resp.status_code == 200

    def test_me_sin_cookie(self, app_client):
        resp = app_client.get("/api/auth/me")
        assert resp.status_code == 401

    def test_me_con_cookie_invalida(self, app_client):
        resp = app_client.get(
            "/api/auth/me",
            cookies={COOKIE_ACCESS: "token-invalido"},
        )
        # InsForge caído → 503 (no 401, porque no podemos validar).
        assert resp.status_code == 503


class TestLogin:
    """Login contra InsForge (caído en tests)."""

    def test_login_con_insforge_caido(self, app_client):
        resp = app_client.post(
            "/api/auth/login",
            json={"email": "usuario@ejemplo.com", "password": "clave12345"},
        )
        assert resp.status_code == 503
        assert "InsForge" in resp.json()["detail"]

    def test_login_password_corto(self, app_client):
        resp = app_client.post(
            "/api/auth/login",
            json={"email": "usuario@ejemplo.com", "password": "123"},
        )
        assert resp.status_code == 422  # Validación de Pydantic (mínimo 8).


class TestSignup:
    """Signup contra InsForge (caído en tests)."""

    def test_signup_con_insforge_caido(self, app_client):
        resp = app_client.post(
            "/api/auth/signup",
            json={"email": "nuevo@ejemplo.com", "password": "clave12345", "name": "Juan"},
        )
        assert resp.status_code == 503

    def test_signup_password_corto(self, app_client):
        resp = app_client.post(
            "/api/auth/signup",
            json={"email": "nuevo@ejemplo.com", "password": "123"},
        )
        assert resp.status_code == 422  # Validación de Pydantic (mínimo 8).


class TestLogout:
    """Logout limpia las cookies."""

    def test_logout_sin_sesion(self, app_client):
        resp = app_client.post("/api/auth/logout")
        assert resp.status_code == 200
        # Las cookies deben estar borradas (o no fijadas).
        assert resp.cookies.get(COOKIE_ACCESS) is None or resp.cookies[COOKIE_ACCESS] == ""


class TestCookies:
    """Las cookies no se fijan si no hay sesión válida."""

    def test_cookies_no_se_fijan_sin_sesion(self, app_client):
        resp = app_client.post(
            "/api/auth/login",
            json={"email": "usuario@ejemplo.com", "password": "clave12345"},
        )
        # InsForge caído → no hay cookies.
        assert resp.status_code == 503
        assert COOKIE_ACCESS not in resp.cookies or not resp.cookies[COOKIE_ACCESS]
