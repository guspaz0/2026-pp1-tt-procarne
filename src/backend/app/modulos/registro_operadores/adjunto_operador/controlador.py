"""Controlador (router API) de ``AdjuntoOperador``.

Se incluye dentro del router raíz ``/api/registro-operadores`` del módulo
(ver :mod:`modulos.registro_operadores.controlador`).

El "request" de subida es JSON con ``data_base64`` (no multipart).
"""

from __future__ import annotations

import base64

from fastapi import APIRouter, HTTPException

from modulos.registro_operadores.adjunto_operador.dto import AdjuntoOperadorOut
from modulos.registro_operadores.adjunto_operador.servicio import AdjuntoOperadorService
from modulos.registro_operadores.operador.servicio import OperadorError


def crear_router(servicio: AdjuntoOperadorService | None, prefix: str = "") -> APIRouter:
    """Crea el router API de adjuntos (documentos) de operador.

    Si ``servicio`` es ``None`` (storage no configurado), los endpoints
    devuelven 503.
    """
    router = APIRouter(prefix=prefix, tags=["Registro de Operadores"])

    def _require_servicio():  # pragma: no cover - guard simple
        if servicio is None:
            raise HTTPException(status_code=503, detail="Adjuntos no configurados")

    @router.post("/{operador_id}/adjuntos", response_model=AdjuntoOperadorOut, status_code=201)
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

        _require_servicio()
        try:
            return await servicio.subir(
                operador_id=operador_id,
                requisito=requisito,
                filename=filename,
                content_type=content_type,
                size=len(data),
                data=data,
            )
        except OperadorError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.get("/{operador_id}/adjuntos", response_model=list[AdjuntoOperadorOut])
    def listar_adjuntos(operador_id: int):
        """Lista los adjuntos de un operador."""
        _require_servicio()
        return servicio.listar(operador_id)

    @router.get("/{operador_id}/adjuntos/{adjunto_id}/url")
    async def obtener_url_adjunto(operador_id: int, adjunto_id: int):
        """Devuelve una URL firmada para descargar un adjunto."""
        _require_servicio()
        try:
            url = await servicio.obtener_url(operador_id, adjunto_id)
            return {"url": url}
        except OperadorError as e:
            raise HTTPException(status_code=404, detail=str(e))

    @router.delete("/{operador_id}/adjuntos/{adjunto_id}", status_code=204)
    async def eliminar_adjunto(operador_id: int, adjunto_id: int):
        """Elimina un adjunto (fila + objeto en storage)."""
        _require_servicio()
        try:
            await servicio.eliminar(operador_id, adjunto_id)
        except OperadorError as e:
            raise HTTPException(status_code=404, detail=str(e))

    return router
