from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime, time
from uuid import UUID

class DatosProveedor(BaseModel):
    tipo: str
    nombre: str
    descripcion: str
    email: str
    telefono: str
    direccion: str
    ciudad: str
    pais: str
    sitio_web: str
    rating_promedio: int 
    verificado: bool
    fecha_registro: datetime
    ubicacion: str
    redes_sociales: str
    relevancia: str
    usuario_creador: str
    tipo_documento: str
    numero_documento: str         
    activo: bool  

class DatosTransporte(BaseModel):
    tipo_vehiculo: str
    modelo: str
    anio: int = Field(..., ge=1900, le=2100)
    placa: str
    capacidad: int
    aire_acondicionado: bool
    wifi: bool
    disponible: bool
    combustible: str
    seguro_vigente: bool
    fecha_mantenimiento: datetime


class CrearTransporteRequest(BaseModel):
    proveedor: DatosProveedor
    transporte: DatosTransporte

############# listar transportes #############

class ListarDatosProveedor(BaseModel):
    id_proveedor: UUID
    tipo: str
    nombre: str
    descripcion: str
    email: str
    telefono: str
    direccion: str
    ciudad: str
    pais: str
    sitio_web: str
    rating_promedio: int 
    verificado: bool
    fecha_registro: datetime
    ubicacion: str
    redes_sociales: str
    relevancia: str
    usuario_creador: str
    tipo_documento: str
    numero_documento: str         
    activo: bool  

class ListarDatosTransporte(BaseModel):
    id_transporte: UUID
    tipo_vehiculo: str
    modelo: str
    anio: int = Field(..., ge=1900, le=2100)
    placa: str
    capacidad: int
    aire_acondicionado: bool
    wifi: bool
    disponible: bool
    combustible: str
    seguro_vigente: bool
    fecha_mantenimiento: datetime
    

class ListarTransporteResponse(BaseModel):
    proveedor: ListarDatosProveedor
    transporte: ListarDatosTransporte

class ResponseList(BaseModel):
    data: List[ListarTransporteResponse]
    total: int
    page: int
    size: int

############# respuesta mensaje transporte #############

class ResponseMessage(BaseModel):
    message: str
    status: int = 200