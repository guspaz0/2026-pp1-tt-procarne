"""Punto de entrada de la aplicación ROCCA.

Ejecuta el servidor Uvicorn con la aplicación FastAPI compuesta por
todos los módulos.

Uso::

    python main.py
"""

import uvicorn

from app.app import crear_app

app = crear_app()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
