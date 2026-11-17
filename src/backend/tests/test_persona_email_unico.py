"""Tests de unicidad de ``personas.email``.

El email es un dato de la persona titular y debe ser único: una persona
tiene un solo email y un email no puede estar asignado a dos personas.
"""

from __future__ import annotations

import pytest

from configs.dao import SQLiteDAO
from core.persona.dao import PersonaDAO
from core.persona.schema import PersonaIn
from core.persona.servicio import PersonaError, PersonaService

# Importar el módulo de domicilio registra la tabla ``domicilios`` en
# ``Base.metadata`` (la FK ``personas.domicilio_id`` la necesita).
from modulos.registro_operadores.domicilio.dao import Domicilio  # noqa: F401


@pytest.fixture
def persona_service():
    """PersonaService sobre una BD SQLite en memoria."""
    dao = SQLiteDAO("sqlite://")
    dao.crear_tablas()
    return PersonaService(PersonaDAO(dao.obtener_sesion))


def _persona(email: str | None = None, identificador: str = "30111111111") -> PersonaIn:
    return PersonaIn(
        tipo="PJ",
        tipo_documento="CUIT",
        identificador=identificador,
        nombre="FRIGORIFICO TEST S.A.",
        email=email,
    )


class TestEmailUnico:
    def test_crear_persona_con_email(self, persona_service):
        out = persona_service.crear_persona(_persona(email="a@ejemplo.com"))
        assert out.email == "a@ejemplo.com"

    def test_crear_persona_email_duplicado_lanza_error(self, persona_service):
        persona_service.crear_persona(_persona(email="a@ejemplo.com", identificador="30111111111"))
        with pytest.raises(PersonaError) as exc:
            persona_service.crear_persona(_persona(email="a@ejemplo.com", identificador="30222222222"))
        assert "ya está asociado a otra persona" in str(exc.value)

    def test_actualizar_email_a_otra_persona_lanza_error(self, persona_service):
        p1 = persona_service.crear_persona(_persona(email="a@ejemplo.com", identificador="30111111111"))
        p2 = persona_service.crear_persona(_persona(identificador="30222222222"))
        with pytest.raises(PersonaError) as exc:
            persona_service.actualizar_email(p2.id, "a@ejemplo.com")
        assert "ya está asociado a otra persona" in str(exc.value)

    def test_actualizar_email_idempotente_misma_persona(self, persona_service):
        p1 = persona_service.crear_persona(_persona(email="a@ejemplo.com"))
        # Reasignar el mismo email a la misma persona no es error.
        out = persona_service.actualizar_email(p1.id, "a@ejemplo.com")
        assert out.email == "a@ejemplo.com"

    def test_actualizar_email_libre_funciona(self, persona_service):
        p1 = persona_service.crear_persona(_persona(email="a@ejemplo.com"))
        out = persona_service.actualizar_email(p1.id, "nuevo@ejemplo.com")
        assert out.email == "nuevo@ejemplo.com"

    def test_email_null_no_choca(self, persona_service):
        # Múltiples personas sin email no violan la unicidad.
        persona_service.crear_persona(_persona(identificador="30111111111"))
        persona_service.crear_persona(_persona(identificador="30222222222"))
        assert len(persona_service.listar()) == 2
