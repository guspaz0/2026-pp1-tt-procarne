"""Servicio de negocio de la mercadería."""

from __future__ import annotations

from .dao import Mercaderia, MercaderiaDAO
from .schema import MercaderiaIn, MercaderiaOut


class MercaderiaError(Exception):
    """Error de negocio del módulo de mercaderías."""


class MercaderiaService:
    """Caso de uso: gestión del catálogo de mercaderías."""

    def __init__(self, dao: MercaderiaDAO) -> None:
        self._dao = dao

    def crear(self, datos: MercaderiaIn) -> MercaderiaOut:
        existente = self._dao.obtener_por_codigo(datos.codigo_afip)
        if existente is not None:
            raise MercaderiaError(f"Mercadería ya existe: código AFIP {datos.codigo_afip}")

        mercaderia = Mercaderia(
            codigo_afip=datos.codigo_afip,
            descripcion=datos.descripcion,
            requiere_numero_tropa=datos.requiere_numero_tropa,
        )
        guardado = self._dao.guardar(mercaderia)
        return self._a_dto(guardado)

    def obtener(self, codigo_afip: str) -> MercaderiaOut:
        mercaderia = self._dao.obtener_por_codigo(codigo_afip)
        if mercaderia is None:
            raise MercaderiaError(f"Mercadería no encontrada: código AFIP {codigo_afip}")
        return self._a_dto(mercaderia)

    def listar(self, limite: int = 200, offset: int = 0) -> list[MercaderiaOut]:
        mercaderias = self._dao.listar(limite=limite, offset=offset)
        return [self._a_dto(m) for m in mercaderias]

    @staticmethod
    def _a_dto(mercaderia: Mercaderia) -> MercaderiaOut:
        return MercaderiaOut(
            id=mercaderia.id,
            codigo_afip=mercaderia.codigo_afip,
            descripcion=mercaderia.descripcion,
            requiere_numero_tropa=mercaderia.requiere_numero_tropa,
        )
