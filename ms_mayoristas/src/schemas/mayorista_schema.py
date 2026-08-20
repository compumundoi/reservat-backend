from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class DatosMayorista(BaseModel):
    nombre: str
    apellidos: Optional[str] = None
    descripcion: Optional[str] = None
    email: str
    telefono: str
    direccion: str
    # El cliente solo manda municipio_id; ciudad, departamento y pais los
    # deriva el servidor desde el catalogo de ubicaciones.
    municipio_id: int
    ciudad: Optional[str] = None
    departamento: Optional[str] = None
    pais: Optional[str] = None
    pais_id: Optional[int] = None
    departamento_id: Optional[int] = None
    recurente: bool = False
    usuario_creador: Optional[str] = None
    verificado: bool = False
    intereses: Optional[str] = None
    tipo_documento: str
    numero_documento: str
    contacto_principal: Optional[str] = None
    telefono_contacto: Optional[str] = None
    email_contacto: Optional[str] = None
    comision_porcentaje: Optional[float] = 0
    limite_credito: Optional[float] = 0
    estado: Optional[str] = "activo"
    observaciones: Optional[str] = None
    activo: bool = True

class ActualizarMayorista(BaseModel):
    nombre: Optional[str] = None
    apellidos: Optional[str] = None
    descripcion: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    municipio_id: Optional[int] = None
    ciudad: Optional[str] = None
    departamento: Optional[str] = None
    pais: Optional[str] = None
    pais_id: Optional[int] = None
    departamento_id: Optional[int] = None
    recurente: Optional[bool] = None
    usuario_creador: Optional[str] = None
    verificado: Optional[bool] = None
    intereses: Optional[str] = None
    tipo_documento: Optional[str] = None
    numero_documento: Optional[str] = None
    contacto_principal: Optional[str] = None
    telefono_contacto: Optional[str] = None
    email_contacto: Optional[str] = None
    comision_porcentaje: Optional[float] = None
    limite_credito: Optional[float] = None
    estado: Optional[str] = None
    observaciones: Optional[str] = None
    activo: Optional[bool] = None


class RespuestaMayorista(DatosMayorista):
    # En lectura municipio_id puede venir nulo: hay registros historicos cuya
    # ciudad en texto libre no matcheo contra ningun municipio del catalogo.
    municipio_id: Optional[int] = None
    id: UUID
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None

    class Config:
        from_attributes = True

class ResponseMessage(BaseModel):
    message: str
    status: int = 200

class ResponseList(BaseModel):
    mayoristas: List[RespuestaMayorista]
    total: int
    page: int
    size: int