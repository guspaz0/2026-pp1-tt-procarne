"""Lógica de negocio de ``Operador``.

Casos de uso del operador (agregado raíz del módulo):
- Alta de operador (con creación idempotente de la persona titular).
- Búsqueda por CUIT / id, listado con filtros.
- Cambio de estado registral.
- Creación de los requisitos iniciales (generales + específicos por
  categoría) al dar de alta un operador.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from modulos.registro_operadores.errores import OperadorError
from modulos.registro_operadores.enums import CategoriaOperador
from modulos.registro_operadores.operador.dao import OperadorDAO
from modulos.registro_operadores.operador.dto import OperadorIn, OperadorOut


class OperadorService:
    """Servicio de negocio de operadores de la cadena cárnica."""

    def __init__(self, dao: OperadorDAO, persona_service=None,
                 certificado_service=None, catalogo_actividades_dao=None,
                 domicilio_dao=None, auth_service=None) -> None:
        self._dao = dao
        self._persona_service = persona_service
        self._domicilio_dao = domicilio_dao
        self._certificado_service = certificado_service
        self._catalogo_actividades_dao = catalogo_actividades_dao
        self._auth_service = auth_service

    # ------------------------------------------------------------------
    # Operadores
    # ------------------------------------------------------------------

    def crear_operador(self, data: OperadorIn) -> OperadorOut:
        """Da de alta un operador y devuelve su representación de salida.

        El CUIT no se guarda en ``operadores``: identifica a la persona
        titular (1 persona : N operadores, el identificador es único por
        persona). Si el alta no trae ``persona_id``, se resuelve/crea la
        persona por CUIT y el operador se vincula a ella.

        Toda la operación se ejecuta en una única transacción: si algo
        falla, se hace rollback y no quedan datos huérfanos.
        """
        from modulos.registro_operadores.domicilio.dao import Domicilio
        from modulos.registro_operadores.categoria.dao import Categoria
        from modulos.registro_operadores.asociaciones import OperadorActividad
        from modulos.registro_operadores.operador.dao import Operador
        from sqlalchemy.orm import joinedload

        session_factory = self._dao._session_factory

        with session_factory() as session:
            try:
                # 1) Resolver persona titular.
                persona_id = self._resolver_persona_tx(
                    session, data.persona_id, data.cuit, data.establecimiento_fantasia
                )

                # 2) Validar y resolver la categoría.
                categoria_id = self._resolver_categoria_tx(session, data.categoria)

                # 3) Domicilio: reutilizar existente o crear nuevo.
                domicilio_id: Optional[int] = None
                if data.domicilio is not None:
                    if data.domicilio.id is not None:
                        domicilio_id = data.domicilio.id
                    else:
                        dom = Domicilio(
                            calle=data.domicilio.calle,
                            numero=data.domicilio.numero,
                            localidad=data.domicilio.localidad,
                            departamento=data.domicilio.departamento,
                            provincia=data.domicilio.provincia or "Santiago del Estero",
                            codigo_postal=data.domicilio.codigo_postal,
                        )
                        session.add(dom)
                        session.flush()  # Obtiene el id sin commit.
                        domicilio_id = dom.id

                # 4) Actualizar email de la persona (idempotente).
                if data.email is not None:
                    from core.persona.dao import Persona
                    persona_obj = session.get(Persona, persona_id)
                    if persona_obj is not None:
                        persona_obj.email = data.email

                # 5) Crear el operador.
                op = Operador(
                    persona_id=persona_id,
                    categoria_id=categoria_id,
                    domicilio_id=domicilio_id,
                    establecimiento_fantasia=data.establecimiento_fantasia,
                    tipos_carne=data.tipos_carne,
                    telefono=data.telefono,
                    estado_registral="PENDIENTE",
                    alta_fecha=datetime.now(timezone.utc),
                )
                session.add(op)
                session.flush()  # Obtiene el id.

                # 6) Actividades económicas (N:M).
                ids: list[int] = list(data.actividad_ids or [])
                codigos: list[str] = list(data.codigo_dgr or [])
                for c in (data.codigo_afip or []):
                    if c not in codigos:
                        codigos.append(c)
                if codigos and self._catalogo_actividades_dao is not None:
                    ids.extend(self._catalogo_actividades_dao.resolver_ids_por_codigos(codigos))
                if ids:
                    # Limpia existentes y re-inserta (idempotente).
                    session.query(OperadorActividad).filter_by(operador_id=op.id).delete()
                    for aid in ids:
                        session.add(OperadorActividad(operador_id=op.id, actividad_id=aid))

                # 7) Commit único: si algo falló arriba, el `with` hace rollback.
                session.commit()

                # Recargar con joinedload para que las relaciones estén en __dict__.
                op = (
                    session.query(Operador)
                    .options(
                        joinedload(Operador.persona),
                        joinedload(Operador.categoria),
                        joinedload(Operador.domicilio),
                    )
                    .filter(Operador.id == op.id)
                    .first()
                )

            except OperadorError:
                session.rollback()
                raise
            except Exception:
                session.rollback()
                raise

        # Crear cuenta de login (fuera de la transacción: es una llamada
        # externa a InsForge que no debe bloquear el commit local).
        if data.crear_cuenta and data.email and self._auth_service is not None:
            self._crear_cuenta_persona(persona_id, data.email, data.cuit or "")

        return self._to_out(op)

    def _resolver_persona_tx(self, session, persona_id: int | None,
                             cuit: str | None, establecimiento_fantasia: str) -> int:
        """Resuelve la persona titular dentro de la transacción activa."""
        if persona_id is not None:
            return persona_id
        if cuit is None:
            raise OperadorError(
                "Se debe informar persona_id o cuit para identificar a la persona titular"
            )
        if self._persona_service is not None:
            from core.persona.schema import PersonaIn
            from core.persona.dao import Persona

            existente = session.query(Persona).filter(
                Persona.tipo_documento == "CUIT",
                Persona.identificador == cuit,
            ).first()
            if existente is not None:
                return existente.id
            tipo_persona = "PJ" if len(cuit.replace("-", "")) >= 11 else "PF"
            nueva = Persona(
                tipo=tipo_persona,
                tipo_documento="CUIT",
                identificador=cuit,
                nombre=establecimiento_fantasia,
            )
            session.add(nueva)
            session.flush()
            return nueva.id
        raise OperadorError(
            "El operador no tiene persona titular (persona_id) y no hay PersonaService configurado"
        )

    def _resolver_categoria_tx(self, session, categoria: str | None) -> int:
        """Valida y resuelve la categoría dentro de la transacción activa."""
        from modulos.registro_operadores.categoria.dao import Categoria

        if categoria is None:
            raise OperadorError(
                "Se debe informar la categoría del operador "
                f"(una de: {', '.join(c.value for c in CategoriaOperador)})"
            )
        categorias_validas = [c.value for c in CategoriaOperador]
        if categoria not in categorias_validas:
            raise OperadorError(
                f"Categoría inválida: {categoria}. "
                f"Categorías válidas: {', '.join(categorias_validas)}"
            )
        existente = session.query(Categoria).filter(Categoria.nombre == categoria).first()
        if existente is not None:
            return existente.id
        nueva = Categoria(nombre=categoria)
        session.add(nueva)
        session.flush()
        return nueva.id

    def _crear_cuenta_persona(self, persona_id: int, email: str, documento: str) -> None:
        """Crea una cuenta de login en InsForge para la persona.

        La contraseña por defecto es el número de documento (CUIT/DNI)
        sin guiones. Se marca ``must_change_password=True`` en la
        ``user_metadata`` para forzar el cambio en el primer login.

        Si el email ya tiene una cuenta, no se crea otra (idempotente).
        """
        import asyncio
        from auth.service import AuthError

        # Contraseña por defecto: documento sin guiones.
        password_defecto = "".join(ch for ch in documento if ch.isdigit())
        if len(password_defecto) < 8:
            # El documento es demasiado corto (p. ej. DNI de 7 dígitos):
            # se completa con ceros a la derecha.
            password_defecto = password_defecto.ljust(8, "0")

        async def _do_signup():
            await self._auth_service.signup(
                email, password_defecto,
                name=None,
                metadata={"persona_id": persona_id, "must_change_password": True},
            )

        try:
            # El endpoint es sync, así que creamos un loop nuevo.
            asyncio.run(_do_signup())
        except AuthError:
            # Si el email ya existe en InsForge, no es un error:
            # la persona ya tiene cuenta. Se ignora.
            pass
        except Exception:
            # No es fatal: el operador se crea igual, solo que sin cuenta de login.
            pass

    def _to_out(self, operador) -> OperadorOut:
        """Convierte un ORM a DTO resolviendo las actividades (N:M)."""
        # ``from_attributes`` solo extrae campos en ``model_fields``; la relación
        # ``persona`` no es un campo del DTO, así que se pasa explícitamente para
        # que ``_inferir_cuit`` pueda leer ``persona.identificador``.
        attrs = {k: getattr(operador, k, None) for k in OperadorOut.model_fields}
        # ``categoria`` es una relación ORM (Categoria); el DTO espera el nombre.
        categoria_obj = attrs.get("categoria")
        attrs["categoria"] = categoria_obj.nombre if categoria_obj is not None else None
        attrs["actividad_ids"] = self._dao.listar_actividad_ids(operador.id)
        # Domicilio comercial legible: se construye a partir del domicilio
        # estructurado (``operadores.domicilio_comercial`` ya no es columna).
        attrs["domicilio_comercial"] = self._dao.construir_domicilio_comercial(
            getattr(operador, "domicilio", None)
        )
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

    def listar(self, estado_registral: str | None = None,
               categoria: str | None = None) -> list[OperadorOut]:
        """Lista operadores, opcionalmente filtrados por estado y categoría."""
        operadores = self._dao.listar(estado_registral=estado_registral, categoria=categoria)
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
                          establecimiento_fantasia: str) -> int:
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
                    nombre=establecimiento_fantasia,
                )
            )
            return creada.id
        raise OperadorError(
            "El operador no tiene persona titular (persona_id) y no hay PersonaService configurado"
        )

    # ------------------------------------------------------------------
    # Internos
    # ------------------------------------------------------------------

    def _resolver_categoria(self, categoria: str | None) -> int:
        """Valida ``categoria`` (nombre) y devuelve el id de la fila en ``categorias``.

        Crea la fila de forma idempotente si no existe (el catálogo de
        categorías es cerrado y conocido).
        """
        if categoria is None:
            raise OperadorError(
                "Se debe informar la categoría del operador "
                f"(una de: {', '.join(c.value for c in CategoriaOperador)})"
            )
        categorias_validas = [c.value for c in CategoriaOperador]
        if categoria not in categorias_validas:
            raise OperadorError(
                f"Categoría inválida: {categoria}. "
                f"Categorías válidas: {', '.join(categorias_validas)}"
            )
        from modulos.registro_operadores.categoria.dao import Categoria, CategoriaDAO

        dao = CategoriaDAO(self._dao._session_factory)
        existente = dao.obtener_por_nombre(categoria)
        if existente is not None:
            return existente.id
        return dao.crear(nombre=categoria).id


