from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class RespuestaPais(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    codigo: str


class RespuestaDepartamento(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    pais_id: int
    nombre: str
    codigo: str


class RespuestaMunicipio(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    departamento_id: int
    nombre: str
    codigo: str


class UbicacionResuelta(BaseModel):
    """Ubicacion completa a partir de un municipio.

    Es lo que consumen los demas microservicios para escribir a la vez los
    ids y el texto derivado (pais / departamento / ciudad).
    """

    pais_id: int
    pais: str
    departamento_id: int
    departamento: str
    municipio_id: int
    municipio: str


class ResponseListPaises(BaseModel):
    paises: List[RespuestaPais]
    total: int


class ResponseListDepartamentos(BaseModel):
    departamentos: List[RespuestaDepartamento]
    total: int


class ResponseListMunicipios(BaseModel):
    municipios: List[RespuestaMunicipio]
    total: int
