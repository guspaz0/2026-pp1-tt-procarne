"""Lógica de negocio de ``Inscripcion``."""

from __future__ import annotations

from datetime import datetime, timezone

from modulos.registro_operadores.inscripcion.dao import InscripcionDAO
from modulos.registro_operadores.inscripcion.dto import InscripcionIn, InscripcionOut


class InscripcionService:
    """Servicio de negocio de inscripciones de un operador."""

    def __init__(self, dao: InscripcionDAO) -> None:
        self._dao = dao

    def agregar(self, operador_id: int, data: InscripcionIn) -> InscripcionOut:
        """Agrega una inscripción a un operador."""
        inscripcion = self._dao.crear(
            operador_id=operador_id,
            tipo=data.tipo,
            fecha_inscripcion=datetime.now(timezone.utc),
            numero_inscripcion=data.numero_inscripcion,
        )
        return InscripcionOut.model_validate(inscripcion)

    def listar(self, operador_id: int) -> list[InscripcionOut]:
        """Lista las inscripciones de un operador."""
        inscripciones = self._dao.listar_por_operador(operador_id)
        return [InscripcionOut.model_validate(i) for i in inscripciones]
