"""Servicio de Requisitos."""

from __future__ import annotations

from typing import Optional

from modulos.registro_operadores.requisito.dao import Requisito, RequisitoDAO


class RequisitoService:
    """Servicio de requisitos de inscripción (ligados a categoría)."""

    def __init__(self, dao: RequisitoDAO) -> None:
        self._dao = dao

    def listar_por_categoria(self, categoria_id: int) -> list[Requisito]:
        """Lista los requisitos de una categoría."""
        return self._dao.listar_por_categoria(categoria_id)

    def obtener(self, requisito_id: int) -> Optional[Requisito]:
        """Obtiene un requisito por su id."""
        return self._dao.obtener_por_id(requisito_id)

    def crear(self, categoria_id: int, nombre: str,
              descripcion: str | None = None,
              obligatorio: bool = True) -> Requisito:
        """Crea un requisito nuevo."""
        return self._dao.crear(categoria_id, nombre, descripcion, obligatorio)

    def actualizar(self, requisito_id: int, **kwargs) -> Optional[Requisito]:
        """Actualiza un requisito."""
        return self._dao.actualizar(requisito_id, **kwargs)

    def eliminar(self, requisito_id: int) -> bool:
        """Elimina un requisito."""
        return self._dao.eliminar(requisito_id)
