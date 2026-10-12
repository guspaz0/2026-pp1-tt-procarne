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
