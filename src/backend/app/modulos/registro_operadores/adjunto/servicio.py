"""Servicio de Adjuntos."""

from __future__ import annotations

from typing import Optional

from modulos.registro_operadores.adjunto.dao import Adjunto, AdjuntoDAO


class AdjuntoService:
    """Servicio de adjuntos (documentos digitales)."""

    def __init__(self, dao: AdjuntoDAO, storage=None,
                 operador_dao=None, requisito_service=None) -> None:
        self._dao = dao
        self._storage = storage
        self._operador_dao = operador_dao
        self._requisito_service = requisito_service

    def listar_por_operador(self, operador_id: int) -> list[Adjunto]:
        """Lista todos los adjuntos de un operador."""
        return self._dao.listar_por_operador(operador_id)

    def listar_por_operador_y_requisito(
        self, operador_id: int, requisito_id: int
    ) -> list[Adjunto]:
        """Lista los adjuntos de un operador para un requisito específico."""
        return self._dao.listar_por_operador_y_requisito(operador_id, requisito_id)

    def obtener(self, adjunto_id: int) -> Optional[Adjunto]:
        """Obtiene un adjunto por su id."""
        return self._dao.obtener_por_id(adjunto_id)

    def crear(
        self,
        operador_id: int,
        requisito_id: int,
        storage_key: str,
        content_type: str,
        size: int,
        nombre_original: str,
    ) -> Adjunto:
        """Crea un adjunto nuevo."""
        return self._dao.crear(operador_id, requisito_id, storage_key,
                               content_type, size, nombre_original)

    def eliminar(self, adjunto_id: int) -> bool:
        """Elimina un adjunto."""
        return self._dao.eliminar(adjunto_id)
