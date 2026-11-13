"""Teste del workflow completo de adjuntos con imágenes dummy reales.

Usa las imágenes generadas por ``scripts/generar_adjuntos_dummy.py``
(regenera en tmp si no existen) y valida el ciclo de vida completo:

- Subir TODOS los adjuntos válidos de cada categoría de operador
  (generales + específicos según la matriz de la especificación).
- Listar y verificar cantidad/requisitos.
- Obtener URL de descarga.
- Rechazo de requisito ajeno a la categoría.
- Rechazo de content type / tamaño.
- Eliminación de adjuntos.
- Adjuntos de Persona (dni_frente, dni_dorso, cuit, iibb).

Storage: se usa un ``FakeStorage`` local que persiste los bytes en
``tmp_path`` (simula InsForge Storage sin red).
"""

from __future__ import annotations

import asyncio
import base64
import sys
from pathlib import Path

import pytest

from configs.dao import crear_dao
from core.persona.adjunto_dao import AdjuntoPersonaDAO
from core.persona.dao import Persona, PersonaDAO
from core.persona.servicio import PersonaError, PersonaService
from modulos.registro_operadores.adjunto_operador.dao import AdjuntoOperadorDAO
from modulos.registro_operadores.categoria.dao import Categoria, CategoriaDAO
from modulos.registro_operadores.operador.dao import Operador, OperadorDAO
from modulos.registro_operadores.enums import CategoriaOperador
from modulos.registro_operadores.errores import OperadorError
from modulos.registro_operadores.adjunto_operador.servicio import AdjuntoOperadorService
from modulos.registro_operadores.requisito_inscripcion.dao import RequisitoInscripcionDAO
from modulos.registro_operadores.requisito_inscripcion.servicio import (
    REQUISITOS_GENERALES,
    REQUISITOS_ESPECIFICOS_POR_CATEGORIA,
    RequisitoInscripcionService,
)

_SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(_SCRIPTS))
from generar_adjuntos_dummy import REQUISITOS_OPERADOR, REQUISITOS_PERSONA, generar_png  # noqa: E402

DUMMY_DIR = _SCRIPTS / "dummy_docs"


# ---------------------------------------------------------------------------
# Fake storage local (simula InsForge Storage)
# ---------------------------------------------------------------------------

class FakeStorage:
    """Storage in-mem/disk que implementa upload / download_url / delete."""

    def __init__(self, base: Path) -> None:
        self.base = base
        self.base.mkdir(parents=True, exist_ok=True)
        self._keys: list[str] = []

    async def upload(self, filename: str, content_type: str, size: int, data: bytes) -> str:
        key = f"test-{len(self._keys) + 1}-{filename}"
        self._keys.append(key)
        (self.base / key).write_bytes(data)
        return key

    async def download_url(self, key: str) -> str:
        return f"https://insforge.test/{key}"

    async def delete(self, key: str) -> None:
        p = self.base / key
        if p.exists():
            p.unlink()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def dummy_docs():
    """Garantiza que las imágenes dummy existen (genera en tmp si falta)."""
    if DUMMY_DIR.exists() and (DUMMY_DIR / "operador__afip_ultimo_pago.png").exists():
        return DUMMY_DIR
    tmp = DUMMY_DIR  # generar en el directorio estándar
    for cod in REQUISITOS_PERSONA:
        generar_png(tmp / f"persona__{cod}.png", "DUMMY", ["x"])
    for cod in REQUISITOS_OPERADOR:
        generar_png(tmp / f"operador__{cod}.png", "DUMMY", ["x"])
    return tmp


@pytest.fixture
def db():
    dao = crear_dao("sqlite:///:memory:")
    dao.crear_tablas()
    yield dao


@pytest.fixture
def storage(tmp_path):
    return FakeStorage(tmp_path / "storage")


@pytest.fixture
def persona_service(db, storage):
    return PersonaService(
        PersonaDAO(db.obtener_sesion),
        adjunto_dao=AdjuntoPersonaDAO(db.obtener_sesion),
        storage=storage,
    )


