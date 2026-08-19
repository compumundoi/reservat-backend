from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class DatosFoto(BaseModel):
    servicio_id: UUID
    url: str
    descripcion: str
    orden: int
    es_portada: bool
    fecha_subida: datetime
    eliminado: bool
    
class ActualizarFoto(BaseModel):
    servicio_id: Optional[UUID] = None
    url: Optional[str] = None
    descripcion: Optional[str] = None
    orden: Optional[int] = None
    es_portada: Optional[bool] = None
    fecha_subida: Optional[datetime] = None
    eliminado: Optional[bool] = None

class RespuestaFoto(DatosFoto):
    id: UUID
    # Nombre del servicio al que pertenece la foto. Queda vacio si el
    # servicio no se puede resolver, en vez de omitir la foto del listado.
    servicio_nombre: Optional[str] = None

    class Config:
        from_attributes = True

class ResponseMessage(BaseModel):
    message: str
    status: int = 200

class ResponseList(BaseModel):
    fotos: List[RespuestaFoto]
    total: int
    page: int
    size: int