"""Servicio de negocio del operador de la cadena cárnica."""

from __future__ import annotations

from modulos.remitos_carnicos.operador.dao import Operador, OperadorDAO
from modulos.remitos_carnicos.operador.schema import OperadorIn, OperadorOut


class OperadorError(Exception):
    """Error de negocio del servicio de operadores."""


class OperadorService:
    """Servicio de negocio de operadores de la cadena cárnica."""

    def __init__(self, dao: OperadorDAO) -> None:
        self._dao = dao

    def crear_operador(self, data: OperadorIn) -> OperadorOut:
        """Crea un operador y devuelve su representación de salida."""
        existente = self._dao.obtener_por_persona(data.persona_id)
        if existente is not None:
            raise OperadorError(
                f"Ya existe un operador para la persona {data.persona_id}"
            )
        operador = self._dao.crear(persona_id=data.persona_id)
        return OperadorOut.model_validate(operador)

    def obtener_por_id(self, operador_id: int) -> OperadorOut | None:
        """Busca un operador por su id."""
        operador = self._dao.obtener_por_id(operador_id)
        return OperadorOut.model_validate(operador) if operador else None

    def listar(self) -> list[OperadorOut]:
        """Lista todos los operadores."""
        return [OperadorOut.model_validate(op) for op in self._dao.listar()]