@pytest.fixture
def operador_service(db, storage):
    return AdjuntoOperadorService(
        AdjuntoOperadorDAO(db.obtener_sesion),
        storage=storage,
        operador_dao=OperadorDAO(db.obtener_sesion),
        requisito_service=RequisitoInscripcionService(RequisitoInscripcionDAO(db.obtener_sesion)),
    )


def _crear_persona(db, tipo="fisica", doc="12345678", nombre="JUAN PEREZ") -> int:
    with db.obtener_sesion() as s:
        p = Persona(tipo=tipo, tipo_documento="DNI" if tipo == "fisica" else "CUIT",
                    identificador=doc, nombre=nombre)
        s.add(p)
        s.commit()
        return p.id


def _crear_operador(db, persona_id: int, categoria: str) -> int:
    """Crea el operador con su persona y categoría (``operadores.categoria_id``
    es NOT NULL: se resuelve/crea la fila en ``categorias`` por nombre)."""
    cat_dao = CategoriaDAO(db.obtener_sesion)
    with db.obtener_sesion() as s:
        cat = s.query(Categoria).filter_by(nombre=categoria).first()
        if cat is None:
            cat = Categoria(nombre=categoria)
            s.add(cat)
            s.flush()
        op = Operador(persona_id=persona_id, razon_social=f"OP {categoria}", tipo="empresa",
                      categoria_id=cat.id, estado_registral="PENDIENTE")
        s.add(op)
        s.commit()
        return op.id


def _datos(dummy_dir: Path, prefijo: str, requisito: str):
    ruta = dummy_dir / f"{prefijo}__{requisito}.png"
    data = ruta.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", f"{ruta.name} no es un PNG válido"
    return data


# ---------------------------------------------------------------------------
# Workflow: persona
# ---------------------------------------------------------------------------

class TestWorkflowPersona:
    def test_subir_todos_adjuntos_persona(self, persona_service, db, dummy_docs):
        pid = _crear_persona(db)
        subidos = []
        for cod in REQUISITOS_PERSONA:
            data = _datos(dummy_docs, "persona", cod)
            out = asyncio.run(persona_service.subir_adjunto(
                persona_id=pid, requisito=cod,
                filename=f"{cod}.png", content_type="image/png",
                size=len(data), data=data,
            ))
            subidos.append(out["requisito"])
        assert sorted(subidos) == sorted(REQUISITOS_PERSONA)
        adjuntos = persona_service.listar_adjuntos(pid)
        assert len(adjuntos) == len(REQUISITOS_PERSONA)

    def test_requisito_invalido_persona(self, persona_service, db):
        pid = _crear_persona(db)
        with pytest.raises(PersonaError):
            asyncio.run(persona_service.subir_adjunto(
                persona_id=pid, requisito="libreta_sanitaria",
                filename="x.png", content_type="image/png", size=4, data=b"iVBK",
            ))


# ---------------------------------------------------------------------------
# Workflow: operador — cada categoría con todos sus requisitos reales
# ---------------------------------------------------------------------------

