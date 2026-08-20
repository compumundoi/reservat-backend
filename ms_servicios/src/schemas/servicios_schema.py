from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from uuid import UUID

# Los servicios se registran unicamente en pesos colombianos. Los registros
# historicos en otra moneda se siguen leyendo y editando sin problema; lo que
# no se permite es crear uno nuevo fuera de esta.
MONEDA_UNICA = "COP"


class DatosServicio(BaseModel):
    proveedor_id: UUID
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    tipo_servicio: Optional[str] = None
    precio: float
    moneda: Optional[str] = MONEDA_UNICA
    activo: bool = True
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)
    fecha_actualizacion: Optional[datetime] = None
    relevancia: Optional[str] = None
    ciudad: Optional[str] = None
    departamento: Optional[str] = None
    ubicacion: Optional[str] = None
    detalles_del_servicio: Optional[str] = None
    
class CrearServicio(DatosServicio):
    """Payload de alta. Solo aqui se exige la moneda unica.

    El validador NO puede vivir en DatosServicio: RespuestaServicio hereda
    de el, asi que tambien correria al LEER y haria fallar el listado de los
    servicios historicos guardados en otra moneda.
    """

    @field_validator("moneda")
    @classmethod
    def validar_moneda(cls, v: Optional[str]) -> str:
        if v is None or v.strip() == "":
            return MONEDA_UNICA
        if v.strip().upper() != MONEDA_UNICA:
            raise ValueError(f"los servicios solo se registran en {MONEDA_UNICA}")
        return MONEDA_UNICA


class ActualizarServicio(BaseModel):
    id_servicio: UUID
    proveedor_id: UUID
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    tipo_servicio: Optional[str] = None
    precio: Optional[float] = None
    moneda: Optional[str] = None
    activo: Optional[bool] = None
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None
    relevancia: Optional[str] = None
    ciudad: Optional[str] = None
    departamento: Optional[str] = None
    ubicacion: Optional[str] = None
    detalles_del_servicio: Optional[str] = None

class RespuestaServicio(DatosServicio):
    id_servicio: UUID
    # Datos del proveedor dueño del servicio. Quedan vacíos si el proveedor
    # ya no existe, para que el servicio siga apareciendo en el listado.
    proveedor_nombre: Optional[str] = None
    proveedor_email: Optional[str] = None

    class Config:
        from_attributes = True

class ResponseMessage(BaseModel):
    message: str
    status: int = 200

class ResponseList(BaseModel):
    servicios: List[RespuestaServicio]
    total: int
    page: int
    size: int

class ServicioBusqueda(BaseModel):
    id_servicio: UUID
    nombre: Optional[str] = None

    class Config:
        from_attributes = True

class ResponseBusquedaServicios(BaseModel):
    servicios: List[ServicioBusqueda]
    total: int
    page: int
    size: int