"""Servicio de negocio de la persona.

Casos de uso:
- Crear una persona (física o jurídica).
- Buscar por documento.
- Listar personas.
- Gestionar adjuntos (documentos) de la persona.
"""

from __future__ import annotations

from core.persona.adjunto_dao import AdjuntoPersona, AdjuntoPersonaDAO
from core.persona.dao import Persona, PersonaDAO
from core.persona.schema import PersonaIn, PersonaOut
from core.storage.insforge import InsforgeStorage


class PersonaError(Exception):
    """Error de negocio del servicio de personas."""


# Requisitos válidos para adjuntos de persona
REQUISITOS_VALIDOS_PERSONA = {"dni_frente", "dni_dorso", "cuit", "iibb"}
# Content types permitidos
CONTENT_TYPES_PERMITIDOS = {"image/jpeg", "image/png", "application/pdf"}
# Tamaño máximo: 10 MB
TAMANO_MAXIMO = 10 * 1024 * 1024


class PersonaService:
    """Servicio de negocio de personas."""

    def __init__(self, dao: PersonaDAO, adjunto_dao: AdjuntoPersonaDAO | None = None,
                 storage: InsforgeStorage | None = None) -> None:
        self._dao = dao
        self._adjunto_dao = adjunto_dao
        self._storage = storage

    def crear_persona(self, data: PersonaIn) -> PersonaOut:
        """Crea una persona y devuelve su representación de salida."""
        existente = self._dao.obtener_por_documento(data.tipo_documento, data.identificador)
        if existente is not None:
            raise PersonaError(
                f"Ya existe una persona con documento {data.tipo_documento} {data.identificador}"
            )
        persona = self._dao.crear(
            tipo=data.tipo,
            tipo_documento=data.tipo_documento,
            identificador=data.identificador,
            nombre=data.nombre,
            domicilio=data.domicilio,
        )
        return PersonaOut.model_validate(persona)

    def obtener_por_documento(self, tipo_documento: str, identificador: str) -> PersonaOut | None:
        """Busca una persona por su documento."""
        persona = self._dao.obtener_por_documento(tipo_documento, identificador)
        return PersonaOut.model_validate(persona) if persona else None

    def listar(self) -> list[PersonaOut]:
        """Lista todas las personas."""
        return [PersonaOut.model_validate(p) for p in self._dao.listar()]

    # ------------------------------------------------------------------
    # Adjuntos
    # ------------------------------------------------------------------

    async def subir_adjunto(
        self, persona_id: int, requisito: str, filename: str,
        content_type: str, size: int, data: bytes,
    ) -> dict:
        """Sube un adjunto a storage y registra la fila en BD."""
        if requisito not in REQUISITOS_VALIDOS_PERSONA:
            raise PersonaError(f"Requisito inválido para persona: {requisito}")
        if content_type not in CONTENT_TYPES_PERMITIDOS:
            raise PersonaError(f"Tipo de archivo no permitido: {content_type}")
        if size > TAMANO_MAXIMO:
            raise PersonaError(f"Archivo excede el tamaño máximo de 10 MB")
        if self._storage is None:
            raise PersonaError("Storage no configurado")
        if self._adjunto_dao is None:
            raise PersonaError("DAO de adjuntos no configurado")

        # Verificar que la persona existe
        persona = self._dao.obtener_por_id(persona_id)
        if persona is None:
            raise PersonaError(f"No existe una persona con id {persona_id}")

        # Subir a storage
        storage_key = await self._storage.upload(filename, content_type, size, data)

        # Registrar en BD
        adjunto = self._adjunto_dao.crear(
            persona_id=persona_id,
            requisito=requisito,
            storage_key=storage_key,
            content_type=content_type,
            size=size,
            nombre_original=filename,
        )
        return self._adjunto_a_dict(adjunto)

    def listar_adjuntos(self, persona_id: int) -> list[dict]:
        """Lista los adjuntos de una persona."""
        if self._adjunto_dao is None:
            return []
        adjuntos = self._adjunto_dao.listar_por_persona(persona_id)
        return [self._adjunto_a_dict(a) for a in adjuntos]

    async def obtener_url_adjunto(self, persona_id: int, adjunto_id: int) -> str:
        """Obtiene una URL firmada para descargar un adjunto."""
        if self._adjunto_dao is None or self._storage is None:
            raise PersonaError("Storage no configurado")
        adjunto = self._adjunto_dao.obtener_por_id(adjunto_id)
        if adjunto is None or adjunto.persona_id != persona_id:
            raise PersonaError(f"No existe un adjunto {adjunto_id} para la persona {persona_id}")
        return await self._storage.download_url(adjunto.storage_key)

    async def eliminar_adjunto(self, persona_id: int, adjunto_id: int) -> None:
        """Elimina un adjunto (fila + objeto en storage)."""
        if self._adjunto_dao is None:
            raise PersonaError("DAO de adjuntos no configurado")
        adjunto = self._adjunto_dao.obtener_por_id(adjunto_id)
        if adjunto is None or adjunto.persona_id != persona_id:
            raise PersonaError(f"No existe un adjunto {adjunto_id} para la persona {persona_id}")
        # Borrar de storage (best-effort)
        if self._storage:
            try:
                await self._storage.delete(adjunto.storage_key)
            except Exception:
                pass  # No bloquear la eliminación de la fila
        self._adjunto_dao.eliminar(adjunto_id)

    @staticmethod
    def _adjunto_a_dict(adjunto: AdjuntoPersona) -> dict:
        return {
            "id": adjunto.id,
            "persona_id": adjunto.persona_id,
            "requisito": adjunto.requisito,
            "storage_key": adjunto.storage_key,
            "content_type": adjunto.content_type,
            "size": adjunto.size,
            "nombre_original": adjunto.nombre_original,
            "creado_en": adjunto.creado_en.isoformat() if adjunto.creado_en else None,
        }
