"""Lógica de negocio de ``Operador``.

Casos de uso del operador (agregado raíz del módulo):
- Alta de operador (con creación idempotente de la persona titular).
- Búsqueda por CUIT / id, listado con filtros.
- Cambio de estado registral.
- Creación de los requisitos iniciales (generales + específicos por
  categoría) al dar de alta un operador.

El catálogo de requisitos por categoría vive en
:mod:`modulos.registro_operadores.requisito_inscripcion.servicio`.
"""

from __future__ import annotations

from modulos.registro_operadores.errores import OperadorError
from modulos.registro_operadores.enums import CategoriaOperador
from modulos.registro_operadores.operador.dao import OperadorDAO
from modulos.registro_operadores.operador.dto import OperadorIn, OperadorOut


class OperadorService:
    """Servicio de negocio de operadores de la cadena cárnica."""

    def __init__(self, dao: OperadorDAO, persona_service=None,
                 requisito_service=None,
                 certificado_service=None, catalogo_actividades_dao=None) -> None:
        self._dao = dao
        self._persona_service = persona_service
        self._requisito_service = requisito_service
        self._certificado_service = certificado_service
        self._catalogo_actividades_dao = catalogo_actividades_dao

    # ------------------------------------------------------------------
    # Operadores
    # ------------------------------------------------------------------

    def crear_operador(self, data: OperadorIn) -> OperadorOut:
        """Da de alta un operador y devuelve su representación de salida.

        El CUIT no se guarda en ``operadores``: identifica a la persona
        titular (1 persona : N operadores, el identificador es único por
        persona). Si el alta no trae ``persona_id``, se resuelve/crea la
        persona por CUIT y el operador se vincula a ella.
        """
        # ``operadores.persona_id`` es NOT NULL: si el alta no trae la persona
        # titular, la resolvemos/creamos por CUIT (idempotente).
        persona_id = self._resolver_persona(data.persona_id, data.cuit, data.razon_social, data.tipo)

        # Validar categoría si se proporciona
        if data.categoria is not None:
            categorias_validas = [c.value for c in CategoriaOperador]
            if data.categoria not in categorias_validas:
                raise OperadorError(
                    f"Categoría inválida: {data.categoria}. "
                    f"Categorías válidas: {', '.join(categorias_validas)}"
                )

        operador = self._dao.crear(
            razon_social=data.razon_social,
            tipo=data.tipo,
            persona_id=persona_id,
            domicilio_comercial=data.domicilio_comercial,
            telefono=data.telefono,
            email=data.email,
            categoria=data.categoria,
        )

        # Cargar la relación persona ANTES de que el DAO cierre la sesión.
        # ``operadores.persona`` es lazy-load; si se accede después del
        # ``session.close()`` del DAO, lanza ``DetachedInstanceError``.
        try:
            _persona = operador.persona  # noqa: F841 — fuerza el lazy load
        except Exception:
            pass

        # Crear los requisitos (generales + específicos) con estado "no cumplido"
        self._crear_requisitos_iniciales(operador.id, data.categoria)

        # Guardar las actividades económicas del catálogo (N:M).
        # ``actividad_ids`` son ids directos; ``codigo_afip`` son códigos del
        # catálogo (AFIP) que se resuelven a ids. Se combinan ambos.
        ids: list[int] = list(data.actividad_ids or [])
        if data.codigo_afip and self._catalogo_actividades_dao is not None:
            ids.extend(self._catalogo_actividades_dao.resolver_ids_por_codigos(data.codigo_afip))
        if ids:
            self._dao.asignar_actividades(operador.id, ids)

        return self._to_out(operador)

    def _to_out(self, operador) -> OperadorOut:
        """Convierte un ORM a DTO resolviendo las actividades (N:M)."""
        # ``from_attributes`` solo extrae campos en ``model_fields``; la relación
        # ``persona`` no es un campo del DTO, así que se pasa explícitamente para
        # que ``_inferir_cuit`` pueda leer ``persona.identificador``.
        attrs = {k: getattr(operador, k, None) for k in OperadorOut.model_fields}
        attrs["actividad_ids"] = self._dao.listar_actividad_ids(operador.id)
        try:
            attrs["persona"] = operador.persona
        except Exception:
            pass
        return OperadorOut.model_validate(attrs)

    def obtener(self, operador_id: int) -> OperadorOut | None:
        """Busca un operador por su id."""
        operador = self._dao.obtener_por_id(operador_id)
        return self._to_out(operador) if operador else None

    def obtener_por_cuit(self, cuit: str) -> OperadorOut | None:
        """Busca un operador por el CUIT de su persona titular.

        El CUIT no vive en ``operadores``: se infiere de
        ``persona.identificador``. Se busca la persona por CUIT y se
        devuelve el primer operador vinculado a ella.
        """
        if self._persona_service is None:
            return None
        persona = self._persona_service.obtener_por_documento("CUIT", cuit)
        if persona is None:
            return None
        operadores = self._dao.listar()
        for op in operadores:
            if op.persona_id == persona.id:
                return self._to_out(op)
        return None

    def listar(self, tipo: str | None = None,
               estado_registral: str | None = None,
               categoria: str | None = None) -> list[OperadorOut]:
        """Lista operadores, opcionalmente filtrados por tipo, estado y categoría."""
        operadores = self._dao.listar(tipo=tipo, estado_registral=estado_registral, categoria=categoria)
        return [self._to_out(op) for op in operadores]

    def cambiar_estado(self, operador_id: int, estado) -> OperadorOut:
        """Cambia el estado registral de un operador."""
        operador = self._dao.actualizar_estado(operador_id, estado)
        if operador is None:
            raise OperadorError(f"No existe un operador con id {operador_id}")
        return self._to_out(operador)

    # ------------------------------------------------------------------
    # Delegación a servicios por entidad (API pública del servicio antiguo)
    # ------------------------------------------------------------------

    def listar_requisitos(self, operador_id: int) -> list["RequisitoInscripcionOut"]:
        """Lista los requisitos de un operador."""
        if self._requisito_service is None:
            raise OperadorError("RequisitoInscripcionService no configurado")
        return self._requisito_service.listar(operador_id)

    def listar_requisitos_pendientes(self, operador_id: int) -> list["RequisitoInscripcionOut"]:
        """Lista los requisitos pendientes de un operador."""
        if self._requisito_service is None:
            raise OperadorError("RequisitoInscripcionService no configurado")
        return self._requisito_service.listar_pendientes(operador_id)

    def obtener_requisitos_pendientes(self, operador_id: int) -> list["RequisitoInscripcionOut"]:
        """Alias de :meth:`listar_requisitos_pendientes` (API antigua)."""
        return self.listar_requisitos_pendientes(operador_id)

    def actualizar_requisito(self, operador_id: int, requisito_id: int,
                             cumplido: bool, observaciones: str | None = None) -> "RequisitoInscripcionOut":
        """Actualiza el cumplimiento de un requisito."""
        if self._requisito_service is None:
            raise OperadorError("RequisitoInscripcionService no configurado")
        return self._requisito_service.actualizar(operador_id, requisito_id, cumplido, observaciones)

    def validar_requisito_para_categoria(self, categoria: str, requisito: str) -> bool:
        """Valida que un requisito corresponda a la categoría."""
        if self._requisito_service is None:
            raise OperadorError("RequisitoInscripcionService no configurado")
        return self._requisito_service.validar_requisito_para_categoria(categoria, requisito)

    def obtener_certificado_vigente(self, operador_id: int) -> "CertificadoOut | None":
        """Obtiene el certificado vigente (delega en :class:`CertificadoService`).

        Lanza ``OperadorError`` si el operador no existe.
        """
        if self._certificado_service is None:
            raise OperadorError("CertificadoService no configurado")
        if self._dao.obtener_por_id(operador_id) is None:
            raise OperadorError(f"No existe un operador con id {operador_id}")
        return self._certificado_service.obtener_vigente(operador_id)

    def crear_certificado(self, operador_id: int, data) -> "CertificadoOut":
        """Crea un certificado (delega en :class:`CertificadoService`)."""
        if self._certificado_service is None:
            raise OperadorError("CertificadoService no configurado")
        return self._certificado_service.crear(operador_id, data)

    # ------------------------------------------------------------------
    # Personas (titulares)
    # ------------------------------------------------------------------

    def _resolver_persona(self, persona_id: int | None, cuit: str,
                          razon_social: str, tipo: str) -> int:
        """Devuelve el id de la persona titular del operador.

        Si el alta trae ``persona_id`` lo usa directamente; si no, busca la
        persona por CUIT y la crea (idempotente) con los datos del primer
        operador registrado bajo ese CUIT.
        """
        if persona_id is not None:
            return persona_id
        if cuit is None:
            raise OperadorError(
                "Se debe informar persona_id o cuit para identificar a la persona titular"
            )
        if self._persona_service is not None:
            from core.persona.schema import PersonaIn

            existente = self._persona_service.obtener_por_documento("CUIT", cuit)
            if existente is not None:
                return existente.id
            # El tipo de persona se infiere del documento: CUIT → PJ (jurídica),
            # DNI → PF (física). La constraint de BD solo acepta 'PF'/'PJ'.
            tipo_persona = "PJ" if len(cuit.replace("-", "")) >= 11 else "PF"
            creada = self._persona_service.crear_persona(
                PersonaIn(
                    tipo=tipo_persona,
                    tipo_documento="CUIT",
                    identificador=cuit,
                    nombre=razon_social,
                )
            )
            return creada.id
        raise OperadorError(
            "El operador no tiene persona titular (persona_id) y no hay PersonaService configurado"
        )

    # ------------------------------------------------------------------
    # Internos
    # ------------------------------------------------------------------

    def _crear_requisitos_iniciales(self, operador_id: int, categoria: str | None) -> None:
        """Crea los requisitos iniciales (generales + específicos) para un operador."""
        # Import tardío: evita el ciclo operador <-> requisito_inscripcion
        # (el servicio de requisitos importa OperadorError de aquí).
        from modulos.registro_operadores.requisito_inscripcion.servicio import (
            REQUISITOS_ESPECIFICOS_POR_CATEGORIA,
            REQUISITOS_GENERALES,
        )
        from modulos.registro_operadores.requisito_inscripcion.dao import (
            RequisitoInscripcion,
        )

        with self._dao._session_factory() as session:

            # Requisitos generales (comunes a todas las categorías)
            for codigo in REQUISITOS_GENERALES:
                req = RequisitoInscripcion(
                    operador_id=operador_id,
                    codigo=codigo,
                    descripcion=codigo.replace("_", " ").title(),
                    es_general=True,
                    cumplido=False,
                )
                session.add(req)

            # Requisitos específicos según categoría
            if categoria is not None:
                for codigo in REQUISITOS_ESPECIFICOS_POR_CATEGORIA.get(categoria, []):
                    req = RequisitoInscripcion(
                        operador_id=operador_id,
                        codigo=codigo,
                        descripcion=codigo.replace("_", " ").title(),
                        es_general=False,
                        cumplido=False,
                    )
                    session.add(req)

            session.commit()
