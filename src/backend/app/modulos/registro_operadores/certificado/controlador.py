"""Controlador (router API) de ``Certificado``.

Se incluye dentro del router raíz ``/api/registro-operadores`` del módulo
(ver :mod:`modulos.registro_operadores.controlador`).

Incluye:
- CRUD de certificados (con RBAC supervisor/admin para crear/suspender).
- ``GET /{operador_id}/certificado-vigente`` — certificado válido.
- ``GET /{operador_id}/certificado.pdf`` — generación de PDF (F102).
"""

from __future__ import annotations

import base64
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request

from modulos.registro_operadores.certificado.dto import (
    CertificadoIn,
    CertificadoOut,
    CertificadoSuspenderIn,
)
from modulos.registro_operadores.certificado.servicio import CertificadoService
from modulos.registro_operadores.enums import EstadoRegistral
from modulos.registro_operadores.operador.servicio import OperadorError, OperadorService
from modulos.registro_operadores.operador.controlador import _require_supervisor


def _require_operador_activo(servicio: OperadorService, operador_id: int) -> None:
    """Verifica que el operador esté en estado ACTIVO.

    Si no → 400 con el estado actual.
    """
    operador = servicio.obtener(operador_id)
    if operador is None:
        raise HTTPException(status_code=404, detail=f"No existe un operador con id {operador_id}")
    if operador.estado_registral != EstadoRegistral.ACTIVO.value:
        raise HTTPException(
            status_code=400,
            detail=f"El operador debe estar ACTIVO para generar un certificado (estado actual: {operador.estado_registral})",
        )


def crear_router(servicio: CertificadoService,
                 operador_service: OperadorService,
                 habilitacion_service=None,
                 inscripcion_service=None, prefix: str = "") -> APIRouter:
    """Crea el router API de certificados de operador."""
    router = APIRouter(prefix=prefix, tags=["Registro de Operadores"])

    # ------------------------------------------------------------------
    # Certificado vigente (JSON)
    # ------------------------------------------------------------------

    @router.get("/{operador_id}/certificado-vigente", response_model=CertificadoOut | None)
    def certificado_vigente(operador_id: int):
        """Devuelve el certificado válido del operador (max vencimiento + max emisión).

        Si no existe ninguno → 404.
        """
        if operador_service.obtener(operador_id) is None:
            raise HTTPException(status_code=404, detail=f"No existe un operador con id {operador_id}")
        cert = servicio.obtener_vigente(operador_id)
        if cert is None:
            raise HTTPException(status_code=404, detail="No hay certificado válido para este operador")
        return cert

    # ------------------------------------------------------------------
    # Certificado de operador (PDF)
    # ------------------------------------------------------------------

    @router.get("/{operador_id}/certificado.pdf")
    def certificado_operador(operador_id: int):
        """Genera y devuelve el Certificado de Operador en PDF.

        Usa el certificado vigente como fuente de datos si existe;
        si no, usa los datos del operador directamente.
        Devuelve el PDF como base64 en JSON.
        """
        operador = operador_service.obtener(operador_id)
        if operador is None:
            raise HTTPException(status_code=404, detail=f"No existe un operador con id {operador_id}")

        # Intentar obtener el certificado vigente como fuente de datos
        try:
            cert_vigente = servicio.obtener_vigente(operador_id)
        except OperadorError:
            cert_vigente = None

        habilitaciones = habilitacion_service.listar(operador_id) if habilitacion_service else []
        inscripciones = inscripcion_service.listar(operador_id) if inscripcion_service else []

        from core.pdfme.certificado_operador import (
            CertificadoOperadorPDF,
            construir_certificado_data,
        )

        # __file__ = .../app/modulos/registro_operadores/certificado/controlador.py
        # parents[0]=certificado, [1]=registro_operadores, [2]=modulos, [3]=app
        template_path = Path(__file__).resolve().parents[3] / "core" / "pdfme" / "template-certificado-operador.json"
        generador = CertificadoOperadorPDF(template_path)
        data = construir_certificado_data(operador_service, operador, habilitaciones, inscripciones)
        pdf_bytes = generador.generar(data)

        pdf_b64 = base64.b64encode(pdf_bytes).decode("ascii")
        nombre = f"certificado-f102-{cert_vigente.numero_certificado}.pdf" if cert_vigente else f"certificado-operador-{operador_id}.pdf"
        return {
            "pdf_base64": pdf_b64,
            "nombre_archivo": nombre,
            "content_type": "application/pdf",
        }

    # ------------------------------------------------------------------
    # Certificados (CRUD)
    # ------------------------------------------------------------------

    @router.get("/{operador_id}/certificados", response_model=list[CertificadoOut])
    def listar_certificados(operador_id: int):
        """Lista los certificados de un operador (con estado efectivo calculado)."""
        if operador_service.obtener(operador_id) is None:
            raise HTTPException(status_code=404, detail=f"No existe un operador con id {operador_id}")
        return servicio.listar(operador_id)

    @router.post("/{operador_id}/certificados", response_model=CertificadoOut, status_code=201)
    def crear_certificado(operador_id: int, data: CertificadoIn, request: Request):
        """Crea un certificado de habilitación para un operador.

        Requiere rol supervisor/admin y operador en estado ACTIVO.
        Si existe un certificado ACTIVO vigente en la fecha de emisión del nuevo,
        el anterior pasa a estado RELEVADO.
        """
        _require_supervisor(request)
        _require_operador_activo(operador_service, operador_id)
        try:
            return servicio.crear(operador_id, data)
        except OperadorError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.get("/{operador_id}/certificados/{certificado_id}", response_model=CertificadoOut)
    def obtener_certificado(operador_id: int, certificado_id: int):
        """Obtiene un certificado específico (con estado efectivo calculado)."""
        try:
            return servicio.obtener(operador_id, certificado_id)
        except OperadorError as e:
            raise HTTPException(status_code=404, detail=str(e))

    @router.post("/{operador_id}/certificados/{certificado_id}/suspender", response_model=CertificadoOut)
    def suspender_certificado(operador_id: int, certificado_id: int, request: Request,
                              data: CertificadoSuspenderIn = CertificadoSuspenderIn()):
        """Suspende un certificado (acción de supervisor).

        Solo se puede suspender un certificado en estado ACTIVO.
        """
        _require_supervisor(request)
        try:
            return servicio.suspender(operador_id, certificado_id, data)
        except OperadorError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.post("/{operador_id}/certificados/{certificado_id}/reactivar", response_model=CertificadoOut)
    def reactivar_certificado(operador_id: int, certificado_id: int, request: Request):
        """Reactiva un certificado suspendido (acción de supervisor)."""
        _require_supervisor(request)
        try:
            return servicio.reactivar(operador_id, certificado_id)
        except OperadorError as e:
            raise HTTPException(status_code=400, detail=str(e))

    return router
