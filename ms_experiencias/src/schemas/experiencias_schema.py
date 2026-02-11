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

class DatosExperiencia(BaseModel):
    duracion: Optional[int] = 0
    dificultad: Optional[str] = None
    idioma: Optional[str] = None
    incluye_transporte: Optional[bool] = False
    grupo_maximo: Optional[int] = 0
    guia_incluido: Optional[bool] = False
    equipamiento_requerido: Optional[str] = None
    punto_de_encuentro: Optional[str] = None
    numero_rnt: Optional[str] = None

class CrearExperienciaRequest(BaseModel):
    proveedor: DatosProveedor
    experiencia: DatosExperiencia

############# listar experiencias #############

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

class ListarDatosExperiencia(BaseModel):
    id_experiencia: UUID
    duracion: Optional[int] = 0
    dificultad: Optional[str] = None
    idioma: Optional[str] = None
    incluye_transporte: Optional[bool] = False
    grupo_maximo: Optional[int] = 0
    guia_incluido: Optional[bool] = False
    equipamiento_requerido: Optional[str] = None
    punto_de_encuentro: Optional[str] = None
    numero_rnt: Optional[str] = None

class ListarExperienciaResponse(BaseModel):
    proveedor: ListarDatosProveedor
    experiencia: ListarDatosExperiencia

class ResponseList(BaseModel):
    data: List[ListarExperienciaResponse]
    total: int
    page: int
    size: int

############# respuesta mensaje experiencia #############

class ResponseMessage(BaseModel):
    message: str
    status: int = 200