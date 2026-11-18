"""Controlador (router API) de requisitos de operador.

Rutas ``/api/registro-operadores/{operador_id}/requisitos``:
- ``POST /{requisito_categoria_id}/archivo`` — sube un archivo de imagen.
- ``GET  /{requisito_categoria_id}/archivos`` — lista archivos subidos.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, UploadFile, File, Query
from modulos.registro_operadores.requisito_operador.servicio import RequisitoOperadorService


def crear_router(servicio: RequisitoOperadorService, prefix: str = "") -> APIRouter:
    """Crea el router API de requisitos de operador."""
    router = APIRouter(
        prefix="/api/registro-operadores/{operador_id}/requisitos",
        tags=["Requisitos de Operador"],
    )

    @router.post("/{requisito_categoria_id}/archivo", status_code=201)
    async def subir_archivo(
        operador_id: int,
        requisito_categoria_id: int,
        file: UploadFile = File(...),
    ):
        """Sube un archivo de imagen para un requisito específico.

        El archivo debe ser una imagen (JPG, PNG, PDF, etc.).
        """
        # Validar tipo de archivo
        content_type = file.content_type or ""
        if not content_type.startswith(("image/", "application/pdf")):
            raise HTTPException(
                status_code=400,
                detail="Solo se permiten imágenes (JPG, PNG) o PDF",
            )

        # Leer el archivo
        archivo_bytes = await file.read()

        # Validar tamaño máximo (10MB)
        if len(archivo_bytes) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="El archivo no puede superar los 10MB",
            )

        try:
            resultado = servicio.subir_archivo_requisito(
                operador_id=operador_id,
                requisito_categoria_id=requisito_categoria_id,
                archivo_bytes=archivo_bytes,
                filename=file.filename or "archivo",
                content_type=content_type,
            )
            return resultado
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al subir archivo: {str(e)}")

    @router.get("/{requisito_categoria_id}/archivos")
    def listar_archivos(
        operador_id: int,
        requisito_categoria_id: int,
    ):
        """Lista todos los archivos subidos para un requisito específico."""
        return servicio.listar_archivos_requisito(
            operador_id=operador_id,
            requisito_categoria_id=requisito_categoria_id,
        )

    return router
