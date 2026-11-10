"""Servicio de negocio del Módulo I — Registro Provincial de Operadores.

Casos de uso:
- Dar de alta un operador.
- Buscar por CUIT.
- Listar operadores (con filtros).
- Cambiar el estado registral.
- Agregar habilitaciones, inscripciones y domicilios operativos.
- Gestionar requisitos de inscripción (generales y específicos por categoría).

NOTA: la "jerarquía" de personas y sucursales NO tiene endpoint propio —
el frontend reutiliza `listar` (GET /registro-operadores) y agrupa los
operadores por CUIT de la persona titular en el cliente
(PaginaJerarquia.tsx).
"""

from __future__ import annotations

from datetime import datetime, timezone

from core.persona.schema import PersonaIn
from core.persona.servicio import PersonaService
from modulos.registro_operadores.adjunto_dao import AdjuntoOperador, AdjuntoOperadorDAO
from modulos.registro_operadores.dao import (
    ActividadEconomica,
    Certificado,
    DomicilioOperativo,
    GrupoActividad,
    Habilitacion,
    Inscripcion,
    RequisitoInscripcion,
    ROCCAOperador,
    ROCCAOperadorDAO,
    SubgrupoActividad,
)
from core.storage.insforge import InsforgeStorage
from modulos.registro_operadores.enums import (
    CategoriaOperador,
    EstadoCertificado,
    EstadoRegistral,
    RequisitoAdjuntoPersona,
    RequisitoEspecifico,
    RequisitoGeneralOperador,
)
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
    RequisitoInscripcionIn,
    RequisitoInscripcionOut,
    ROCCAOperadorIn,
    ROCCAOperadorOut,
    SubgrupoActividadOut,
)


class ROCCAOperadorError(Exception):
    """Error de negocio del servicio de operadores."""


# ---------------------------------------------------------------------------
# Matriz de requisitos específicos por categoría (según especificación)
# ---------------------------------------------------------------------------

# Adjuntos de persona (compartidos entre todos sus operadores)
REQUISITOS_ADJUNTO_PERSONA: list[str] = [
    RequisitoAdjuntoPersona.DNI_FRENTE.value,
    RequisitoAdjuntoPersona.DNI_DORSO.value,
    RequisitoAdjuntoPersona.CUIT.value,
    RequisitoAdjuntoPersona.IIBB.value,
]

# Requisitos generales de operador (comunes a todas las categorías)
REQUISITOS_GENERALES: list[str] = [
    RequisitoGeneralOperador.AFIP_ULTIMO_PAGO.value,
    RequisitoGeneralOperador.REGIMEN_PROVISIONAL.value,
]

