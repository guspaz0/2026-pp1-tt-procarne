"""Controlador (router API) del Módulo I — Registro Provincial de Operadores."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

from modulos.registro_operadores.enums import EstadoRegistral
from modulos.registro_operadores.schema import (
    ActividadEconomicaOut,
    CertificadoIn,
    CertificadoOut,
    CertificadoSuspenderIn,
    DomicilioOperativoIn,
    DomicilioOperativoOut,
    GrupoActividadOut,
    HabilitacionIn,
    HabilitacionOut,
    InscripcionIn,
    InscripcionOut,
    RequisitoInscripcionOut,
    ROCCAOperadorIn,
    ROCCAOperadorOut,
    SubgrupoActividadOut,
)
from modulos.registro_operadores.servicio import (
    REQUISITOS_ESPECIFICOS_POR_CATEGORIA,
    REQUISITOS_GENERALES,
    ROCCAOperadorError,
    ROCCAOperadorService,
)


def crear_router(servicio: ROCCAOperadorService) -> APIRouter:
    """Crea el router API del módulo de registro de operadores."""
    router = APIRouter(prefix="/api/registro-operadores", tags=["Registro de Operadores"])

    # ------------------------------------------------------------------
    # Catálogo de requisitos (referencia) — debe ir antes de /{operador_id}
    # ------------------------------------------------------------------

    @router.get("/catalogo/requisitos")
    def catalogo_requisitos():
        """Devuelve el catálogo de requisitos generales y específicos por categoría."""
        return {
            "generales": REQUISITOS_GENERALES,
            "especificos_por_categoria": REQUISITOS_ESPECIFICOS_POR_CATEGORIA,
        }

    @router.get("/catalogo/actividades/grupos", response_model=list[GrupoActividadOut])
    def catalogo_grupos():
        """Lista los grupos de actividades económicas (A, B, C, ...)."""
        return servicio.listar_grupos()

    @router.get("/catalogo/actividades/subgrupos", response_model=list[SubgrupoActividadOut])
    def catalogo_subgrupos(grupo: str | None = Query(None, description="Filtrar por grupo")):
        """Lista los subgrupos de actividades económicas."""
        return servicio.listar_subgrupos(grupo=grupo)

    @router.get("/catalogo/actividades", response_model=list[ActividadEconomicaOut])
    def catalogo_actividades(
        grupo: str | None = Query(None, description="Filtrar por grupo"),
        subgrupo: str | None = Query(None, description="Filtrar por subgrupo"),
    ):
        """Lista las actividades económicas (con alícuota)."""
        return servicio.listar_actividades(grupo=grupo, subgrupo=subgrupo)

    # ------------------------------------------------------------------
    # Operadores
    # ------------------------------------------------------------------

    @router.get("", response_model=list[ROCCAOperadorOut])
    def listar_operadores(
        tipo: str | None = Query(None, description="Filtrar por tipo de operador"),
        estado_registral: str | None = Query(None, description="Filtrar por estado registral"),
        categoria: str | None = Query(None, description="Filtrar por categoría (SALA_DE_DESPOSTE, CARNICERIAS, etc.)"),
    ):
        """Lista operadores, opcionalmente filtrados por tipo, estado y categoría."""
        return servicio.listar(tipo=tipo, estado_registral=estado_registral, categoria=categoria)

    @router.post("", response_model=ROCCAOperadorOut, status_code=201)
    def crear_operador(data: ROCCAOperadorIn):
        """Da de alta un operador en el registro provincial."""
        try:
            return servicio.crear_operador(data)
        except ROCCAOperadorError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.get("/{operador_id}", response_model=ROCCAOperadorOut)
    def obtener_operador(operador_id: int):
        """Obtiene un operador por su id."""
        operadores = servicio.listar()
        for op in operadores:
            if op.id == operador_id:
                return op
        raise HTTPException(status_code=404, detail=f"No existe un operador con id {operador_id}")

    @router.patch("/{operador_id}/estado", response_model=ROCCAOperadorOut)
    def cambiar_estado(operador_id: int, estado: EstadoRegistral = Query(..., description="Nuevo estado registral")):
        """Cambia el estado registral de un operador."""
        try:
            return servicio.cambiar_estado(operador_id, estado)
        except ROCCAOperadorError as e:
            raise HTTPException(status_code=404, detail=str(e))

    # ------------------------------------------------------------------
    # Certificado de operador (PDF)
    # ------------------------------------------------------------------

    @router.get("/{operador_id}/certificado.pdf")
    def certificado_operador(operador_id: int):
        """Genera y devuelve el Certificado de Operador en PDF.

        Usa la librería Python ``pdfme`` para reconstruir el diseño del
        template ``template-certificado-operador.json``.
        """
        operador = servicio.obtener(operador_id)
        if operador is None:
            raise HTTPException(status_code=404, detail=f"No existe un operador con id {operador_id}")

        habilitaciones = servicio.listar_habilitaciones(operador_id)
        inscripciones = servicio.listar_inscripciones(operador_id)

        from core.pdfme.certificado_operador import (
            CertificadoOperadorPDF,
            construir_certificado_data,
        )

        template_path = Path(__file__).resolve().parents[2] / "core" / "pdfme" / "template-certificado-operador.json"
        generador = CertificadoOperadorPDF(template_path)
        data = construir_certificado_data(servicio, operador, habilitaciones, inscripciones)
        pdf_bytes = generador.generar(data)

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'inline; filename="certificado-operador-{operador_id}.pdf"'
            },
        )

    # ------------------------------------------------------------------
    # Certificados
    # ------------------------------------------------------------------

    @router.get("/{operador_id}/certificados", response_model=list[CertificadoOut])
    def listar_certificados(operador_id: int):
        """Lista los certificados de un operador (con estado efectivo calculado)."""
        try:
            return servicio.listar_certificados(operador_id)
        except ROCCAOperadorError as e:
            raise HTTPException(status_code=404, detail=str(e))

    @router.post("/{operador_id}/certificados", response_model=CertificadoOut, status_code=201)
    def crear_certificado(operador_id: int, data: CertificadoIn):
        """Crea un certificado de habilitación para un operador.

        Si existe un certificado ACTIVO vigente en la fecha de emisión del nuevo,
        el anterior pasa a estado RELEVADO.
        """
        try:
            return servicio.crear_certificado(operador_id, data)
        except ROCCAOperadorError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.get("/{operador_id}/certificados/{certificado_id}", response_model=CertificadoOut)
    def obtener_certificado(operador_id: int, certificado_id: int):
        """Obtiene un certificado específico (con estado efectivo calculado)."""
        try:
            return servicio.obtener_certificado(operador_id, certificado_id)
        except ROCCAOperadorError as e:
            raise HTTPException(status_code=404, detail=str(e))

    @router.post("/{operador_id}/certificados/{certificado_id}/suspender", response_model=CertificadoOut)
    def suspender_certificado(operador_id: int, certificado_id: int, data: CertificadoSuspenderIn = CertificadoSuspenderIn()):
        """Suspende un certificado (acción de supervisor).

        Solo se puede suspender un certificado en estado ACTIVO.
        """
        try:
            return servicio.suspender_certificado(operador_id, certificado_id, data)
        except ROCCAOperadorError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.post("/{operador_id}/certificados/{certificado_id}/reactivar", response_model=CertificadoOut)
    def reactivar_certificado(operador_id: int, certificado_id: int):
        """Reactiva un certificado suspendido (acción de supervisor)."""
        try:
            return servicio.reactivar_certificado(operador_id, certificado_id)
        except ROCCAOperadorError as e:
            raise HTTPException(status_code=400, detail=str(e))

    # ------------------------------------------------------------------
    # Habilitaciones
    # ------------------------------------------------------------------

    @router.get("/{operador_id}/habilitaciones", response_model=list[HabilitacionOut])
    def listar_habilitaciones(operador_id: int):
        """Lista las habilitaciones de un operador."""
        return servicio.listar_habilitaciones(operador_id)

    @router.post("/{operador_id}/habilitaciones", response_model=HabilitacionOut, status_code=201)
    def agregar_habilitacion(operador_id: int, data: HabilitacionIn):
        """Agrega una habilitación a un operador."""
        try:
            return servicio.agregar_habilitacion(operador_id, data)
        except ROCCAOperadorError as e:
            raise HTTPException(status_code=404, detail=str(e))

    # ------------------------------------------------------------------
    # Inscripciones
    # ------------------------------------------------------------------

    @router.get("/{operador_id}/inscripciones", response_model=list[InscripcionOut])
    def listar_inscripciones(operador_id: int):
        """Lista las inscripciones de un operador."""
        return servicio.listar_inscripciones(operador_id)

    @router.post("/{operador_id}/inscripciones", response_model=InscripcionOut, status_code=201)
    def agregar_inscripcion(operador_id: int, data: InscripcionIn):
        """Agrega una inscripción a un operador."""
        try:
            return servicio.agregar_inscripcion(operador_id, data)
        except ROCCAOperadorError as e:
            raise HTTPException(status_code=404, detail=str(e))

    # ------------------------------------------------------------------
    # Domicilios operativos
    # ------------------------------------------------------------------

    @router.get("/{operador_id}/domicilios-operativos", response_model=list[DomicilioOperativoOut])
    def listar_domicilios_operativos(operador_id: int):
        """Lista los domicilios operativos de un operador."""
        return servicio.listar_domicilios_operativos(operador_id)

    @router.post("/{operador_id}/domicilios-operativos", response_model=DomicilioOperativoOut, status_code=201)
    def agregar_domicilio_operativo(operador_id: int, data: DomicilioOperativoIn):
        """Agrega un domicilio operativo a un operador."""
        try:
            return servicio.agregar_domicilio_operativo(operador_id, data)
        except ROCCAOperadorError as e:
            raise HTTPException(status_code=404, detail=str(e))

    # ------------------------------------------------------------------
    # Requisitos de inscripción
    # ------------------------------------------------------------------

    @router.get("/{operador_id}/requisitos", response_model=list[RequisitoInscripcionOut])
    def listar_requisitos(operador_id: int):
        """Lista los requisitos de inscripción de un operador."""
        return servicio.listar_requisitos(operador_id)

    @router.get("/{operador_id}/requisitos/pendientes", response_model=list[RequisitoInscripcionOut])
    def listar_requisitos_pendientes(operador_id: int):
        """Lista los requisitos aún no cumplidos de un operador."""
        return servicio.obtener_requisitos_pendientes(operador_id)

    @router.patch("/{operador_id}/requisitos/{requisito_id}")
    def actualizar_requisito(
        operador_id: int,
        requisito_id: int,
        cumplido: bool = Query(..., description="¿Está cumplido?"),
        observaciones: str | None = Query(None, description="Observaciones"),
    ):
        """Actualiza el estado de cumplimiento de un requisito."""
        try:
            return servicio.actualizar_requisito(operador_id, requisito_id, cumplido, observaciones)
        except ROCCAOperadorError as e:
            raise HTTPException(status_code=404, detail=str(e))

    return router
