from typing import Optional, List
from pydantic import BaseModel
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
    rating_promedio: Optional[float] = 0 
    verificado: bool
    fecha_registro: datetime
    ubicacion: str
    redes_sociales: str
    relevancia: str
    usuario_creador: str
    tipo_documento: str
    numero_documento: str         
    activo: bool  

class DatosRestaurante(BaseModel):
    tipo_cocina: str
    horario_apertura: time
    horario_cierre: time
    capacidad: int
    menu_url: str
    tiene_terraza: bool
    apto_celiacos: bool
    apto_vegetarianos: bool
    reservas_requeridas: bool
    entrega_a_domicilio: bool
    wifi: bool
    zonas_comunes: bool
    auditorio: bool
    pet_friendly: bool
    eventos: bool
    menu_vegana: bool
    bufete: bool
    catering: bool
    menu_infantil: bool
    parqueadero: bool
    terraza: bool
    sillas_bebe: bool
    decoraciones_fechas_especiales: bool
    rampa_discapacitados: bool
    aforo_maximo: int
    tipo_comida: str
    precio_ascendente: int

class CrearRestauranteRequest(BaseModel):
    proveedor: DatosProveedor
    restaurante: DatosRestaurante

############# listar restaurantes #############

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
    rating_promedio: Optional[float] = 0 
    verificado: bool
    fecha_registro: datetime
    ubicacion: str
    redes_sociales: str
    relevancia: str
    usuario_creador: str
    tipo_documento: str
    numero_documento: str         
    activo: bool  

class ListarDatosRestaurante(BaseModel):
    id_restaurante: UUID
    tipo_cocina: str
    horario_apertura: time
    horario_cierre: time
    capacidad: int
    menu_url: str
    tiene_terraza: bool
    apto_celiacos: bool
    apto_vegetarianos: bool
    reservas_requeridas: bool
    entrega_a_domicilio: bool
    wifi: bool
    zonas_comunes: bool
    auditorio: bool
    pet_friendly: bool
    eventos: bool
    menu_vegana: bool
    bufete: bool
    catering: bool
    menu_infantil: bool
    parqueadero: bool
    terraza: bool
    sillas_bebe: bool
    decoraciones_fechas_especiales: bool
    rampa_discapacitados: bool
    aforo_maximo: int
    tipo_comida: str
    precio_ascendente: int
    

class ListarRestauranteResponse(BaseModel):
    proveedor: ListarDatosProveedor
    restaurante: ListarDatosRestaurante

class ResponseList(BaseModel):
    data: List[ListarRestauranteResponse]
    total: int
    page: int
    size: int

############# respuesta mensaje restaurante #############

class ResponseMessage(BaseModel):
    message: str
    status: int = 200