class TestWorkflowOperador:
    @pytest.mark.parametrize("categoria", [c.value for c in CategoriaOperador])
    def test_subir_todos_adjuntos_categoria(self, operador_service, db, dummy_docs, categoria):
        """Sube TODOS los adjuntos válidos de una categoría con imágenes reales."""
        pid = _crear_persona(db, tipo="juridica", doc=f"30-{hash(categoria) % 99999999:08d}",
                             nombre=f"EMP {categoria}")
        op_id = _crear_operador(db, pid, categoria)

        requisitos = REQUISITOS_GENERALES + REQUISITOS_ESPECIFICOS_POR_CATEGORIA.get(categoria, [])
        for req in requisitos:
            data = _datos(dummy_docs, "operador", req)
            out = asyncio.run(operador_service.subir(
                operador_id=op_id, requisito=req,
                filename=f"{req}.png", content_type="image/png",
                size=len(data), data=data,
            ))
            assert out.operador_id == op_id
            assert out.requisito == req
            assert out.size == len(data)
            assert out.content_type == "image/png"

        adjuntos = operador_service.listar(op_id)
        assert [a.requisito for a in adjuntos] == requisitos
        assert all(a.size > 1000 for a in adjuntos)  # PNGs reales, no stubs

    def test_obtener_url(self, operador_service, db, dummy_docs):
        pid = _crear_persona(db, tipo="juridica", doc="30-11111111-1")
        op_id = _crear_operador(db, pid, CategoriaOperador.CARNICERIAS.value)
        data = _datos(dummy_docs, "operador", "formulario_101")
        out = asyncio.run(operador_service.subir(
            operador_id=op_id, requisito="formulario_101",
            filename="formulario_101.png", content_type="image/png",
            size=len(data), data=data,
        ))
        url = asyncio.run(operador_service.obtener_url(op_id, out.id))
        assert url.startswith("https://insforge.test/")

    def test_eliminar_adjunto(self, operador_service, db, dummy_docs):
        pid = _crear_persona(db, tipo="juridica", doc="30-22222222-2")
        op_id = _crear_operador(db, pid, CategoriaOperador.CARNICERIAS.value)
        data = _datos(dummy_docs, "operador", "habilitacion_municipal")
        out = asyncio.run(operador_service.subir(
            operador_id=op_id, requisito="habilitacion_municipal",
            filename="hab.png", content_type="image/png", size=len(data), data=data,
        ))
        asyncio.run(operador_service.eliminar(op_id, out.id))
        assert operador_service.listar(op_id) == []

    def test_requisito_ajeno_a_categoria_rechazado(self, operador_service, db, dummy_docs):
        """plano_camara (Cámaras) no puede subirse a una Carnicería."""
        pid = _crear_persona(db, tipo="juridica", doc="30-33333333-3")
        op_id = _crear_operador(db, pid, CategoriaOperador.CARNICERIAS.value)
        data = _datos(dummy_docs, "operador", "plano_camara")
        with pytest.raises(OperadorError, match="no corresponde"):
            asyncio.run(operador_service.subir(
                operador_id=op_id, requisito="plano_camara",
                filename="plano.png", content_type="image/png", size=len(data), data=data,
            ))

    def test_content_type_rechazado(self, operador_service, db):
        pid = _crear_persona(db, tipo="juridica", doc="30-44444444-4")
        op_id = _crear_operador(db, pid, CategoriaOperador.CARNICERIAS.value)
        with pytest.raises(OperadorError, match="no permitido"):
            asyncio.run(operador_service.subir(
                operador_id=op_id, requisito="formulario_101",
                filename="f.exe", content_type="application/x-msdownload",
                size=4, data=b"MZxx",
            ))

    def test_tamano_excedido_rechazado(self, operador_service, db):
        pid = _crear_persona(db, tipo="juridica", doc="30-55555555-5")
        op_id = _crear_operador(db, pid, CategoriaOperador.CARNICERIAS.value)
        with pytest.raises(OperadorError, match="tamaño"):
            asyncio.run(operador_service.subir(
                operador_id=op_id, requisito="formulario_101",
                filename="f.png", content_type="image/png",
                size=11 * 1024 * 1024, data=b"x",
            ))

    def test_payload_api_base64(self, operador_service, db, dummy_docs):
        """Simula el body JSON de POST /{operador_id}/adjuntos (data_base64)."""
        pid = _crear_persona(db, tipo="juridica", doc="30-66666666-6")
        op_id = _crear_operador(db, pid, CategoriaOperador.SALA_DE_DESPOSTE.value)
        data = _datos(dummy_docs, "operador", "memoria_constructiva")
        body = {
            "requisito": "memoria_constructiva",
            "filename": "memoria_constructiva.png",
            "content_type": "image/png",
            "data_base64": base64.b64encode(data).decode(),
        }
        raw = base64.b64decode(body["data_base64"])
        out = asyncio.run(operador_service.subir(
            operador_id=op_id, requisito=body["requisito"], filename=body["filename"],
            content_type=body["content_type"], size=len(raw), data=raw,
        ))
        assert out.nombre_original == "memoria_constructiva.png"
