"""Controlador (router API) del Módulo I — Registro Provincial de Operadores."""

from __future__ import annotations

from pathlib import Path

import base64

from fastapi import APIRouter, HTTPException, Query, Request
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


def _require_supervisor(request: Request) -> None:
    """Verifica que el usuario autenticado tenga rol supervisor o admin.

    Lee ``request.state.user.user_metadata.rol`` (inyectado por el middleware
    de InsForge). Si no tiene rol suficiente → 403.
    """
    user = getattr(request.state, "user", None)
    if user is None:
        raise HTTPException(status_code=401, detail="No autenticado")
    metadata = user.get("user_metadata", {}) if isinstance(user, dict) else getattr(user, "user_metadata", {})
    rol = metadata.get("rol", "") if isinstance(metadata, dict) else ""
    if rol not in ("supervisor", "admin"):
        raise HTTPException(status_code=403, detail="Requiere rol supervisor o admin")


def _require_operador_activo(servicio: ROCCAOperadorService, operador_id: int) -> None:
    """Verifica que el operador esté en estado ACTIVO.

    Si no → 400 con el estado actual.
    """
    from modulos.registro_operadores.enums import EstadoRegistral
    operador = servicio.obtener(operador_id)
    if operador is None:
        raise HTTPException(status_code=404, detail=f"No existe un operador con id {operador_id}")
    if operador.estado_registral != EstadoRegistral.ACTIVO.value:
        raise HTTPException(
            status_code=400,
            detail=f"El operador debe estar ACTIVO para generar un certificado (estado actual: {operador.estado_registral})",
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
    # Certificado vigente (JSON)
    # ------------------------------------------------------------------

    @router.get("/{operador_id}/certificado-vigente", response_model=CertificadoOut | None)
    def certificado_vigente(operador_id: int):
        """Devuelve el certificado válido del operador (max vencimiento + max emisión).

        Si no existe ninguno → 404.
        """
        try:
            cert = servicio.obtener_certificado_vigente(operador_id)
        except ROCCAOperadorError as e:
            raise HTTPException(status_code=404, detail=str(e))
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
        operador = servicio.obtener(operador_id)
        if operador is None:
            raise HTTPException(status_code=404, detail=f"No existe un operador con id {operador_id}")

        # Intentar obtener el certificado vigente como fuente de datos
        try:
            cert_vigente = servicio.obtener_certificado_vigente(operador_id)
        except ROCCAOperadorError:
            cert_vigente = None

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
        try:
            return servicio.listar_certificados(operador_id)
        except ROCCAOperadorError as e:
            raise HTTPException(status_code=404, detail=str(e))

    @router.post("/{operador_id}/certificados", response_model=CertificadoOut, status_code=201)
    def crear_certificado(operador_id: int, data: CertificadoIn, request: Request):
        """Crea un certificado de habilitación para un operador.

        Requiere rol supervisor/admin y operador en estado ACTIVO.
        Si existe un certificado ACTIVO vigente en la fecha de emisión del nuevo,
        el anterior pasa a estado RELEVADO.
        """
        _require_supervisor(request)
        _require_operador_activo(servicio, operador_id)
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
    def suspender_certificado(operador_id: int, certificado_id: int, request: Request, data: CertificadoSuspenderIn = CertificadoSuspenderIn()):
        """Suspende un certificado (acción de supervisor).

        Solo se puede suspender un certificado en estado ACTIVO.
        """
        _require_supervisor(request)
        try:
            return servicio.suspender_certificado(operador_id, certificado_id, data)
        except ROCCAOperadorError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.post("/{operador_id}/certificados/{certificado_id}/reactivar", response_model=CertificadoOut)
    def reactivar_certificado(operador_id: int, certificado_id: int, request: Request):
        """Reactiva un certificado suspendido (acción de supervisor)."""
        _require_supervisor(request)
        try:
            return servicio.reactivar_certificado(operador_id, certificado_id)
        except ROCCAOperadorError as e:
            raise HTTPException(status_code=400, detail=str(e))

    # ------------------------------------------------------------------
    # Ciclo de vida del operador (activar / suspender / reactivar / bajar)
    # ------------------------------------------------------------------

    @router.post("/{operador_id}/activar", response_model=ROCCAOperadorOut)
    def activar_operador(operador_id: int, request: Request):
        """Activa un operador PENDIENTE (acción de supervisor).

        Cambia PENDIENTE → ACTIVO. Si ya está ACTIVO → 400.
        """
        _require_supervisor(request)
        from modulos.registro_operadores.enums import EstadoRegistral
        try:
            operador = servicio.obtener(operador_id)
            if operador is None:
                raise HTTPException(status_code=404, detail=f"No existe un operador con id {operador_id}")
            if operador.estado_registral == EstadoRegistral.ACTIVO.value:
                raise HTTPException(status_code=400, detail="El operador ya está ACTIVO")
            if operador.estado_registral == EstadoRegistral.BAJADO.value:
                raise HTTPException(status_code=400, detail="No se puede activar un operador BAJADO")
            actualizado = servicio._dao.actualizar_estado(operador_id, EstadoRegistral.ACTIVO)
            return ROCCAOperadorOut.model_validate(actualizado)
        except HTTPException:
            raise
        except ROCCAOperadorError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.post("/{operador_id}/suspender", response_model=ROCCAOperadorOut)
    def suspender_operador(operador_id: int, request: Request):
        """Suspende un operador ACTIVO (acción de supervisor).

        Cambia ACTIVO → SUSPENDIDO.
        """
        _require_supervisor(request)
        from modulos.registro_operadores.enums import EstadoRegistral
        try:
            operador = servicio.obtener(operador_id)
            if operador is None:
                raise HTTPException(status_code=404, detail=f"No existe un operador con id {operador_id}")
            if operador.estado_registral != EstadoRegistral.ACTIVO.value:
                raise HTTPException(status_code=400, detail=f"Solo se puede suspender un operador ACTIVO (estado actual: {operador.estado_registral})")
            return ROCCAOperadorOut.model_validate(servicio._dao.actualizar_estado(operador_id, EstadoRegistral.SUSPENDIDO))
        except HTTPException:
            raise
        except ROCCAOperadorError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.post("/{operador_id}/reactivar", response_model=ROCCAOperadorOut)
    def reactivar_operador(operador_id: int, request: Request):
        """Reactiva un operador SUSPENDIDO (acción de supervisor).

        Cambia SUSPENDIDO → ACTIVO.
        """
        _require_supervisor(request)
        from modulos.registro_operadores.enums import EstadoRegistral
        try:
            operador = servicio.obtener(operador_id)
            if operador is None:
                raise HTTPException(status_code=404, detail=f"No existe un operador con id {operador_id}")
            if operador.estado_registral != EstadoRegistral.SUSPENDIDO.value:
                raise HTTPException(status_code=400, detail=f"Solo se puede reactivar un operador SUSPENDIDO (estado actual: {operador.estado_registral})")
            return ROCCAOperadorOut.model_validate(servicio._dao.actualizar_estado(operador_id, EstadoRegistral.ACTIVO))
        except HTTPException:
            raise
        except ROCCAOperadorError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.post("/{operador_id}/bajar", response_model=ROCCAOperadorOut)
    def bajar_operador(operador_id: int, request: Request):
        """Da de baja un operador (acción de supervisor).

        Cambia a BAJADO. Solo desde ACTIVO o SUSPENDIDO.
        """
        _require_supervisor(request)
        from modulos.registro_operadores.enums import EstadoRegistral
        try:
            operador = servicio.obtener(operador_id)
            if operador is None:
                raise HTTPException(status_code=404, detail=f"No existe un operador con id {operador_id}")
            if operador.estado_registral not in (EstadoRegistral.ACTIVO.value, EstadoRegistral.SUSPENDIDO.value):
                raise HTTPException(status_code=400, detail=f"Solo se puede dar de baja un operador ACTIVO o SUSPENDIDO (estado actual: {operador.estado_registral})")
            return ROCCAOperadorOut.model_validate(servicio._dao.actualizar_estado(operador_id, EstadoRegistral.BAJADO))
        except HTTPException:
            raise
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

    # ------------------------------------------------------------------
    # Adjuntos de operador
    # ------------------------------------------------------------------

    @router.post("/{operador_id}/adjuntos", status_code=201)
    async def subir_adjunto(operador_id: int, body: dict):
        """Sube un adjunto (documento) a un operador.

        Body JSON:
        - ``requisito``: código del requisito (debe corresponder a la categoría)
        - ``filename``: nombre original del archivo
        - ``content_type``: MIME type (image/jpeg, image/png, application/pdf)
        - ``data_base64``: contenido del archivo en base64
        """
        requisito = body.get("requisito", "")
        filename = body.get("filename", "sin_nombre")
        content_type = body.get("content_type", "application/octet-stream")
        data_b64 = body.get("data_base64", "")

        if not data_b64:
            raise HTTPException(status_code=400, detail="Falta el campo data_base64")

        try:
            data = base64.b64decode(data_b64)
        except Exception:
            raise HTTPException(status_code=400, detail="data_base64 no es base64 válido")

        try:
            return await servicio.subir_adjunto_operador(
                operador_id=operador_id,
                requisito=requisito,
                filename=filename,
                content_type=content_type,
                size=len(data),
                data=data,
            )
        except ROCCAOperadorError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.get("/{operador_id}/adjuntos")
    def listar_adjuntos(operador_id: int):
        """Lista los adjuntos de un operador."""
        return servicio.listar_adjuntos_operador(operador_id)

    @router.get("/{operador_id}/adjuntos/{adjunto_id}/url")
    async def obtener_url_adjunto(operador_id: int, adjunto_id: int):
        """Devuelve una URL firmada para descargar un adjunto."""
        try:
            url = await servicio.obtener_url_adjunto_operador(operador_id, adjunto_id)
            return {"url": url}
        except ROCCAOperadorError as e:
            raise HTTPException(status_code=404, detail=str(e))

    @router.delete("/{operador_id}/adjuntos/{adjunto_id}", status_code=204)
    async def eliminar_adjunto(operador_id: int, adjunto_id: int):
        """Elimina un adjunto (fila + objeto en storage)."""
        try:
            await servicio.eliminar_adjunto_operador(operador_id, adjunto_id)
        except ROCCAOperadorError as e:
            raise HTTPException(status_code=404, detail=str(e))

    return router
