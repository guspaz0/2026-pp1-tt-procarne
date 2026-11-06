"""Servicio de negocio del Módulo I — Registro Provincial de Operadores.

Casos de uso:
- Dar de alta un operador.
- Buscar por CUIT.
- Listar operadores (con filtros).
- Cambiar el estado registral.
- Agregar habilitaciones, inscripciones y domicilios operativos.
- Gestionar requisitos de inscripción (generales y específicos por categoría).
"""

from __future__ import annotations

from datetime import datetime, timezone

from modulos.registro_operadores.dao import (
    DomicilioOperativo,
    Habilitacion,
    Inscripcion,
    RequisitoInscripcion,
    ROCCAOperador,
    ROCCAOperadorDAO,
)
from modulos.registro_operadores.enums import (
    CategoriaOperador,
    EstadoRegistral,
    RequisitoEspecifico,
    RequisitoGeneral,
)
from modulos.registro_operadores.schema import (
    DomicilioOperativoIn,
    DomicilioOperativoOut,
    HabilitacionIn,
    HabilitacionOut,
    InscripcionIn,
    InscripcionOut,
    RequisitoInscripcionIn,
    RequisitoInscripcionOut,
    ROCCAOperadorIn,
    ROCCAOperadorOut,
)


class ROCCAOperadorError(Exception):
    """Error de negocio del servicio de operadores."""


# ---------------------------------------------------------------------------
# Matriz de requisitos específicos por categoría (según especificación)
# ---------------------------------------------------------------------------

REQUISITOS_ESPECIFICOS_POR_CATEGORIA: dict[str, list[str]] = {
    CategoriaOperador.SALA_DE_DESPOSTE.value: [
        RequisitoEspecifico.REGISTRO_NACIONAL_FRIGORIFICOS.value,
    ],
    CategoriaOperador.CAMARAS_FRIGORIFICAS.value: [
        RequisitoEspecifico.REGISTRO_NACIONAL_CAMARAS.value,
    ],
    CategoriaOperador.FABRICA_DE_CHACINADOS.value: [
        RequisitoEspecifico.REGISTRO_NACIONAL_CHACINADOS.value,
    ],
    CategoriaOperador.CARNICERIAS.value: [
        RequisitoEspecifico.MATRICULA_MUNICIPAL_CARNICERIA.value,
    ],
    CategoriaOperador.TRANSPONEDOR.value: [
        RequisitoEspecifico.REGISTRO_NACIONAL_TRANSPORTE.value,
    ],
    CategoriaOperador.SUPERMERCADO.value: [
        RequisitoEspecifico.MATRICULA_MUNICIPAL_SUPERMERCADO.value,
    ],
    CategoriaOperador.DISTRIBUIDOR.value: [
        RequisitoEspecifico.REGISTRO_NACIONAL_DISTRIBUIDOR.value,
    ],
}

REQUISITOS_GENERALES: list[str] = [
    RequisitoGeneral.INGRESOS_BRUTOS.value,
    RequisitoGeneral.AFIP.value,
    RequisitoGeneral.REGIMEN_PROVISIONAL.value,
]


