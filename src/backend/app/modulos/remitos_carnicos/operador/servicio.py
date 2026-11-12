# """Servicio de negocio del operador de la cadena cárnica."""

# from __future__ import annotations

# from modulos.remitos_carnicos.operador.dao import OperadorORM, RemitoOperadorDAO
# from modulos.remitos_carnicos.operador.schema import RemitoOperadorIn, RemitoOperadorOut


# class RemitoOperadorError(Exception):
#     """Error de negocio del servicio de operadores de remitos."""


# class RemitoOperadorService:
#     """Servicio de negocio de operadores de la cadena cárnica."""

#     def __init__(self, dao: RemitoOperadorDAO) -> None:
#         self._dao = dao

#     def crear_operador(self, data: RemitoOperadorIn) -> RemitoOperadorOut:
#         """Crea un operador y devuelve su representación de salida."""
#         existentes = self._dao.obtener_por_persona(data.persona_id)
#         if existentes:
#             raise RemitoOperadorError(
#                 f"Ya existe un operador para la persona {data.persona_id}"
#             )
#         operador = self._dao.crear(persona_id=data.persona_id)
#         return RemitoOperadorOut.model_validate(operador)

#     def obtener_por_id(self, operador_id: int) -> RemitoOperadorOut | None:
#         """Busca un operador por su id."""
#         operador = self._dao.obtener_por_id(operador_id)
#         return RemitoOperadorOut.model_validate(operador) if operador else None

#     def listar(self) -> list[RemitoOperadorOut]:
#         """Lista todos los operadores."""
#         return [RemitoOperadorOut.model_validate(op) for op in self._dao.listar()]
