"""Controlador (router API) de ``Categoria``.

Ruta:
- ``GET /api/registro-operadores/categorias`` — lista de categorías con sus
  requisitos de papeleo anidados (alimenta el select de categorías y el
  checklist de requisitos del formulario de inscripción).

IMPORTANTE: declarar el router ANTES que las rutas ``/{operador_id}`` del
router de operadores para que ``/categorias`` no sea capturado como id.
"""

from __future__ import annotations

from fastapi import APIRouter

from modulos.registro_operadores.categoria.dto import CategoriaOut
from modulos.registro_operadores.categoria.servicio import CategoriaService


def crear_router(servicio: CategoriaService, prefix: str = "") -> APIRouter:
    """Crea el router API de categorías del módulo de registro."""
    router = APIRouter(prefix=prefix, tags=["Registro de Operadores"])

    @router.get("/categorias", response_model=list[CategoriaOut])
    def listar_categorias():
        """Lista todas las categorías con sus requisitos de papeleo."""
        return servicio.listar()

    return router
