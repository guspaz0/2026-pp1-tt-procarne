"""ROCCA — backend.

Punto de entrada: instancia la aplicación y expone la instancia de
:class:`FastAPI` para uvicorn.

Uso::

    uvicorn app.main:app --reload
"""

from .app import RoccaApp, crear_app

# Instancia única de la aplicación (se crea al importar este módulo)
_rocca = RoccaApp()
app = _rocca.app

__all__ = ["app", "RoccaApp", "crear_app"]
