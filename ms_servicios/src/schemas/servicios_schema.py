from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

class DatosServicio(BaseModel):
    proveedor_id: UUID
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    tipo_servicio: Optional[str] = None
    precio: float
    moneda: Optional[str] = "USD"
    activo: bool = True
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)
    fecha_actualizacion: Optional[datetime] = None
    relevancia: Optional[str] = None
    ciudad: Optional[str] = None
    departamento: Optional[str] = None
    ubicacion: Optional[str] = None
    detalles_del_servicio: Optional[str] = None
    
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