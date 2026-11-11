"""Entidad de dominio: Operador de la cadena cárnica.

Representa a un operador (productor, frigorífico, carnicería, etc.)
y sus roles en un remito (titular, transportista, destinatario).
"""

from __future__ import annotations

from modulos.remitos_carnicos.base import Entidad


class RemitoOperador(Entidad):
    """Operador de la cadena cárnica (entidad de dominio de remitos).

    Campos:
        persona_id: referencia a la persona (física o jurídica).
        cuit: CUIT del operador.
        razon_social: razón social.
        tipo: tipo de operador (PRODUCTOR, FRIGORIFICO, etc.).
    """

    def __init__(
        self,
        persona_id: int,
        cuit: str | None = None,
        razon_social: str | None = None,
        tipo: str | None = None,
    ) -> None:
        super().__init__()
        self.persona_id = persona_id
        self.cuit = cuit
        self.razon_social = razon_social
        self.tipo = tipo

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "persona_id": self.persona_id,
            "cuit": self.cuit,
            "razon_social": self.razon_social,
            "tipo": self.tipo,
        }


class ParticipanteRemito(Entidad):
    """Participante en un remito (rol abstracto)."""

    def __init__(self, operador_id: int) -> None:
        super().__init__()
        self.operador_id = operador_id

    def to_dict(self) -> dict:
        return {"id": self.id, "operador_id": self.operador_id}


class Titular(ParticipanteRemito):
    """Titular del remito (emisor)."""


class Transportista(ParticipanteRemito):
    """Transportista del remito."""


class Destinatario(ParticipanteRemito):
    """Destinatario del remito."""


class Depositario(ParticipanteRemito):
    """Depositario del remito."""
