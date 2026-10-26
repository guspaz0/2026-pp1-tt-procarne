"""Paquete de aplicación ROCCA.

Añade el propio directorio a ``sys.path`` para que los subpaquetes
``configs`` y ``modulos`` sean importables como top-level (``import configs.db``),
tanto desde ``main.py`` como desde los tests y Alembic.
"""

from __future__ import annotations

import sys
from pathlib import Path

_APP_DIR = str(Path(__file__).resolve().parent)
if _APP_DIR not in sys.path:
    sys.path.insert(0, _APP_DIR)
