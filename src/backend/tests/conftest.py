"""Conftest raíz: prepara el path para importar el paquete ``app``.

Los módulos internos (``configs``, ``modulos``) se importan como
top-level gracias al shim de ``app/__init__.py``; basta con que el
directorio ``src/backend`` esté en ``sys.path`` y se importe ``app``.
"""

from __future__ import annotations

import sys
from pathlib import Path

_BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

import app  # noqa: F401  # añade app/ a sys.path (shim)


def montar_auth_testeable(app, persona_id: int = 1, rol: str = "supervisor"):
    """Monta un middleware de test que fija ``request.state.user``.

    Permite probar los endpoints protegidos sin InsForge. El usuario simulado
    tiene ``persona_id`` y ``rol`` (por defecto supervisor/admin, que omite
    las verificaciones de titularidad en el backend).
    """
    from starlette.middleware.base import BaseHTTPMiddleware

    class _TestAuthMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            request.state.user = {
                "sub": "test-user",
                "email": "test@example.com",
                "name": "Test User",
                "user_metadata": {"persona_id": persona_id, "rol": rol},
            }
            return await call_next(request)

    app.add_middleware(_TestAuthMiddleware)
