"""DAO del operador de la cadena cárnica.

Ahora usa el modelo unificado ``ROCCAOperador`` (tabla ``operadores``)
del módulo de registro de operadores.
"""

from __future__ import annotations

from typing import Optional

from modulos.registro_operadores.dao import ROCCAOperador, ROCCAOperadorDAO


# Alias para compatibilidad con código existente
Operador = ROCCAOperador


class OperadorDAO:
    """DAO de operadores (compatibilidad con módulo de remitos).

    Delega en el ``ROCCAOperadorDAO`` del módulo de registro.
    """

    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory
        self._dao = ROCCAOperadorDAO(session_factory)

    def crear(self, persona_id: int, cuit: str | None = None,
              razon_social: str | None = None, tipo: str | None = None) -> ROCCAOperador:
        """Crea y persiste un operador nuevo."""
        return self._dao.crear(
            cuit=cuit or f"00000000000",
            razon_social=razon_social or f"Operador {persona_id}",
            tipo=tipo or "COMERCIALIZADOR",
            persona_id=persona_id,
        )

    def obtener_por_id(self, operador_id: int) -> ROCCAOperador | None:
        """Devuelve el operador con el id dado, o ``None``."""
        return self._dao.obtener_por_id(operador_id)

    def obtener_por_persona(self, persona_id: int) -> list[ROCCAOperador]:
        """Devuelve los operadores asociados a una persona."""
        with self._session_factory() as session:
            return (
                session.query(ROCCAOperador)
                .filter_by(persona_id=persona_id)
                .all()
            )

    def listar(self) -> list[ROCCAOperador]:
        """Devuelve todos los operadores."""
        return self._dao.listar()
