"""Lógica de negocio de ``Habilitacion``."""

from __future__ import annotations

from datetime import datetime, timezone

from modulos.registro_operadores.habilitacion.dao import HabilitacionDAO
from modulos.registro_operadores.habilitacion.dto import HabilitacionIn, HabilitacionOut
from modulos.registro_operadores.operador.servicio import OperadorError


class HabilitacionService:
    """Servicio de negocio de habilitaciones de un operador."""

    def __init__(self, dao: HabilitacionDAO) -> None:
        self._dao = dao

    def agregar(self, operador_id: int, data: HabilitacionIn) -> HabilitacionOut:
        """Agrega una habilitación a un operador."""
        habilitacion = self._dao.crear(
            operador_id=operador_id,
            actividad=data.actividad,
            fecha_habilitacion=datetime.now(timezone.utc),
            fecha_vencimiento=data.fecha_vencimiento,
        )
        return HabilitacionOut.model_validate(habilitacion)

    def listar(self, operador_id: int) -> list[HabilitacionOut]:
        """Lista las habilitaciones de un operador."""
        habilitaciones = self._dao.listar_por_operador(operador_id)
        return [HabilitacionOut.model_validate(h) for h in habilitaciones]
