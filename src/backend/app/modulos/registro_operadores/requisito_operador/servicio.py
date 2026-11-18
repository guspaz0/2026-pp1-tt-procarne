"""Servicio de requisitos de operador (upload de archivos de imagen)."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Optional

from configs.db import Base
from modulos.registro_operadores.operador_requisito.dao import OperadorRequisitoDAO
from modulos.registro_operadores.documento_requisito.dao import DocumentoRequisitoDAO
from modulos.registro_operadores.archivo.dao import ArchivoDAO


class RequisitoOperadorService:
    """Servicio para gestionar archivos de requisitos de operadores."""

    def __init__(
        self,
        operador_requisito_dao: OperadorRequisitoDAO,
        documento_requisito_dao: DocumentoRequisitoDAO,
        archivo_dao: ArchivoDAO,
        storage,
    ) -> None:
        self._or_dao = operador_requisito_dao
        self._dr_dao = documento_requisito_dao
        self._archivo_dao = archivo_dao
        self._storage = storage

    def subir_archivo_requisito(
        self,
        operador_id: int,
        requisito_categoria_id: int,
        archivo_bytes: bytes,
        filename: str,
        content_type: str,
    ) -> dict:
        """Sube un archivo de imagen para un requisito específico.

        1. Verifica que el operador_requisito exista (lo crea si no existe).
        2. Sube el archivo al storage.
        3. Crea un registro en archivos.
        4. Crea un documento_requisito vinculando el archivo al requisito.
        5. Actualiza el estado del requisito a CUMPLIDO.
        """
        # Paso 1: Obtener o crear el operador_requisito
        ors = self._or_dao.listar_por_operador(operador_id)
        or_req = None
        for or_ in ors:
            if or_.requisito_categoria_id == requisito_categoria_id:
                or_req = or_
                break

        if or_req is None:
            or_req = self._or_dao.crear(
                operador_id=operador_id,
                requisito_categoria_id=requisito_categoria_id,
                estado="PENDIENTE",
            )

        # Paso 2: Subir el archivo al storage
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        storage_path = f"requisitos/operador_{operador_id}/{timestamp}_{filename}"

        if self._storage:
            self._storage.upload_file(
                bucket="requisitos",
                object_name=storage_path,
                file=archivo_bytes,
                content_type=content_type,
            )
            url = self._storage.get_public_url("requisitos", storage_path)
        else:
            url = f"/api/files/{storage_path}"

        # Paso 3: Crear registro en archivos
        archivo = self._archivo_dao.crear(
            nombre=filename,
            storage_path=storage_path,
            size_bytes=len(archivo_bytes),
            mime_type=content_type,
        )

        # Paso 4: Crear documento_requisito
        self._dr_dao.crear(
            operador_requisito_id=or_req.id,
            archivo_id=archivo.id,
            persona_carga_id=None,  # Se puede obtener del request si es necesario
            fecha_carga=datetime.now(timezone.utc),
        )

        # Paso 5: Actualizar estado a CUMPLIDO
        self._or_dao.actualizar_estado(or_req.id, "CUMPLIDO")

        return {
            "operador_requisito_id": or_req.id,
            "archivo_id": archivo.id,
            "url": url,
            "estado": "CUMPLIDO",
        }

    def listar_archivos_requisito(
        self,
        operador_id: int,
        requisito_categoria_id: int,
    ) -> list[dict]:
        """Lista todos los archivos subidos para un requisito específico."""
        # Obtener el operador_requisito
        ors = self._or_dao.listar_por_operador(operador_id)
        or_req = None
        for or_ in ors:
            if or_.requisito_categoria_id == requisito_categoria_id:
                or_req = or_
                break

        if or_req is None:
            return []

        # Obtener documentos
        documentos = self._dr_dao.listar_por_operador_requisito(or_req.id)
        resultado = []
        for doc in documentos:
            archivo = self._archivo_dao.obtener_por_id(doc.archivo_id)
            if archivo:
                url = self._storage.get_public_url("requisitos", archivo.storage_path) if self._storage else f"/api/files/{archivo.storage_path}"
                resultado.append({
                    "documento_id": doc.id,
                    "archivo_id": archivo.id,
                    "nombre": archivo.nombre,
                    "url": url,
                    "fecha_carga": doc.fecha_carga.isoformat() if doc.fecha_carga else None,
                })
        return resultado
