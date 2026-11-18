"""Controlador (router API) de Domicilios.

Rutas ``/api/domicilios``:
- ``GET  /`` — búsqueda de domicilios por calle, localidad y/o departamento.
- ``POST /`` — creación de un domicilio nuevo.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Request

from modulos.registro_operadores.domicilio.dao import Domicilio, DomicilioDAO
from modulos.registro_operadores.domicilio.servicio import DomicilioService

router = APIRouter(prefix="/api/domicilios", tags=["domicilios"])


def _get_domicilio_service(request: Request) -> DomicilioService:
    """Obtiene el DomicilioService inyectado en el app state."""
    svc = getattr(request.app.state, "domicilio_service", None)
    if svc is None:
        raise HTTPException(status_code=500, detail="DomicilioService no disponible")
    return svc


@router.get("")
async def buscar_domicilios(
    request: Request,
    calle: str = Query("", description="Texto de búsqueda en la calle"),
    localidad: str = Query("", description="Localidad para filtrar"),
    departamento: str = Query("", description="Departamento para filtrar"),
    max: int = Query(20, description="Máximo de resultados"),
):
    """Busca domicilios existentes que coincidan con los parámetros.

    Todos los filtros son opcionales; se aplican como LIKE parcial.
    """
    svc = _get_domicilio_service(request)
    dao: DomicilioDAO = svc._dao  # type: ignore[attr-defined]

    with dao._session_factory() as session:  # type: ignore[attr-defined]
        q = session.query(Domicilio)
        if calle:
            q = q.filter(Domicilio.calle.ilike(f"%{calle}%"))
        if localidad:
            q = q.filter(Domicilio.localidad.ilike(f"%{localidad}%"))
        if departamento:
            q = q.filter(Domicilio.departamento.ilike(f"%{departamento}%"))
        resultados = q.limit(max).all()

    return [
        {
            "id": d.id,
            "calle": d.calle,
            "numero": d.numero,
            "localidad": d.localidad,
            "departamento": d.departamento,
            "provincia": d.provincia,
            "codigo_postal": d.codigo_postal,
        }
        for d in resultados
    ]


@router.post("")
async def crear_domicilio(
    request: Request,
    calle: str = Query(..., description="Nombre de la calle"),
    numero: str | None = Query(None, description="Número de la calle"),
    localidad: str = Query(..., description="Localidad"),
    departamento: str = Query(..., description="Departamento provincial"),
    provincia: str = Query("Santiago del Estero", description="Provincia"),
    codigo_postal: str | None = Query(None, description="Código postal"),
):
    """Crea un domicilio nuevo y devuelve la entidad persistida."""
    svc = _get_domicilio_service(request)
    dom = svc.crear(
        calle=calle,
        numero=numero,
        localidad=localidad,
        departamento=departamento,
        provincia=provincia,
        codigo_postal=codigo_postal,
    )
    return {
        "id": dom.id,
        "calle": dom.calle,
        "numero": dom.numero,
        "localidad": dom.localidad,
        "departamento": dom.departamento,
        "provincia": dom.provincia,
        "codigo_postal": dom.codigo_postal,
    }
