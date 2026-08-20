from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import sessionmaker, Session
import logging
from typing import Optional

from config.db2 import DB
from models.ubicaciones_model import PaisModel, DepartamentoModel, MunicipioModel
from schemas.ubicaciones_schema import (
    RespuestaPais,
    RespuestaDepartamento,
    RespuestaMunicipio,
    ResponseListPaises,
    ResponseListDepartamentos,
    ResponseListMunicipios,
    UbicacionResuelta,
)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

db = DB.create()
Session = sessionmaker(bind=db.engine)


def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()


ubicaciones = APIRouter()

# Colombia es el unico pais operativo hoy: los formularios lo traen fijo y el
# catalogo de departamentos/municipios solo esta cargado para el.
CODIGO_PAIS_POR_DEFECTO = "CO"


@ubicaciones.get("/ubicaciones/paises", response_model=ResponseListPaises)
async def listar_paises(db: Session = Depends(get_db)):
    """Catalogo completo de paises, ordenado por nombre."""
    filas = db.query(PaisModel).order_by(PaisModel.name).all()
    paises = [
        RespuestaPais(id=f.id, nombre=f.name, codigo=f.code) for f in filas
    ]
    return ResponseListPaises(paises=paises, total=len(paises))


@ubicaciones.get("/ubicaciones/paises/por-defecto", response_model=RespuestaPais)
async def pais_por_defecto(db: Session = Depends(get_db)):
    """Pais que los formularios dejan fijo y no editable (Colombia)."""
    fila = (
        db.query(PaisModel)
        .filter(PaisModel.code == CODIGO_PAIS_POR_DEFECTO)
        .first()
    )
    if not fila:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El pais por defecto no esta cargado en el catalogo",
        )
    return RespuestaPais(id=fila.id, nombre=fila.name, codigo=fila.code)


@ubicaciones.get("/ubicaciones/departamentos", response_model=ResponseListDepartamentos)
async def listar_departamentos(
    pais_id: Optional[int] = Query(
        None,
        description="Filtra por pais. Si se omite se usa el pais por defecto (Colombia).",
    ),
    db: Session = Depends(get_db),
):
    """Departamentos de un pais. Sin filtro devuelve los de Colombia."""
    consulta = db.query(DepartamentoModel)

    if pais_id is None:
        consulta = consulta.join(
            PaisModel, PaisModel.id == DepartamentoModel.country_id
        ).filter(PaisModel.code == CODIGO_PAIS_POR_DEFECTO)
    else:
        consulta = consulta.filter(DepartamentoModel.country_id == pais_id)

    filas = consulta.order_by(DepartamentoModel.name).all()
    departamentos = [
        RespuestaDepartamento(
            id=f.id, pais_id=f.country_id, nombre=f.name, codigo=f.code
        )
        for f in filas
    ]
    return ResponseListDepartamentos(
        departamentos=departamentos, total=len(departamentos)
    )


@ubicaciones.get("/ubicaciones/municipios", response_model=ResponseListMunicipios)
async def listar_municipios(
    departamento_id: int = Query(..., description="Departamento al que pertenecen"),
    db: Session = Depends(get_db),
):
    """Municipios de un departamento.

    El departamento es obligatorio a proposito: devolver los 1122 municipios
    del pais de una sola vez no le sirve a ningun formulario.
    """
    filas = (
        db.query(MunicipioModel)
        .filter(MunicipioModel.department_id == departamento_id)
        .order_by(MunicipioModel.name)
        .all()
    )
    municipios = [
        RespuestaMunicipio(
            id=f.id, departamento_id=f.department_id, nombre=f.name, codigo=f.code
        )
        for f in filas
    ]
    return ResponseListMunicipios(municipios=municipios, total=len(municipios))


@ubicaciones.get(
    "/ubicaciones/municipios/{municipio_id}", response_model=UbicacionResuelta
)
async def resolver_municipio(municipio_id: int, db: Session = Depends(get_db)):
    """Devuelve la ubicacion completa (pais + departamento + municipio).

    Los formularios solo mandan el id del municipio; este endpoint es lo que
    permite reconstruir el texto derivado sin duplicar el catalogo.
    """
    fila = (
        db.query(MunicipioModel, DepartamentoModel, PaisModel)
        .join(DepartamentoModel, DepartamentoModel.id == MunicipioModel.department_id)
        .join(PaisModel, PaisModel.id == DepartamentoModel.country_id)
        .filter(MunicipioModel.id == municipio_id)
        .first()
    )
    if not fila:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Municipio no encontrado",
        )

    municipio, departamento, pais = fila
    return UbicacionResuelta(
        pais_id=pais.id,
        pais=pais.name,
        departamento_id=departamento.id,
        departamento=departamento.name,
        municipio_id=municipio.id,
        municipio=municipio.name,
    )