class ROCCAOperadorService:
    """Servicio de negocio de operadores de la cadena cárnica."""

    def __init__(self, dao: ROCCAOperadorDAO) -> None:
        self._dao = dao

    # ------------------------------------------------------------------
    # Operadores
    # ------------------------------------------------------------------

    def crear_operador(self, data: ROCCAOperadorIn) -> ROCCAOperadorOut:
        """Da de alta un operador y devuelve su representación de salida."""
        existente = self._dao.obtener_por_cuit(data.cuit)
        if existente is not None:
            raise ROCCAOperadorError(f"Ya existe un operador con CUIT {data.cuit}")

        # Validar categoría si se proporciona
        if data.categoria is not None:
            categorias_validas = [c.value for c in CategoriaOperador]
            if data.categoria not in categorias_validas:
                raise ROCCAOperadorError(
                    f"Categoría inválida: {data.categoria}. "
                    f"Categorías válidas: {', '.join(categorias_validas)}"
                )

        operador = self._dao.crear(
            cuit=data.cuit,
            razon_social=data.razon_social,
            tipo=data.tipo,
            domicilio=data.domicilio,
            domicilio_fiscal=data.domicilio_fiscal,
            telefono=data.telefono,
            email=data.email,
            categoria=data.categoria,
        )

        # Crear los requisitos (generales + específicos) con estado "no cumplido"
        self._crear_requisitos_iniciales(operador.id, data.categoria)

        return ROCCAOperadorOut.model_validate(operador)

    def obtener_por_cuit(self, cuit: str) -> ROCCAOperadorOut | None:
        """Busca un operador por su CUIT."""
        operador = self._dao.obtener_por_cuit(cuit)
        return ROCCAOperadorOut.model_validate(operador) if operador else None

    def listar(self, tipo: str | None = None,
               estado_registral: str | None = None,
               categoria: str | None = None) -> list[ROCCAOperadorOut]:
        """Lista operadores, opcionalmente filtrados por tipo, estado y categoría."""
        operadores = self._dao.listar(tipo=tipo, estado_registral=estado_registral, categoria=categoria)
        return [ROCCAOperadorOut.model_validate(op) for op in operadores]

    def cambiar_estado(self, operador_id: int, estado: EstadoRegistral) -> ROCCAOperadorOut:
        """Cambia el estado registral de un operador."""
        operador = self._dao.actualizar_estado(operador_id, estado)
        if operador is None:
            raise ROCCAOperadorError(f"No existe un operador con id {operador_id}")
        return ROCCAOperadorOut.model_validate(operador)

    # ------------------------------------------------------------------
    # Habilitaciones
    # ------------------------------------------------------------------

    def agregar_habilitacion(self, operador_id: int, data: HabilitacionIn) -> HabilitacionOut:
        """Agrega una habilitación a un operador."""
        with self._dao._session_factory() as session:
            operador = session.get(ROCCAOperador, operador_id)
            if operador is None:
                raise ROCCAOperadorError(f"No existe un operador con id {operador_id}")
            habilitacion = Habilitacion(
                operador_id=operador_id,
                actividad=data.actividad,
                fecha_habilitacion=datetime.now(timezone.utc),
                fecha_vencimiento=data.fecha_vencimiento,
            )
            session.add(habilitacion)
            session.commit()
            session.refresh(habilitacion)
            return HabilitacionOut.model_validate(habilitacion)

    def listar_habilitaciones(self, operador_id: int) -> list[HabilitacionOut]:
        """Lista las habilitaciones de un operador."""
        with self._dao._session_factory() as session:
            habilitaciones = (
                session.query(Habilitacion)
                .filter_by(operador_id=operador_id)
                .all()
            )
            return [HabilitacionOut.model_validate(h) for h in habilitaciones]

    # ------------------------------------------------------------------
    # Inscripciones
    # ------------------------------------------------------------------

    def agregar_inscripcion(self, operador_id: int, data: InscripcionIn) -> InscripcionOut:
        """Agrega una inscripción a un operador."""
        with self._dao._session_factory() as session:
            operador = session.get(ROCCAOperador, operador_id)
            if operador is None:
                raise ROCCAOperadorError(f"No existe un operador con id {operador_id}")
            inscripcion = Inscripcion(
                operador_id=operador_id,
                tipo=data.tipo,
                fecha_inscripcion=datetime.now(timezone.utc),
                numero_inscripcion=data.numero_inscripcion,
            )
            session.add(inscripcion)
            session.commit()
            session.refresh(inscripcion)
            return InscripcionOut.model_validate(inscripcion)

    def listar_inscripciones(self, operador_id: int) -> list[InscripcionOut]:
        """Lista las inscripciones de un operador."""
        with self._dao._session_factory() as session:
            inscripciones = (
                session.query(Inscripcion)
                .filter_by(operador_id=operador_id)
                .all()
            )
            return [InscripcionOut.model_validate(i) for i in inscripciones]

    # ------------------------------------------------------------------
    # Domicilios operativos
    # ------------------------------------------------------------------

    def agregar_domicilio_operativo(self, operador_id: int, data: DomicilioOperativoIn) -> DomicilioOperativoOut:
        """Agrega un domicilio operativo a un operador."""
        with self._dao._session_factory() as session:
            operador = session.get(ROCCAOperador, operador_id)
            if operador is None:
                raise ROCCAOperadorError(f"No existe un operador con id {operador_id}")
            domicilio = DomicilioOperativo(
                operador_id=operador_id,
                direccion=data.direccion,
                localidad=data.localidad,
                provincia=data.provincia,
                codigo_postal=data.codigo_postal,
                es_principal=data.es_principal,
            )
            session.add(domicilio)
            session.commit()
            session.refresh(domicilio)
            return DomicilioOperativoOut.model_validate(domicilio)

    def listar_domicilios_operativos(self, operador_id: int) -> list[DomicilioOperativoOut]:
        """Lista los domicilios operativos de un operador."""
        with self._dao._session_factory() as session:
            domicilios = (
                session.query(DomicilioOperativo)
                .filter_by(operador_id=operador_id)
                .all()
            )
            return [DomicilioOperativoOut.model_validate(d) for d in domicilios]

    # ------------------------------------------------------------------
    # Requisitos de inscripción
    # ------------------------------------------------------------------

    def listar_requisitos(self, operador_id: int) -> list[RequisitoInscripcionOut]:
        """Lista los requisitos de inscripción de un operador."""
        requisitos = self._dao.listar_requisitos(operador_id)
        return [RequisitoInscripcionOut.model_validate(r) for r in requisitos]

    def actualizar_requisito(self, operador_id: int, requisito_id: int,
                             cumplido: bool, observaciones: str | None = None) -> RequisitoInscripcionOut:
        """Actualiza el estado de cumplimiento de un requisito."""
        with self._dao._session_factory() as session:
            requisito = session.get(RequisitoInscripcion, requisito_id)
            if requisito is None or requisito.operador_id != operador_id:
                raise ROCCAOperadorError(f"No existe el requisito {requisito_id} para el operador {operador_id}")
            requisito.cumplido = cumplido
            if observaciones is not None:
                requisito.observaciones = observaciones
            if cumplido:
                requisito.fecha_cumplimiento = datetime.now(timezone.utc)
            else:
                requisito.fecha_cumplimiento = None
            session.commit()
            session.refresh(requisito)
            return RequisitoInscripcionOut.model_validate(requisito)

    def obtener_requisitos_pendientes(self, operador_id: int) -> list[RequisitoInscripcionOut]:
        """Lista los requisitos aún no cumplidos de un operador."""
        requisitos = self._dao.listar_requisitos(operador_id)
        pendientes = [r for r in requisitos if not r.cumplido]
        return [RequisitoInscripcionOut.model_validate(r) for r in pendientes]

    def obtener_requisitos_especificos_por_categoria(self, categoria: str) -> list[str]:
        """Devuelve los códigos de requisitos específicos para una categoría."""
        return REQUISITOS_ESPECIFICOS_POR_CATEGORIA.get(categoria, [])

    # ------------------------------------------------------------------
    # Internos
    # ------------------------------------------------------------------

    def _crear_requisitos_iniciales(self, operador_id: int, categoria: str | None) -> None:
        """Crea los requisitos iniciales (generales + específicos) para un operador."""
        with self._dao._session_factory() as session:
            # Requisitos generales (comunes a todas las categorías)
            for codigo in REQUISITOS_GENERALES:
                req = RequisitoInscripcion(
                    operador_id=operador_id,
                    codigo=codigo,
                    descripcion=codigo.replace("_", " ").title(),
                    es_general=True,
                    cumplido=False,
                )
                session.add(req)

            # Requisitos específicos según categoría
            if categoria is not None:
                for codigo in REQUISITOS_ESPECIFICOS_POR_CATEGORIA.get(categoria, []):
                    req = RequisitoInscripcion(
                        operador_id=operador_id,
                        codigo=codigo,
                        descripcion=codigo.replace("_", " ").title(),
                        es_general=False,
                        cumplido=False,
                    )
                    session.add(req)

            session.commit()
