"""Servicio de negocio de la mercadería."""

from __future__ import annotations

from .dao import Mercaderia, MercaderiaDAO
from .schema import MercaderiaIn, MercaderiaOut


class MercaderiaError(Exception):
    """Error de negocio del módulo de mercaderías."""


class MercaderiaService:
    """Caso de uso: gestión del catálogo genérico de mercaderías."""

    def __init__(self, dao: MercaderiaDAO) -> None:
        self._dao = dao

    def crear(self, datos: MercaderiaIn) -> MercaderiaOut:
        existente = self._dao.obtener_por_codigo(datos.codigo)
        if existente is not None:
            raise MercaderiaError(f"Mercadería ya existe: código {datos.codigo}")

        mercaderia = Mercaderia(
            codigo=datos.codigo,
            descripcion=datos.descripcion,
            unidad_medida=datos.unidad_medida,
            requiere_trazabilidad=datos.requiere_trazabilidad,
            requiere_numero_tropa=datos.requiere_numero_tropa,
        )
        guardado = self._dao.guardar(mercaderia)
        return MercaderiaOut.model_validate(guardado)

    def obtener(self, codigo: str) -> MercaderiaOut:
        mercaderia = self._dao.obtener_por_codigo(codigo)
        if mercaderia is None:
            raise MercaderiaError(f"Mercadería no encontrada: código {codigo}")
        return MercaderiaOut.model_validate(mercaderia)

    def listar(self, limite: int = 200, offset: int = 0) -> list[MercaderiaOut]:
        mercaderias = self._dao.listar(limite=limite, offset=offset)
        return [MercaderiaOut.model_validate(m) for m in mercaderias]