# Matriz de requisitos específicos por categoría (según especificación)
REQUISITOS_ESPECIFICOS_POR_CATEGORIA: dict[str, list[str]] = {
    CategoriaOperador.SALA_DE_DESPOSTE.value: [
        RequisitoEspecifico.FORMULARIO_101.value,
        RequisitoEspecifico.HABILITACION_MUNICIPAL.value,
        RequisitoEspecifico.MEMORIA_CONSTRUCTIVA.value,
        RequisitoEspecifico.MEMORIA_OPERATIVA.value,
        RequisitoEspecifico.CERTIFICADO_EFLUENTES.value,
    ],
    CategoriaOperador.CAMARAS_FRIGORIFICAS.value: [
        RequisitoEspecifico.FORMULARIO_101.value,
        RequisitoEspecifico.HABILITACION_MUNICIPAL.value,
        RequisitoEspecifico.PLANO_CAMARA.value,
        RequisitoEspecifico.MATRICULA_RUCA.value,
        RequisitoEspecifico.USUARIO_FAENADOR.value,
        RequisitoEspecifico.DOMINIO_CAMARA.value,
        RequisitoEspecifico.HABILITACION_SANITARIA_CAMARA.value,
    ],
    CategoriaOperador.FABRICA_DE_CHACINADOS.value: [
        RequisitoEspecifico.HABILITACION_MUNICIPAL.value,
        RequisitoEspecifico.LIBRETA_SANITARIA.value,
        RequisitoEspecifico.MEMORIA_OPERATIVA.value,
        RequisitoEspecifico.PLANOS_OBRA.value,
        RequisitoEspecifico.MEMORIA_EDILICIA.value,
        RequisitoEspecifico.TASA_FOJAS.value,
        RequisitoEspecifico.PERMISO_VUELCO_EFLUENTES.value,
        RequisitoEspecifico.ACTA_CONSTITUCION.value,
        RequisitoEspecifico.DOMINIO_ESTABLECIMIENTO.value,
        RequisitoEspecifico.DDJJ_VOLUMEN.value,
        RequisitoEspecifico.LIBRO_ACTAS.value,
        RequisitoEspecifico.INSCRIPCION_BROMATOLOGIA.value,
    ],
    CategoriaOperador.CARNICERIAS.value: [
        RequisitoEspecifico.FORMULARIO_101.value,
        RequisitoEspecifico.HABILITACION_MUNICIPAL.value,
        RequisitoEspecifico.LIBRETA_SANITARIA.value,
    ],
    CategoriaOperador.CARNICERIA_CON_CAMARA.value: [
        RequisitoEspecifico.FORMULARIO_101.value,
        RequisitoEspecifico.HABILITACION_MUNICIPAL.value,
        RequisitoEspecifico.LIBRETA_SANITARIA.value,
        RequisitoEspecifico.PLANO_CAMARA.value,
        RequisitoEspecifico.MATRICULA_RUCA.value,
        RequisitoEspecifico.USUARIO_FAENADOR.value,
        RequisitoEspecifico.DOMINIO_CAMARA.value,
        RequisitoEspecifico.HABILITACION_SANITARIA_CAMARA.value,
    ],
    # Transportista, Supermercado y Distribuidor: pendientes de definir
    CategoriaOperador.TRANSPONEDOR.value: [],
    CategoriaOperador.SUPERMERCADO.value: [],
    CategoriaOperador.DISTRIBUIDOR.value: [],
}


