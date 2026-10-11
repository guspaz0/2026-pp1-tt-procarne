"""ROCCA — backend.

Al importar el paquete ``app`` se añade el propio directorio a
``sys.path`` para que los módulos internos (``configs``, ``modulos``)
puedan importarse como top-level, tal como están escritos en el código.
"""

import sys
from pathlib import Path

_APP_DIR = str(Path(__file__).resolve().parent)
if _APP_DIR not in sys.path:
    sys.path.insert(0, _APP_DIR)
