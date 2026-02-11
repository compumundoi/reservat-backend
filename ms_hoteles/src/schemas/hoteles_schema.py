from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime, time
from uuid import UUID

class DatosProveedor(BaseModel):
    tipo: Optional[str] = None
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    pais: Optional[str] = None
    sitio_web: Optional[str] = None
    rating_promedio: Optional[float] = 0 
    verificado: bool = True
    fecha_registro: Optional[datetime] = None
    ubicacion: Optional[str] = None
    redes_sociales: Optional[str] = None
    relevancia: Optional[str] = None
    usuario_creador: Optional[str] = None
    tipo_documento: Optional[str] = None
    numero_documento: Optional[str] = None         
    activo: bool = True

class DatosHotel(BaseModel):
    estrellas: Optional[int] = 0
    numero_habitaciones: Optional[int] = 0
    servicios_incluidos: Optional[str] = None
    check_in: Optional[time] = None
    check_out: Optional[time] = None
    admite_mascotas: bool = False
    tiene_estacionamiento: bool = False
    tipo_habitacion: Optional[str] = None
    precio_ascendente: Optional[float] = 0.0  
    servicio_restaurante: bool = False
    recepcion_24_horas: bool = False
    bar: bool = False
    room_service: bool = False
    asensor: bool = False
    rampa_discapacitado: bool = False
    pet_friendly: bool = False
    auditorio: bool = False
    parqueadero: bool = False
    piscina: bool = False
    planta_energia: bool = False

class CrearHotelRequest(BaseModel):
    proveedor: DatosProveedor
    hotel: DatosHotel

############# listar hoteles #############

class ListarDatosProveedor(BaseModel):
    id_proveedor: UUID
    tipo: Optional[str] = None
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    pais: Optional[str] = None
    sitio_web: Optional[str] = None
    rating_promedio: Optional[float] = 0 
    verificado: bool = True
    fecha_registro: Optional[datetime] = None
    ubicacion: Optional[str] = None
    redes_sociales: Optional[str] = None
    relevancia: Optional[str] = None
    usuario_creador: Optional[str] = None
    tipo_documento: Optional[str] = None
    numero_documento: Optional[str] = None         
    activo: bool = True

class ListarDatosHotel(BaseModel):
    id_hotel: UUID
    estrellas: Optional[int] = 0
    numero_habitaciones: Optional[int] = 0
    servicios_incluidos: Optional[str] = None
    check_in: Optional[time] = None
    check_out: Optional[time] = None
    admite_mascotas: bool = False
    tiene_estacionamiento: bool = False
    tipo_habitacion: Optional[str] = None
    precio_ascendente: Optional[float] = 0.0  
    servicio_restaurante: bool = False
    recepcion_24_horas: bool = False
    bar: bool = False
    room_service: bool = False
    asensor: bool = False
    rampa_discapacitado: bool = False
    pet_friendly: bool = False
    auditorio: bool = False
    parqueadero: bool = False
    piscina: bool = False
    planta_energia: bool = False

class ListarHotelResponse(BaseModel):
    proveedor: ListarDatosProveedor
    hotel: ListarDatosHotel

class ResponseList(BaseModel):
    data: List[ListarHotelResponse]
    total: int
    page: int
    size: int

############# respuesta mensaje hotel #############

class ResponseMessage(BaseModel):
    message: str
    status: int = 200