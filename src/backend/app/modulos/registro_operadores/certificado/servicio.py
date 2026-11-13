"""Lógica de negocio de ``Certificado``.

Reglas de negocio:
- **Certificado vigente**: entre los certificados NO RELEVADOS, el de máxima
  fecha_vencimiento (NULL = sin vencimiento, se trata como infinito).
  Desempate: máxima fecha_emisión.
- **Relevación**: al crear un nuevo certificado, si existe uno ACTIVO cuyo
  vencimiento es posterior a la fecha de emisión del nuevo, el anterior pasa
  a estado RELEVADO.
- **Suspensión**: solo desde ACTIVO (acción de supervisor).
- **Reactivación**: solo desde SUSPENDIDO (acción de supervisor).
"""

from __future__ import annotations

from datetime import datetime, timezone

from modulos.registro_operadores.certificado.dao import Certificado, CertificadoDAO
from modulos.registro_operadores.certificado.dto import (
    CertificadoIn,
    CertificadoOut,
    CertificadoSuspenderIn,
)
from modulos.registro_operadores.enums import EstadoCertificado
from modulos.registro_operadores.operador.servicio import OperadorError


def _aware(dt: datetime | None) -> datetime | None:
    """Normaliza un datetime a aware UTC (o deja None)."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


class CertificadoService:
    """Servicio de negocio de certificados de habilitación."""

    def __init__(self, dao: CertificadoDAO) -> None:
        self._dao = dao

    def obtener_vigente(self, operador_id: int) -> CertificadoOut | None:
        """Devuelve el único certificado válido del operador.

        Regla: entre los certificados que NO están RELEVADO, elige el de
        máxima fecha_vencimiento (NULL = sin vencimiento, se trata como
        infinito). Desempate: máxima fecha_emision.

        Si no existe ninguno → None.
        """
        certs = self._dao.listar_no_relevados_por_operador(operador_id)
        if not certs:
            return None

        def _sort_key(c):
            venc = _aware(c.fecha_vencimiento)
            if venc is None:
                # Sin vencimiento se trata como infinito.
                venc = datetime.max.replace(tzinfo=timezone.utc)
            emision = _aware(c.fecha_emision) or datetime.min.replace(tzinfo=timezone.utc)
            return (venc, emision)

        vigente = max(certs, key=_sort_key)
        return self._to_out(vigente)

    def listar(self, operador_id: int) -> list[CertificadoOut]:
        """Lista los certificados de un operador (con estado efectivo calculado)."""
        certs = self._dao.listar_por_operador(operador_id)
        return [self._to_out(c) for c in certs]

    def obtener(self, operador_id: int, certificado_id: int) -> CertificadoOut:
        """Obtiene un certificado específico (con estado efectivo calculado)."""
        cert = self._dao.obtener(certificado_id)
        if cert is None or cert.operador_id != operador_id:
            raise OperadorError(f"No existe el certificado {operador_id}/{certificado_id}")
        return self._to_out(cert)

    def _to_out(self, cert) -> CertificadoOut:
        """Convierte un ORM a DTO resolviendo las actividades (N:M)."""
        return CertificadoOut.from_certificado(
            cert, actividad_ids=self._dao.listar_actividad_ids(cert.id)
        )

    def suspender(self, operador_id: int, certificado_id: int | None = None,
                  data: CertificadoSuspenderIn | None = None) -> CertificadoOut:
        """Suspende el certificado vigente del operador (acción de supervisor).

        Si ``certificado_id`` es ``None``, se resuelve el certificado vigente
        (el único que puede estar ACTIVO). Solo se puede suspender un
        certificado en estado ACTIVO.
        """
        if certificado_id is None:
            vigente = self.obtener_vigente(operador_id)
            if vigente is None:
                raise OperadorError("El operador no tiene un certificado vigente")
            certificado_id = vigente.id
        cert = self._dao.obtener(certificado_id)
        if cert is None or cert.operador_id != operador_id:
            raise OperadorError(f"No existe el certificado {operador_id}/{certificado_id}")
        if cert.estado != EstadoCertificado.ACTIVO.value:
            raise OperadorError(
                f"No se puede suspender un certificado en estado {cert.estado}"
            )
        with self._dao._session_factory() as session:
            session_cert = session.get(Certificado, certificado_id)
            session_cert.estado = EstadoCertificado.SUSPENDIDO.value
            if data is not None and data.observaciones:
                session_cert.observaciones = (session_cert.observaciones or "") + f" | Suspendido: {data.observaciones}"
            session.commit()
        return self.obtener(operador_id, certificado_id)

    def reactivar(self, operador_id: int, certificado_id: int | None = None,
                  data: CertificadoSuspenderIn | None = None) -> CertificadoOut:
        """Reactiva el certificado suspendido del operador (acción de supervisor).

        Si ``certificado_id`` es ``None``, se resuelve el certificado vigente
        (el único que puede estar SUSPENDIDO). Solo se puede reactivar un
        certificado en estado SUSPENDIDO.
        """
        if certificado_id is None:
            vigente = self.obtener_vigente(operador_id)
            if vigente is None:
                raise OperadorError("El operador no tiene un certificado para reactivar")
            certificado_id = vigente.id
        cert = self._dao.obtener(certificado_id)
        if cert is None or cert.operador_id != operador_id:
            raise OperadorError(f"No existe el certificado {operador_id}/{certificado_id}")
        if cert.estado != EstadoCertificado.SUSPENDIDO.value:
            raise OperadorError(
                f"No se puede reactivar un certificado en estado {cert.estado}"
            )
        with self._dao._session_factory() as session:
            session_cert = session.get(Certificado, certificado_id)
            session_cert.estado = EstadoCertificado.ACTIVO.value
            session.commit()
        return self.obtener(operador_id, certificado_id)

    def crear(self, operador_id: int, data: CertificadoIn) -> CertificadoOut:
        """Crea un certificado para un operador.

        Regla de relevación: si existe un certificado ACTIVO cuya
        fecha_vencimiento es posterior a la fecha_emision del nuevo
        certificado, el certificado anterior pasa a estado RELEVADO.
        """
        # --- Regla de relevación ---
        emision = _aware(data.fecha_emision) or datetime.now(timezone.utc)
        for cert_ant in self._dao.listar_activos_por_operador(operador_id):
            venc = _aware(cert_ant.fecha_vencimiento)
            if venc is not None and venc > emision:
                self._dao.marcar_relevado(cert_ant.id)

        # --- Crear el nuevo certificado ---
        cert = self._dao.crear(
            operador_id=operador_id,
            numero_certificado=data.numero_certificado,
            tipo_certificado=data.tipo_certificado,
            fecha_emision=data.fecha_emision,
            fecha_vencimiento=data.fecha_vencimiento,
            actividades_economicas=data.actividades_economicas,
            observaciones=data.observaciones,
            actividad_ids=data.actividad_ids,
        )
        return self._to_out(cert)
