"""Servicio de negocio de la mercadería (catálogo genérico)."""

from __future__ import annotations

from core.mercaderia.dao import Mercaderia, MercaderiaDAO
from core.mercaderia.schema import MercaderiaIn, MercaderiaOut


class MercaderiaError(Exception):
    """Error de negocio del servicio de mercaderías."""


class MercaderiaService:
    """Servicio de negocio de mercaderías."""

    def __init__(self, dao: MercaderiaDAO) -> None:
        self._dao = dao

    def crear_mercaderia(self, data: MercaderiaIn) -> MercaderiaOut:
        """Crea una mercadería y devuelve su representación de salida."""
        existente = self._dao.obtener_por_codigo_afip(data.codigo)
        if existente is not None:
            raise MercaderiaError(f"Ya existe una mercadería con código AFIP {data.codigo}")
        mercaderia = self._dao.crear(
            codigo=data.codigo,
            descripcion=data.descripcion,
            unidad_medida=data.unidad_medida,
            requiere_trazabilidad=data.requiere_trazabilidad,
            requiere_numero_tropa=data.requiere_numero_tropa,
        )
        return MercaderiaOut.model_validate(mercaderia)

    def obtener_por_codigo_afip(self, codigo: str) -> MercaderiaOut | None:
        """Busca una mercadería por su código AFIP."""
        mercaderia = self._dao.obtener_por_codigo_afip(codigo)
        return MercaderiaOut.model_validate(mercaderia) if mercaderia else None

    def listar(self) -> list[MercaderiaOut]:
        """Lista todas las mercaderías."""
        return [MercaderiaOut.model_validate(m) for m in self._dao.listar()]
