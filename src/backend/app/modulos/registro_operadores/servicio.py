"""Servicio de negocio del Módulo I — Registro Provincial de Operadores.

Casos de uso:
- Dar de alta un operador.
- Buscar por CUIT.
- Listar operadores (con filtros).
- Cambiar el estado registral.
- Agregar habilitaciones, inscripciones y domicilios operativos.
"""

from __future__ import annotations

from datetime import datetime, timezone

from modulos.registro_operadores.dao import (
    DomicilioOperativo,
    Habilitacion,
    Inscripcion,
    ROCCAOperador,
    ROCCAOperadorDAO,
)
from modulos.registro_operadores.enums import EstadoRegistral
from modulos.registro_operadores.schema import (
    DomicilioOperativoIn,
    DomicilioOperativoOut,
    HabilitacionIn,
    HabilitacionOut,
    InscripcionIn,
    InscripcionOut,
    ROCCAOperadorIn,
    ROCCAOperadorOut,
)


class ROCCAOperadorError(Exception):
    """Error de negocio del servicio de operadores."""


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
        operador = self._dao.crear(
            cuit=data.cuit,
            razon_social=data.razon_social,
            tipo=data.tipo,
            domicilio=data.domicilio,
            domicilio_fiscal=data.domicilio_fiscal,
            telefono=data.telefono,
            email=data.email,
        )
        return ROCCAOperadorOut.model_validate(operador)

    def obtener_por_cuit(self, cuit: str) -> ROCCAOperadorOut | None:
        """Busca un operador por su CUIT."""
        operador = self._dao.obtener_por_cuit(cuit)
        return ROCCAOperadorOut.model_validate(operador) if operador else None

    def listar(self, tipo: str | None = None,
               estado_registral: str | None = None) -> list[ROCCAOperadorOut]:
        """Lista operadores, opcionalmente filtrados por tipo y estado."""
        operadores = self._dao.listar(tipo=tipo, estado_registral=estado_registral)
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
