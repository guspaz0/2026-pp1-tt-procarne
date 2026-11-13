"""Servicio de Categorías."""

from __future__ import annotations

from typing import Optional

from modulos.registro_operadores.categoria.dao import Categoria, CategoriaDAO


class CategoriaService:
    """Servicio de categorías de operador."""

    def __init__(self, dao: CategoriaDAO) -> None:
        self._dao = dao

    def listar(self) -> list[Categoria]:
        """Lista todas las categorías."""
        return self._dao.listar()

    def obtener(self, categoria_id: int) -> Optional[Categoria]:
        """Obtiene una categoría por su id."""
        return self._dao.obtener_por_id(categoria_id)

    def crear(self, nombre: str, descripcion: str | None = None,
              ciclo: str | None = None) -> Categoria:
        """Crea una categoría nueva."""
        return self._dao.crear(nombre, descripcion, ciclo)

    def actualizar(self, categoria_id: int, **kwargs) -> Optional[Categoria]:
        """Actualiza una categoría."""
        return self._dao.actualizar(categoria_id, **kwargs)
