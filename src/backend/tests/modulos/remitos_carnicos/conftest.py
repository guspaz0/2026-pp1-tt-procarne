# """Fixtures comunes para los tests de ROCCA.

# Crea una base de datos SQLite en memoria para cada test,
# de modo que no se afecte la BD de desarrollo.

# Las fixtures de configuración de BD se reutilizan desde
# :mod:`tests.fixtures`.
# """

# from __future__ import annotations

# import pytest

# # Reutilizar fixtures de configuración compartidas
# from tests.fixtures import db_engine, db_session_factory, db_dao  # noqa: F401

# # Importar todos los modelos para que Base.metadata los conozca
# from core.persona.dao import Persona
# from core.mercaderia.dao import Mercaderia, MercaderiaDAO
# from modulos.remitos_carnicos.operador.dao import OperadorORM, RemitoOperadorDAO
# from modulos.remitos_carnicos.operador.categoria import (
#     Actividad,
#     ActividadDAO,
#     CategoriaAfip,
#     CategoriaAfipDAO,
#     CategoriaOperador,
#     CategoriaOperadorDAO,
# )
# from modulos.remitos_carnicos.remito.dao import RemitoCarnico, RemitoCarnicoDAO


# # ---------------------------------------------------------------------------
# # Aliases para compatibilidad (engine / session_factory)
# # ---------------------------------------------------------------------------

# @pytest.fixture()
# def engine(db_engine):
#     """Alias de :func:`db_engine` para compatibilidad."""
#     return db_engine


# @pytest.fixture()
# def session_factory(db_session_factory):
#     """Alias de :func:`db_session_factory` para compatibilidad."""
#     return db_session_factory


# # ---------------------------------------------------------------------------
# # DAOs por entidad
# # ---------------------------------------------------------------------------

# @pytest.fixture()
# def operador_dao(session_factory):
#     """DAO de operadores."""
#     return RemitoOperadorDAO(session_factory)


# @pytest.fixture()
# def actividad_dao(session_factory):
#     """DAO de actividades."""
#     return ActividadDAO(session_factory)


# @pytest.fixture()
# def categoria_afip_dao(session_factory):
#     """DAO de categorías AFIP."""
#     return CategoriaAfipDAO(session_factory)


# @pytest.fixture()
# def categoria_operador_dao(session_factory):
#     """DAO de categorías de operador."""
#     return CategoriaOperadorDAO(session_factory)


# @pytest.fixture()
# def mercaderia_dao(session_factory):
#     """DAO de mercaderías."""
#     return MercaderiaDAO(session_factory)


# @pytest.fixture()
# def remito_dao(session_factory):
#     """DAO de remitos cárnicos."""
#     return RemitoCarnicoDAO(session_factory)


# # ---------------------------------------------------------------------------
# # Seeds
# # ---------------------------------------------------------------------------

# def _crear_persona_juridica(session, cuit: str, nombre: str) -> Persona:
#     """Crea una persona jurídica y la devuelve."""
#     persona = Persona(
#         tipo="JURIDICA",
#         tipo_documento="CUIT",
#         identificador=cuit,
#         nombre=nombre,
#     )
#     session.add(persona)
#     session.commit()
#     session.refresh(persona)
#     return persona


# def _crear_operador(session, persona_id: int, tipo: str = "FRIGORIFICO") -> OperadorORM:
#     """Crea un operador referenciando a una persona."""
#     op = OperadorORM(
#         persona_id=persona_id,
#         razon_social="Operador Test",
#         tipo=tipo,
#         estado_registral="ACTIVO",
#     )
#     session.add(op)
#     session.commit()
#     session.refresh(op)
#     return op


# def crear_operador_test(session, cuit: str, razon_social: str) -> Operador:
#     """Crea una persona jurídica y un operador asociado (helper para tests)."""
#     persona = _crear_persona_juridica(session, cuit, razon_social)
#     return _crear_operador(session, persona.id)


# def obtener_operador_id_por_cuit(session, cuit: str) -> int:
#     """Devuelve el id del operador con el CUIT dado."""
#     persona = (
#         session.query(Persona)
#         .filter_by(tipo_documento="CUIT", identificador=cuit)
#         .first()
#     )
#     if persona is None:
#         raise ValueError(f"No existe persona con CUIT {cuit}")
#     op = (
#         session.query(OperadorORM)
#         .filter_by(persona_id=persona.id)
#         .first()
#     )
#     if op is None:
#         raise ValueError(f"No existe operador para persona {persona.id}")
#     return op.id


# @pytest.fixture()
# def seed_operadores(session_factory):
#     """Crea tres operadores de prueba (titular, transportista, destinatario)."""
#     with session_factory() as session:
#         titular = crear_operador_test(session, "30111111111", "TITULAR S.A.")
#         transportista = crear_operador_test(session, "30222222222", "TRANSPORTES XYZ")
#         destinatario = crear_operador_test(session, "30333333333", "DESTINATARIO S.R.L.")
#     return {
#         "titular": "30111111111",
#         "transportista": "30222222222",
#         "destinatario": "30333333333",
#     }


# @pytest.fixture()
# def seed_mercaderias(session_factory):
#     """Crea mercaderías de prueba."""
#     with session_factory() as session:
#         m1 = Mercaderia(
#             codigo="1101",
#             descripcion="Media res con hueso",
#             requiere_trazabilidad=True,
#             requiere_numero_tropa=True,
#         )
#         m2 = Mercaderia(
#             codigo="2101",
#             descripcion="Asado a 10 costillas",
#             requiere_trazabilidad=True,
#             requiere_numero_tropa=False,
#         )
#         session.add_all([m1, m2])
#         session.commit()
#     return ["1101", "2101"]


# @pytest.fixture()
# def seed_categorias(session_factory):
#     """Crea actividades y categorías AFIP de prueba."""
#     with session_factory() as session:
#         actividad = Actividad(nombre="Bovino/Bubalino")
#         session.add(actividad)
#         session.commit()
#         session.refresh(actividad)

#         cat1 = CategoriaAfip(
#             actividad_id=actividad.id,
#             codigo="B1",
#             descripcion="Productor/criador",
#         )
#         cat2 = CategoriaAfip(
#             actividad_id=actividad.id,
#             codigo="B6",
#             descripcion="Establecimientos faenadores y/o frigorífico",
#         )
#         session.add_all([cat1, cat2])
#         session.commit()
#     return {"actividad_id": actividad.id, "B1": cat1.id, "B6": cat2.id}
