"""Controlador (router API) de ``Certificado``.

Se incluye dentro del router raíz ``/api/registro-operadores`` del módulo
(ver :mod:`modulos.registro_operadores.controlador`).

Incluye:
- CRUD de certificados (con RBAC supervisor/admin para crear/suspender).
- ``GET /{operador_id}/certificado-vigente`` — certificado válido.
- ``GET /{operador_id}/certificado.pdf`` — generación de PDF (F102).
- ``GET /{operador_id}/carton-f102.pdf`` — Formulario F102 mockeado (estático).
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
                 prefix: str = "") -> APIRouter:
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

    @router.post("/certificados/suspender", response_model=CertificadoOut)
    def suspender_certificado(request: Request,
                              data: CertificadoSuspenderIn):
        """Suspende el certificado vigente del operador (acción de supervisor).

        El ``operador_id`` se pasa en el body (JSON). El operador no puede
        tener dos certificados ACTIVOS simultáneos, por lo que se resuelve
        automáticamente el certificado vigente. Solo se puede suspender un
        certificado en estado ACTIVO.
        """
        _require_supervisor(request)
        try:
            return servicio.suspender(data.operador_id, None, data)
        except OperadorError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.post("/certificados/reactivar", response_model=CertificadoOut)
    def reactivar_certificado(request: Request,
                              data: CertificadoSuspenderIn):
        """Reactiva el certificado suspendido del operador (acción de supervisor).

        El ``operador_id`` se pasa en el body (JSON). Se resuelve
        automáticamente el certificado vigente (el único que puede estar
        SUSPENDIDO). Solo se puede reactivar un certificado en estado
        SUSPENDIDO.
        """
        _require_supervisor(request)
        try:
            return servicio.reactivar(data.operador_id, None)
        except OperadorError as e:
            raise HTTPException(status_code=400, detail=str(e))

    return router