class ROCCAOperadorService:
    """Servicio de negocio de operadores de la cadena cárnica."""

    def __init__(self, dao: ROCCAOperadorDAO, persona_service: PersonaService | None = None,
                 adjunto_dao: AdjuntoOperadorDAO | None = None,
                 storage: InsforgeStorage | None = None) -> None:
        self._dao = dao
        self._persona_service = persona_service
        self._adjunto_dao = adjunto_dao
        self._storage = storage

    # ------------------------------------------------------------------
    # Operadores
    # ------------------------------------------------------------------

    def crear_operador(self, data: ROCCAOperadorIn) -> ROCCAOperadorOut:
        """Da de alta un operador y devuelve su representación de salida.

        Si el alta no trae ``persona_id``, se crea la persona titular con el
        CUIT del operador (1 persona : N sucursales).
        """
        existente = self._dao.obtener_por_cuit(data.cuit)
        if existente is not None:
            raise ROCCAOperadorError(f"Ya existe un operador con CUIT {data.cuit}")

        # ``operadores.persona_id`` es NOT NULL: si el alta no trae la persona
        # titular, la creamos con los datos del propio operador (idempotente
        # por CUIT).
        persona_id = self._resolver_persona(data.persona_id, data.cuit, data.razon_social, data.tipo)

        # Validar categoría si se proporciona
        if data.categoria is not None:
            categorias_validas = [c.value for c in CategoriaOperador]
            if data.categoria not in categorias_validas:
                raise ROCCAOperadorError(
                    f"Categoría inválida: {data.categoria}. "
                    f"Categorías válidas: {', '.join(categorias_validas)}"
                )

        operador = self._dao.crear(
            cuit=data.cuit,
            razon_social=data.razon_social,
            tipo=data.tipo,
            persona_id=persona_id,
            domicilio_comercial=data.domicilio_comercial,
            telefono=data.telefono,
            email=data.email,
            categoria=data.categoria,
        )

        # Crear los requisitos (generales + específicos) con estado "no cumplido"
        self._crear_requisitos_iniciales(operador.id, data.categoria)

        return ROCCAOperadorOut.model_validate(operador)

    def obtener_por_cuit(self, cuit: str) -> ROCCAOperadorOut | None:
        """Busca un operador por su CUIT."""
        operador = self._dao.obtener_por_cuit(cuit)
        return ROCCAOperadorOut.model_validate(operador) if operador else None

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
        if self._persona_service is not None:
            existente = self._persona_service.obtener_por_documento("CUIT", cuit)
            if existente is not None:
                return existente.id
            creada = self._persona_service.crear_persona(
                PersonaIn(
                    tipo=tipo if tipo in ("FISICA", "JURIDICA") else "JURIDICA",
                    tipo_documento="CUIT",
                    identificador=cuit,
                    nombre=razon_social,
                )
            )
            return creada.id
        raise ROCCAOperadorError(
            "El operador no tiene persona titular (persona_id) y no hay PersonaService configurado"
        )

    def obtener(self, operador_id: int) -> ROCCAOperadorOut | None:
        """Busca un operador por su id."""
        with self._dao._session_factory() as session:
            operador = session.get(ROCCAOperador, operador_id)
            if operador is None:
                return None
            session.refresh(operador)
            return ROCCAOperadorOut.model_validate(operador)

    def listar(self, tipo: str | None = None,
               estado_registral: str | None = None,
               categoria: str | None = None) -> list[ROCCAOperadorOut]:
        """Lista operadores, opcionalmente filtrados por tipo, estado y categoría."""
        operadores = self._dao.listar(tipo=tipo, estado_registral=estado_registral, categoria=categoria)
        return [ROCCAOperadorOut.model_validate(op) for op in operadores]

    def cambiar_estado(self, operador_id: int, estado: EstadoRegistral) -> ROCCAOperadorOut:
        """Cambia el estado registral de un operador."""
        operador = self._dao.actualizar_estado(operador_id, estado)
        if operador is None:
            raise ROCCAOperadorError(f"No existe un operador con id {operador_id}")
        return ROCCAOperadorOut.model_validate(operador)

    # ------------------------------------------------------------------
    # Habilitaciones
    # ------------------------------------------------------------------

    def agregar_habilitacion(self, operador_id: int, data: HabilitacionIn) -> HabilitacionOut:
        """Agrega una habilitación a un operador."""
        with self._dao._session_factory() as session:
            operador = session.get(ROCCAOperador, operador_id)
            if operador is None:
                raise ROCCAOperadorError(f"No existe un operador con id {operador_id}")
            habilitacion = Habilitacion(
                operador_id=operador_id,
                actividad=data.actividad,
                fecha_habilitacion=datetime.now(timezone.utc),
                fecha_vencimiento=data.fecha_vencimiento,
            )
            session.add(habilitacion)
            session.commit()
            session.refresh(habilitacion)
            return HabilitacionOut.model_validate(habilitacion)

    def listar_habilitaciones(self, operador_id: int) -> list[HabilitacionOut]:
        """Lista las habilitaciones de un operador."""
        with self._dao._session_factory() as session:
            habilitaciones = (
                session.query(Habilitacion)
                .filter_by(operador_id=operador_id)
                .all()
            )
            return [HabilitacionOut.model_validate(h) for h in habilitaciones]

    # ------------------------------------------------------------------
    # Inscripciones
    # ------------------------------------------------------------------

    def agregar_inscripcion(self, operador_id: int, data: InscripcionIn) -> InscripcionOut:
        """Agrega una inscripción a un operador."""
        with self._dao._session_factory() as session:
            operador = session.get(ROCCAOperador, operador_id)
            if operador is None:
                raise ROCCAOperadorError(f"No existe un operador con id {operador_id}")
            inscripcion = Inscripcion(
                operador_id=operador_id,
                tipo=data.tipo,
                fecha_inscripcion=datetime.now(timezone.utc),
                numero_inscripcion=data.numero_inscripcion,
            )
            session.add(inscripcion)
            session.commit()
            session.refresh(inscripcion)
            return InscripcionOut.model_validate(inscripcion)

    def listar_inscripciones(self, operador_id: int) -> list[InscripcionOut]:
        """Lista las inscripciones de un operador."""
        with self._dao._session_factory() as session:
            inscripciones = (
                session.query(Inscripcion)
                .filter_by(operador_id=operador_id)
                .all()
            )
            return [InscripcionOut.model_validate(i) for i in inscripciones]

    # ------------------------------------------------------------------
    # Domicilios operativos
    # ------------------------------------------------------------------

    def agregar_domicilio_operativo(self, operador_id: int, data: DomicilioOperativoIn) -> DomicilioOperativoOut:
        """Agrega un domicilio operativo a un operador."""
        with self._dao._session_factory() as session:
            operador = session.get(ROCCAOperador, operador_id)
            if operador is None:
                raise ROCCAOperadorError(f"No existe un operador con id {operador_id}")
            domicilio = DomicilioOperativo(
                operador_id=operador_id,
                direccion=data.direccion,
                localidad=data.localidad,
                provincia=data.provincia,
                codigo_postal=data.codigo_postal,
                es_principal=data.es_principal,
            )
            session.add(domicilio)
            session.commit()
            session.refresh(domicilio)
            return DomicilioOperativoOut.model_validate(domicilio)

    def listar_domicilios_operativos(self, operador_id: int) -> list[DomicilioOperativoOut]:
        """Lista los domicilios operativos de un operador."""
        with self._dao._session_factory() as session:
            domicilios = (
                session.query(DomicilioOperativo)
                .filter_by(operador_id=operador_id)
                .all()
            )
            return [DomicilioOperativoOut.model_validate(d) for d in domicilios]

    # ------------------------------------------------------------------
    # Requisitos de inscripción
    # ------------------------------------------------------------------

    def listar_requisitos(self, operador_id: int) -> list[RequisitoInscripcionOut]:
        """Lista los requisitos de inscripción de un operador."""
        requisitos = self._dao.listar_requisitos(operador_id)
        return [RequisitoInscripcionOut.model_validate(r) for r in requisitos]

    def actualizar_requisito(self, operador_id: int, requisito_id: int,
                             cumplido: bool, observaciones: str | None = None) -> RequisitoInscripcionOut:
        """Actualiza el estado de cumplimiento de un requisito."""
        with self._dao._session_factory() as session:
            requisito = session.get(RequisitoInscripcion, requisito_id)
            if requisito is None or requisito.operador_id != operador_id:
                raise ROCCAOperadorError(f"No existe el requisito {requisito_id} para el operador {operador_id}")
            requisito.cumplido = cumplido
            if observaciones is not None:
                requisito.observaciones = observaciones
            if cumplido:
                requisito.fecha_cumplimiento = datetime.now(timezone.utc)
            else:
                requisito.fecha_cumplimiento = None
            session.commit()
            session.refresh(requisito)
            return RequisitoInscripcionOut.model_validate(requisito)

    def obtener_requisitos_pendientes(self, operador_id: int) -> list[RequisitoInscripcionOut]:
        """Lista los requisitos aún no cumplidos de un operador."""
        requisitos = self._dao.listar_requisitos(operador_id)
        pendientes = [r for r in requisitos if not r.cumplido]
        return [RequisitoInscripcionOut.model_validate(r) for r in pendientes]

    def obtener_requisitos_especificos_por_categoria(self, categoria: str) -> list[str]:
        """Devuelve los códigos de requisitos específicos para una categoría."""
        return REQUISITOS_ESPECIFICOS_POR_CATEGORIA.get(categoria, [])

    def requisitos_para_categoria(self, categoria: str) -> list[str]:
        """Devuelve todos los requisitos de adjunto (generales + específicos) para una categoría."""
        return REQUISITOS_GENERALES + REQUISITOS_ESPECIFICOS_POR_CATEGORIA.get(categoria, [])

    def validar_requisito_para_categoria(self, categoria: str, requisito: str) -> bool:
        """Valida que un requisito corresponda a la categoría del operador."""
        validos = self.requisitos_para_categoria(categoria)
        return requisito in validos

    # ------------------------------------------------------------------
    # Catálogo de actividades económicas
    # ------------------------------------------------------------------

    def listar_grupos(self) -> list[GrupoActividadOut]:
        """Lista los grupos de actividades económicas."""
        with self._dao._session_factory() as session:
            grupos = session.query(GrupoActividad).order_by(GrupoActividad.codigo).all()
            return [GrupoActividadOut.model_validate(g) for g in grupos]

    def listar_subgrupos(self, grupo: str | None = None) -> list[SubgrupoActividadOut]:
        """Lista los subgrupos, opcionalmente filtrados por grupo (código)."""
        with self._dao._session_factory() as session:
            q = session.query(SubgrupoActividad)
            if grupo:
                g = session.query(GrupoActividad).filter_by(codigo=grupo).first()
                if g:
                    q = q.filter_by(grupo_id=g.id)
            subgrupos = q.order_by(SubgrupoActividad.codigo).all()
            return [SubgrupoActividadOut.model_validate(s) for s in subgrupos]

    def listar_actividades(
        self, grupo: str | None = None, subgrupo: str | None = None
    ) -> list[ActividadEconomicaOut]:
        """Lista las actividades económicas, opcionalmente filtradas por grupo/subgrupo (código)."""
        with self._dao._session_factory() as session:
            q = session.query(ActividadEconomica)
            if grupo:
                g = session.query(GrupoActividad).filter_by(codigo=grupo).first()
                if g:
                    q = q.filter_by(grupo_id=g.id)
            if subgrupo:
                # Find subgrupo by codigo (within the grupo if specified)
                sq = session.query(SubgrupoActividad).filter_by(codigo=subgrupo)
                if grupo:
                    g = session.query(GrupoActividad).filter_by(codigo=grupo).first()
                    if g:
                        sq = sq.filter_by(grupo_id=g.id)
                sg = sq.first()
                if sg:
                    q = q.filter_by(subgrupo_id=sg.id)
            actividades = q.order_by(ActividadEconomica.codigo).all()
            return [ActividadEconomicaOut.model_validate(a) for a in actividades]

    # ------------------------------------------------------------------
    # Certificados
    # ------------------------------------------------------------------

    def obtener_certificado_vigente(self, operador_id: int) -> CertificadoOut | None:
        """Devuelve el único certificado válido del operador.

        Regla: entre los certificados que NO están RELEVADO, elige el de
        máxima fecha_vencimiento (NULL = sin vencimiento, se trata como
        infinito). Desempate: máxima fecha_emision.

        Si no existe ninguno → None.
        """
        from datetime import datetime as dt, timezone as tz

        with self._dao._session_factory() as session:
            operador = session.get(ROCCAOperador, operador_id)
            if operador is None:
                raise ROCCAOperadorError(f"No existe un operador con id {operador_id}")

            certs = (
                session.query(Certificado)
                .filter(
                    Certificado.operador_id == operador_id,
                    Certificado.estado != EstadoCertificado.RELEVADO.value,
                )
                .all()
            )
            if not certs:
                return None

            # Elegir: max fecha_vencimiento (None = ∞), desempate max fecha_emision
            def _sort_key(c: Certificado):
                venc = c.fecha_vencimiento
                # None (sin vencimiento) se trata como infinito → usar un datetime lejano
                if venc is None:
                    venc = dt.max.replace(tzinfo=tz.utc)
                elif venc.tzinfo is None:
                    venc = venc.replace(tzinfo=tz.utc)
                emision = c.fecha_emision
                if emision.tzinfo is None:
                    emision = emision.replace(tzinfo=tz.utc)
                return (venc, emision)

            vigente = max(certs, key=_sort_key)
            return CertificadoOut.from_certificado(vigente)

    def listar_certificados(self, operador_id: int) -> list[CertificadoOut]:
        """Lista los certificados de un operador (con estado efectivo calculado)."""
        with self._dao._session_factory() as session:
            operador = session.get(ROCCAOperador, operador_id)
            if operador is None:
                raise ROCCAOperadorError(f"No existe un operador con id {operador_id}")
            certs = (
                session.query(Certificado)
                .filter_by(operador_id=operador_id)
                .order_by(Certificado.fecha_emision.desc())
                .all()
            )
            return [CertificadoOut.from_certificado(c) for c in certs]

    def obtener_certificado(self, operador_id: int, certificado_id: int) -> CertificadoOut:
        """Obtiene un certificado específico (con estado efectivo calculado)."""
        with self._dao._session_factory() as session:
            cert = session.get(Certificado, certificado_id)
            if cert is None or cert.operador_id != operador_id:
                raise ROCCAOperadorError(f"No existe el certificado {operador_id}/{certificado_id}")
            return CertificadoOut.from_certificado(cert)

    def suspender_certificado(self, operador_id: int, certificado_id: int,
                              data: CertificadoSuspenderIn) -> CertificadoOut:
        """Suspende un certificado (acción de supervisor).

        Solo se puede suspender un certificado en estado ACTIVO.
        """
        with self._dao._session_factory() as session:
            cert = session.get(Certificado, certificado_id)
            if cert is None or cert.operador_id != operador_id:
                raise ROCCAOperadorError(f"No existe el certificado {operador_id}/{certificado_id}")
            if cert.estado != EstadoCertificado.ACTIVO.value:
                raise ROCCAOperadorError(
                    f"No se puede suspender un certificado en estado {cert.estado}"
                )
            cert.estado = EstadoCertificado.SUSPENDIDO.value
            if data.observaciones:
                cert.observaciones = (cert.observaciones or "") + f" | Suspendido: {data.observaciones}"
            session.commit()
            session.refresh(cert)
            return CertificadoOut.from_certificado(cert)

    def reactivar_certificado(self, operador_id: int, certificado_id: int,
                              data: CertificadoSuspenderIn | None = None) -> CertificadoOut:
        """Reactiva un certificado suspendido (acción de supervisor).

        Solo se puede reactivar un certificado en estado SUSPENDIDO.
        """
        with self._dao._session_factory() as session:
            cert = session.get(Certificado, certificado_id)
            if cert is None or cert.operador_id != operador_id:
                raise ROCCAOperadorError(f"No existe el certificado {operador_id}/{certificado_id}")
            if cert.estado != EstadoCertificado.SUSPENDIDO.value:
                raise ROCCAOperadorError(
                    f"No se puede reactivar un certificado en estado {cert.estado}"
                )
            cert.estado = EstadoCertificado.ACTIVO.value
            session.commit()
            session.refresh(cert)
            return CertificadoOut.from_certificado(cert)

    def crear_certificado(self, operador_id: int, data: CertificadoIn) -> CertificadoOut:
        """Crea un certificado para un operador.

        Regla de relevación: si existe un certificado ACTIVO cuya fecha_vencimiento
        es posterior a la fecha_emision del nuevo certificado, el certificado
        anterior pasa a estado RELEVADO.
        """
        with self._dao._session_factory() as session:
            operador = session.get(ROCCAOperador, operador_id)
            if operador is None:
                raise ROCCAOperadorError(f"No existe un operador con id {operador_id}")

            # --- Regla de relevación ---
            # Buscar certificados ACTIVO del mismo operador que estén vigentes
            # en la fecha de emisión del nuevo certificado.
            activos = (
                session.query(Certificado)
                .filter(
                    Certificado.operador_id == operador_id,
                    Certificado.estado == EstadoCertificado.ACTIVO.value,
                )
                .all()
            )
            for cert_ant in activos:
                # El certificado anterior es relevante si su vencimiento es
                # posterior a la emisión del nuevo (es decir, el nuevo se emite
                # mientras el anterior aún estaba vigente).
                if cert_ant.fecha_vencimiento is not None:
                    venc = cert_ant.fecha_vencimiento
                    emision = data.fecha_emision
                    # Normalizar a aware UTC para la comparación
                    if venc.tzinfo is None:
                        venc = venc.replace(tzinfo=timezone.utc)
                    if emision.tzinfo is None:
                        emision = emision.replace(tzinfo=timezone.utc)
                    if venc > emision:
                        cert_ant.estado = EstadoCertificado.RELEVADO.value

            # --- Crear el nuevo certificado ---
            cert = Certificado(
                operador_id=operador_id,
                numero_certificado=data.numero_certificado,
                tipo_certificado=data.tipo_certificado,
                fecha_emision=data.fecha_emision,
                fecha_vencimiento=data.fecha_vencimiento,
                actividades_economicas=data.actividades_economicas,
                observaciones=data.observaciones,
            )
            session.add(cert)
            session.commit()
            session.refresh(cert)
            return CertificadoOut.from_certificado(cert)

    # ------------------------------------------------------------------
    # Internos
    # ------------------------------------------------------------------

    def _crear_requisitos_iniciales(self, operador_id: int, categoria: str | None) -> None:
        """Crea los requisitos iniciales (generales + específicos) para un operador."""
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

    # ------------------------------------------------------------------
    # Adjuntos de operador
    # ------------------------------------------------------------------

    async def subir_adjunto_operador(
        self, operador_id: int, requisito: str, filename: str,
        content_type: str, size: int, data: bytes,
    ) -> dict:
        """Sube un adjunto a storage y registra la fila en BD."""
        if self._storage is None:
            raise ROCCAOperadorError("Storage no configurado")
        if self._adjunto_dao is None:
            raise ROCCAOperadorError("DAO de adjuntos no configurado")

        # Verificar que el operador existe
        operador = self._dao.obtener_por_id(operador_id)
        if operador is None:
            raise ROCCAOperadorError(f"No existe un operador con id {operador_id}")

        # Validar content type
        if content_type not in ("image/jpeg", "image/png", "application/pdf"):
            raise ROCCAOperadorError(f"Tipo de archivo no permitido: {content_type}")
        # Validar tamaño
        if size > 10 * 1024 * 1024:
            raise ROCCAOperadorError("Archivo excede el tamaño máximo de 10 MB")
        # Validar que el requisito corresponda a la categoría
        categoria = operador.categoria or ""
        if not self.validar_requisito_para_categoria(categoria, requisito):
            raise ROCCAOperadorError(
                f"El requisito '{requisito}' no corresponde a la categoría '{categoria}'"
            )

        # Subir a storage
        storage_key = await self._storage.upload(filename, content_type, size, data)

        # Registrar en BD
        adjunto = self._adjunto_dao.crear(
            operador_id=operador_id,
            requisito=requisito,
            storage_key=storage_key,
            content_type=content_type,
            size=size,
            nombre_original=filename,
        )
        return self._adjunto_a_dict(adjunto)

    def listar_adjuntos_operador(self, operador_id: int) -> list[dict]:
        """Lista los adjuntos de un operador."""
        if self._adjunto_dao is None:
            return []
        adjuntos = self._adjunto_dao.listar_por_operador(operador_id)
        return [self._adjunto_a_dict(a) for a in adjuntos]

    async def obtener_url_adjunto_operador(self, operador_id: int, adjunto_id: int) -> str:
        """Obtiene una URL firmada para descargar un adjunto."""
        if self._adjunto_dao is None or self._storage is None:
            raise ROCCAOperadorError("Storage no configurado")
        adjunto = self._adjunto_dao.obtener_por_id(adjunto_id)
        if adjunto is None or adjunto.operador_id != operador_id:
            raise ROCCAOperadorError(f"No existe un adjunto {adjunto_id} para el operador {operador_id}")
        return await self._storage.download_url(adjunto.storage_key)

    async def eliminar_adjunto_operador(self, operador_id: int, adjunto_id: int) -> None:
        """Elimina un adjunto (fila + objeto en storage)."""
        if self._adjunto_dao is None:
            raise ROCCAOperadorError("DAO de adjuntos no configurado")
        adjunto = self._adjunto_dao.obtener_por_id(adjunto_id)
        if adjunto is None or adjunto.operador_id != operador_id:
            raise ROCCAOperadorError(f"No existe un adjunto {adjunto_id} para el operador {operador_id}")
        if self._storage:
            try:
                await self._storage.delete(adjunto.storage_key)
            except Exception:
                pass
        self._adjunto_dao.eliminar(adjunto_id)

    @staticmethod
    def _adjunto_a_dict(adjunto: AdjuntoOperador) -> dict:
        return {
            "id": adjunto.id,
            "operador_id": adjunto.operador_id,
            "requisito": adjunto.requisito,
            "storage_key": adjunto.storage_key,
            "content_type": adjunto.content_type,
            "size": adjunto.size,
            "nombre_original": adjunto.nombre_original,
            "creado_en": adjunto.creado_en.isoformat() if adjunto.creado_en else None,
        }
