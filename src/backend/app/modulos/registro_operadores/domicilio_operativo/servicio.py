"""Lógica de negocio de ``DomicilioOperativo``."""

from __future__ import annotations

from modulos.registro_operadores.domicilio_operativo.dao import DomicilioOperativoDAO
from modulos.registro_operadores.domicilio_operativo.dto import (
    DomicilioOperativoIn,
    DomicilioOperativoOut,
)


class DomicilioOperativoService:
    """Servicio de negocio de domicilios operativos."""

    def __init__(self, dao: DomicilioOperativoDAO) -> None:
        self._dao = dao

    def agregar(self, operador_id: int, data: DomicilioOperativoIn) -> DomicilioOperativoOut:
        """Agrega un domicilio operativo a un operador."""
        domicilio = self._dao.crear(
            operador_id=operador_id,
            direccion=data.direccion,
            localidad=data.localidad,
            provincia=data.provincia,
            codigo_postal=data.codigo_postal,
            es_principal=data.es_principal,
        )
        return DomicilioOperativoOut.model_validate(domicilio)

    def listar(self, operador_id: int) -> list[DomicilioOperativoOut]:
        """Lista los domicilios operativos de un operador."""
        domicilios = self._dao.listar_por_operador(operador_id)
        return [DomicilioOperativoOut.model_validate(d) for d in domicilios]
