"""Fixtures del Módulo I — Registro Provincial de Operadores.

El modelo ``Operador`` exige ``persona_id`` y ``categoria_id`` NOT NULL,
por lo que toda creación de operador en tests debe:

1. Crear (o reutilizar) la persona titular (``personas``).
2. Crear (o reutilizar) la categoría (``categorias``).
3. Crear el operador con ambos ids.

Los helpers :func:`seed_persona` / :func:`seed_categoria` /
:func:`crear_operador_test` encapsulan ese seed y se reutilizan en
todos los tests del módulo.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

# Reutilizar fixtures de configuración compartidas
from tests.fixtures import db_engine, db_session_factory, db_dao  # noqa: F401

# Importar los modelos del módulo (y la tabla personas, FK NOT NULL de
# operadores) para que Base.metadata los conozca al crear las tablas.
from core.persona.dao import Persona  # noqa: F401
from core.persona.servicio import PersonaService  # noqa: F401
from modulos.registro_operadores.asociaciones import (  # noqa: F401  (tablas N:M)
    CertificadoActividad,
    OperadorActividad,
)
from modulos.registro_operadores.adjunto.dao import Adjunto  # noqa: F401
from modulos.registro_operadores.categoria.dao import Categoria  # noqa: F401
from modulos.registro_operadores.domicilio.dao import Domicilio  # noqa: F401
from modulos.registro_operadores.operador.dao import Operador  # noqa: F401
from modulos.registro_operadores.requisito.dao import Requisito  # noqa: F401


# ---------------------------------------------------------------------------
# Helpers de seed (reutilizables desde los test_*.py del módulo)
# ---------------------------------------------------------------------------

def seed_persona(session, cuit: str, razon_social: str) -> Persona:
    """Crea (o reutiliza) la persona jurídica titular por CUIT."""
    persona = (
        session.query(Persona)
        .filter(Persona.tipo_documento == "CUIT", Persona.identificador == cuit)
        .first()
    )
    if persona is None:
        persona = Persona(
            tipo="PJ",
            tipo_documento="CUIT",
            identificador=cuit,
            nombre=razon_social,
        )
        session.add(persona)
        session.flush()
    return persona


def seed_categoria(session, nombre: str) -> Categoria:
    """Crea (o reutiliza) una categoría del registro."""
    categoria = session.query(Categoria).filter_by(nombre=nombre).first()
    if categoria is None:
        categoria = Categoria(nombre=nombre)
        session.add(categoria)
        session.flush()
    return categoria


def crear_operador_test(
    session,
    cuit: str,
    razon_social: str,
    tipo: str = "FRIGORIFICO",
    categoria: str | None = "SALA_DE_DESPOSTE",
    estado_registral: str = "PENDIENTE",
) -> Operador:
    """Crea un operador con su persona y categoría, y lo devuelve (ORM)."""
    persona = seed_persona(session, cuit, razon_social)
    cat = seed_categoria(session, categoria) if categoria else None
    op = Operador(
        persona_id=persona.id,
        categoria_id=cat.id if cat else None,
        razon_social=razon_social,
        tipo=tipo,
        estado_registral=estado_registral,
        alta_fecha=datetime.now(timezone.utc),
    )
    session.add(op)
    session.flush()
    return op


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def session_factory(db_session_factory):
    """Alias de :func:`db_session_factory` para compatibilidad."""
    return db_session_factory


@pytest.fixture()
def persona_service(db_session_factory):
    """PersonaService sobre la BD en memoria (para resolver la persona titular)."""
    from core.persona.dao import PersonaDAO

    return PersonaService(PersonaDAO(db_session_factory))


@pytest.fixture()
def operador_service(db_session_factory, persona_service):
    """OperadorService completo (operador + requisitos + certificado + catálogo)."""
    from modulos.registro_operadores.actividad_economica.dao import CatalogoActividadesDAO
    from modulos.registro_operadores.certificado.dao import CertificadoDAO
    from modulos.registro_operadores.certificado.servicio import CertificadoService
    from modulos.registro_operadores.operador.dao import OperadorDAO
    from modulos.registro_operadores.operador.servicio import OperadorService
    from modulos.registro_operadores.requisito_inscripcion.dao import RequisitoInscripcionDAO
    from modulos.registro_operadores.requisito_inscripcion.servicio import (
        RequisitoInscripcionService,
    )

    return OperadorService(
        OperadorDAO(db_session_factory),
        persona_service=persona_service,
        requisito_service=RequisitoInscripcionService(RequisitoInscripcionDAO(db_session_factory)),
        certificado_service=CertificadoService(CertificadoDAO(db_session_factory)),
        catalogo_actividades_dao=CatalogoActividadesDAO(db_session_factory),
    )
