from typing import Optional, List
from pydantic import BaseModel, field_validator
from datetime import datetime, time
from uuid import UUID

# Tipos de documento aceptados al crear/editar. RUT quedo descontinuado:
# los registros historicos que aun lo tienen se leen sin problema, pero no
# se puede volver a grabar.
TIPOS_DOCUMENTO_VALIDOS = ("NIT", "CC", "CE")

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
    rnt: Optional[str] = None
    activo: bool = True

    @field_validator("tipo_documento")
    @classmethod
    def validar_tipo_documento(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v == "":
            return v
        if v not in TIPOS_DOCUMENTO_VALIDOS:
            raise ValueError(
                "tipo_documento invalido: se permite "
                + ", ".join(TIPOS_DOCUMENTO_VALIDOS)
            )
        return v

    @field_validator("rnt")
    @classmethod
    def validar_rnt(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if v == "":
            return None
        if not v.isdigit():
            raise ValueError("rnt debe contener solo digitos")
        if len(v) > 8:
            raise ValueError("rnt admite maximo 8 digitos")
        return v

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
    rnt: Optional[str] = None
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