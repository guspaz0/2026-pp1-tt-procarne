"""Servicio de negocio del Módulo I — Registro Provincial de Operadores."""

from __future__ import annotations

from datetime import date
from typing import Optional

from modulos.genericos.persona.dao import Persona

from .dao import ROCCAOperador, ROCCAOperadorDAO
from .enums import EstadoRegistral, TipoOperador
from .schema import (
    DomicilioOperativoIn,
    HabilitacionIn,
    InscripcionIn,
    ROCCAOperadorIn,
    ROCCAOperadorOut,
)
from .dao import DomicilioOperativo, Habilitacion, Inscripcion


class ROCCAOperadorError(Exception):
    """Error de negocio del Registro Provincial de Operadores."""


class ROCCAOperadorService:
    """Caso de uso: registro provincial de operadores de la cadena cárnica."""

    def __init__(self, dao: ROCCAOperadorDAO) -> None:
        self._dao = dao

    # ------------------------------------------------------------------
    # Operaciones
    # ------------------------------------------------------------------

    def registrar(self, datos: ROCCAOperadorIn) -> ROCCAOperadorOut:
        """Registra un nuevo operador en el ROCCA."""
        existente = self._dao.obtener_por_cuit(datos.cuit)
        if existente is not None:
            raise ROCCAOperadorError(
                f"Operador ya inscripto en el ROCCA: CUIT {datos.cuit}"
            )

        persona = Persona(
            tipo="PJ",
            identificador=datos.cuit,
            nombre=datos.razon_social,
            cuit=datos.cuit,
            domicilio=datos.domicilio,
            telefono=datos.telefono,
            email=datos.email,
        )

        operador = ROCCAOperador(
            persona_id=0,  # se asigna al guardar
            tipo=datos.tipo.value,
            estado_registral=datos.estado_registral.value,
            fecha_inscripcion=date.today(),
            observaciones=datos.observaciones,
            habilitaciones=[self._crear_habilitacion(h) for h in datos.habilitaciones],
            inscripciones=[self._crear_inscripcion(i) for i in datos.inscripciones],
            domicilios=[self._crear_domicilio(d) for d in datos.domicilios],
        )

        guardado = self._dao.guardar(operador, persona)
        return ROCCAOperadorOut.from_orm(guardado)

    def obtener(self, cuit: str) -> ROCCAOperadorOut:
        operador = self._dao.obtener_por_cuit(cuit)
        if operador is None:
            raise ROCCAOperadorError(f"Operador no encontrado: CUIT {cuit}")
        return ROCCAOperadorOut.from_orm(operador)

    def listar(
        self,
        tipo: Optional[TipoOperador] = None,
        estado_registral: Optional[EstadoRegistral] = None,
        limite: int = 100,
        offset: int = 0,
    ) -> list[ROCCAOperadorOut]:
        operadores = self._dao.listar(
            tipo=tipo.value if tipo else None,
            estado_registral=estado_registral.value if estado_registral else None,
            limite=limite,
            offset=offset,
        )
        return [ROCCAOperadorOut.from_orm(o) for o in operadores]

    def cambiar_estado(self, cuit: str, nuevo_estado: EstadoRegistral) -> ROCCAOperadorOut:
        """Cambia el estado registral del operador (ACTIVO/SUSPENDIDO/BAJADO)."""
        operador = self._dao.obtener_por_cuit(cuit)
        if operador is None:
            raise ROCCAOperadorError(f"Operador no encontrado: CUIT {cuit}")
        operador.estado_registral = nuevo_estado.value
        actualizado = self._dao.actualizar(operador)
        return ROCCAOperadorOut.from_orm(actualizado)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _crear_habilitacion(h: HabilitacionIn) -> Habilitacion:
        return Habilitacion(
            tipo=h.tipo,
            numero=h.numero,
            autoridad=h.autoridad,
            fecha_emision=h.fecha_emision,
            fecha_vencimiento=h.fecha_vencimiento,
            estado=h.estado,
        )

    @staticmethod
    def _crear_inscripcion(i: InscripcionIn) -> Inscripcion:
        return Inscripcion(
            tipo=i.tipo.value,
            organismo=i.organismo,
            numero=i.numero,
            fecha_inscripcion=i.fecha_inscripcion,
            estado=i.estado,
        )

    @staticmethod
    def _crear_domicilio(d: DomicilioOperativoIn) -> DomicilioOperativo:
        return DomicilioOperativo(
            tipo=d.tipo.value,
            calle=d.calle,
            numero=d.numero,
            localidad=d.localidad,
            departamento=d.departamento,
            provincia=d.provincia,
            codigo_postal=d.codigo_postal,
            activo=d.activo,
        )
