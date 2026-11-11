"""Lógica de negocio de ``AdjuntoOperador``.

Reglas:
- Solo se aceptan ``image/jpeg``, ``image/png`` y ``application/pdf``.
- Tamaño máximo: 10 MB.
- El requisito debe corresponder a la categoría del operador
  (validación delegada en :class:`RequisitoInscripcionService`).
"""

from __future__ import annotations

from modulos.registro_operadores.adjunto_operador.dao import AdjuntoOperador, AdjuntoOperadorDAO
from modulos.registro_operadores.adjunto_operador.dto import AdjuntoOperadorOut
from modulos.registro_operadores.operador.servicio import OperadorError
from modulos.registro_operadores.requisito_inscripcion.servicio import RequisitoInscripcionService

_TIPOS_PERMITIDOS = ("image/jpeg", "image/png", "application/pdf")
_TAMANO_MAXIMO = 10 * 1024 * 1024  # 10 MB


class AdjuntoOperadorService:
    """Servicio de negocio de adjuntos (documentos) de operador."""

    def __init__(self, dao: AdjuntoOperadorDAO, storage=None,
                 operador_dao=None,
                 requisito_service: RequisitoInscripcionService | None = None) -> None:
        self._dao = dao
        self._storage = storage
        self._operador_dao = operador_dao
        self._requisito_service = requisito_service

    async def subir(self, operador_id: int, requisito: str, filename: str,
                    content_type: str, size: int, data: bytes) -> AdjuntoOperadorOut:
        """Sube un adjunto a storage y registra la fila en BD."""
        if self._storage is None:
            raise OperadorError("Storage no configurado")

        # Verificar que el operador existe
        operador = self._operador_dao.obtener_por_id(operador_id) if self._operador_dao else None
        if operador is None:
            raise OperadorError(f"No existe un operador con id {operador_id}")

        # Validar content type
        if content_type not in _TIPOS_PERMITIDOS:
            raise OperadorError(f"Tipo de archivo no permitido: {content_type}")
        # Validar tamaño
        if size > _TAMANO_MAXIMO:
            raise OperadorError("Archivo excede el tamaño máximo de 10 MB")
        # Validar que el requisito corresponda a la categoría
        if self._requisito_service is not None:
            categoria = operador.categoria or ""
            if not self._requisito_service.validar_requisito_para_categoria(categoria, requisito):
                raise OperadorError(
                    f"El requisito '{requisito}' no corresponde a la categoría '{categoria}'"
                )

        # Subir a storage
        storage_key = await self._storage.upload(filename, content_type, size, data)

        # Registrar en BD
        adjunto = self._dao.crear(
            operador_id=operador_id,
            requisito=requisito,
            storage_key=storage_key,
            content_type=content_type,
            size=size,
            nombre_original=filename,
        )
        return self._a_out(adjunto)

    def listar(self, operador_id: int) -> list[AdjuntoOperadorOut]:
        """Lista los adjuntos de un operador."""
        adjuntos = self._dao.listar_por_operador(operador_id)
        return [self._a_out(a) for a in adjuntos]

    async def obtener_url(self, operador_id: int, adjunto_id: int) -> str:
        """Obtiene una URL firmada para descargar un adjunto."""
        if self._storage is None:
            raise OperadorError("Storage no configurado")
        adjunto = self._dao.obtener_por_id(adjunto_id)
        if adjunto is None or adjunto.operador_id != operador_id:
            raise OperadorError(f"No existe un adjunto {adjunto_id} para el operador {operador_id}")
        return await self._storage.download_url(adjunto.storage_key)

    async def eliminar(self, operador_id: int, adjunto_id: int) -> None:
        """Elimina un adjunto (fila + objeto en storage)."""
        adjunto = self._dao.obtener_por_id(adjunto_id)
        if adjunto is None or adjunto.operador_id != operador_id:
            raise OperadorError(f"No existe un adjunto {adjunto_id} para el operador {operador_id}")
        if self._storage:
            try:
                await self._storage.delete(adjunto.storage_key)
            except Exception:
                pass
        self._dao.eliminar(adjunto_id)

    def validar_requisito_para_categoria(self, categoria: str, requisito: str) -> bool:
        """Indica si ``requisito`` corresponde a ``categoria`` (delega en
        :class:`RequisitoInscripcionService`)."""
        if self._requisito_service is None:
            # Sin servicio de requisitos, se asume válido (no se puede validar).
            return True
        return self._requisito_service.validar_requisito_para_categoria(categoria, requisito)

    @staticmethod
    def _a_out(adjunto: AdjuntoOperador) -> AdjuntoOperadorOut:
        return AdjuntoOperadorOut(
            id=adjunto.id,
            operador_id=adjunto.operador_id,
            requisito=adjunto.requisito,
            storage_key=adjunto.storage_key,
            content_type=adjunto.content_type,
            size=adjunto.size,
            nombre_original=adjunto.nombre_original,
            creado_en=adjunto.creado_en,
        )
