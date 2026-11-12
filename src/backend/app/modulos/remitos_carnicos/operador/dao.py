# """DAO del operador de la cadena cárnica.

# Usa el modelo unificado ``Operador`` (tabla ``operadores``)
# del módulo de registro de operadores.
# """

# from __future__ import annotations

# from typing import Optional

# from modulos.registro_operadores.dao import Operador, OperadorDAO as RegistroOperadorDAO


# # Alias para compatibilidad con código existente (ORM unificado)
# OperadorORM = Operador


# class RemitoOperadorDAO:
#     """DAO de operadores (compatibilidad con módulo de remitos).

#     Delega en el ``OperadorDAO`` del módulo de registro.
#     """

#     def __init__(self, session_factory) -> None:
#         self._session_factory = session_factory
#         self._dao = RegistroOperadorDAO(session_factory)

#     def crear(self, persona_id: int, cuit: str | None = None,
#               razon_social: str | None = None, tipo: str | None = None) -> Operador:
#         """Crea y persiste un operador nuevo.

#         El CUIT no se guarda en ``operadores``: se infiere de la persona
#         titular vía ``persona_id``.
#         """
#         return self._dao.crear(
#             razon_social=razon_social or f"Operador {persona_id}",
#             tipo=tipo or "COMERCIALIZADOR",
#             persona_id=persona_id,
#         )

#     def obtener_por_id(self, operador_id: int) -> Operador | None:
#         """Devuelve el operador con el id dado, o ``None``."""
#         return self._dao.obtener_por_id(operador_id)

#     def obtener_por_persona(self, persona_id: int) -> list[Operador]:
#         """Devuelve los operadores asociados a una persona."""
#         with self._session_factory() as session:
#             return (
#                 session.query(Operador)
#                 .filter_by(persona_id=persona_id)
#                 .all()
#             )

#     def listar(self) -> list[Operador]:
#         """Devuelve todos los operadores."""
#         return self._dao.listar()
