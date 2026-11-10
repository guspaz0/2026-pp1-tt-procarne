"""Controlador (router API) de personas y sus adjuntos.

Nota: no usamos ``UploadFile``/``File``/``Form`` de FastAPI porque
``python-multipart`` no está disponible en este entorno. En su lugar,
el frontend envía el archivo como base64 en un cuerpo JSON:

    POST /api/personas/{id}/adjuntos
    {
        "requisito": "dni_frente",
        "filename": "dni.jpg",
        "content_type": "image/jpeg",
        "data_base64": "<base64-encoded bytes>"
    }
"""

from __future__ import annotations

import base64

from fastapi import APIRouter, HTTPException

from core.persona.schema import PersonaOut
from core.persona.servicio import PersonaError, PersonaService


class AdjuntoIn:
    """DTO de entrada para subir un adjunto (sin pydantic para evitar dependencias)."""
    pass


def crear_router(servicio: PersonaService) -> APIRouter:
    """Crea el router API de personas."""
    router = APIRouter(prefix="/api/personas", tags=["Personas"])

    # ------------------------------------------------------------------
    # Personas (básico)
    # ------------------------------------------------------------------

    @router.get("")
    def listar_personas():
        """Lista todas las personas."""
        return servicio.listar()

    @router.get("/{persona_id}")
    def obtener_persona(persona_id: int):
        """Obtiene una persona por id."""
        for p in servicio.listar():
            if p.id == persona_id:
                return p
        raise HTTPException(status_code=404, detail=f"No existe una persona con id {persona_id}")

    # ------------------------------------------------------------------
    # Adjuntos de persona
    # ------------------------------------------------------------------

    @router.post("/{persona_id}/adjuntos", status_code=201)
    async def subir_adjunto(persona_id: int, body: dict):
        """Sube un adjunto (documento) a una persona.

        Body JSON:
        - ``requisito``: dni_frente | dni_dorso | cuit | iibb
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
            return await servicio.subir_adjunto(
                persona_id=persona_id,
                requisito=requisito,
                filename=filename,
                content_type=content_type,
                size=len(data),
                data=data,
            )
        except PersonaError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.get("/{persona_id}/adjuntos")
    def listar_adjuntos(persona_id: int):
        """Lista los adjuntos de una persona."""
        return servicio.listar_adjuntos(persona_id)

    @router.get("/{persona_id}/adjuntos/{adjunto_id}/url")
    async def obtener_url_adjunto(persona_id: int, adjunto_id: int):
        """Devuelve una URL firmada para descargar un adjunto."""
        try:
            url = await servicio.obtener_url_adjunto(persona_id, adjunto_id)
            return {"url": url}
        except PersonaError as e:
            raise HTTPException(status_code=404, detail=str(e))

    @router.delete("/{persona_id}/adjuntos/{adjunto_id}", status_code=204)
    async def eliminar_adjunto(persona_id: int, adjunto_id: int):
        """Elimina un adjunto (fila + objeto en storage)."""
        try:
            await servicio.eliminar_adjunto(persona_id, adjunto_id)
        except PersonaError as e:
            raise HTTPException(status_code=404, detail=str(e))

    return router
