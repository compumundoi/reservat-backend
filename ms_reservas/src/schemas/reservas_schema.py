from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, date
from uuid import UUID

class DatosReserva(BaseModel):
    id_proveedor: UUID
    id_servicio: UUID
    id_mayorista: UUID
    nombre_servicio: str
    descripcion: str
    tipo_servicio: str
    precio: float
    ciudad: str
    activo: bool
    # 'estado' se acepta por compatibilidad con los clientes actuales pero se
    # ignora: toda reserva nace 'pendiente' por decision del servidor.
    estado: Optional[str] = None
    observaciones: str
    fecha_creacion: datetime
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    cantidad: int


class RechazarReserva(BaseModel):
    """Motivo con el que un administrador rechaza una reserva."""

    motivo_rechazo: str = Field(min_length=1, max_length=1000)
    id_admin_decision: Optional[UUID] = None

    @field_validator("motivo_rechazo")
    @classmethod
    def motivo_no_vacio(cls, valor: str) -> str:
        motivo = valor.strip()
        if not motivo:
            raise ValueError("El motivo del rechazo no puede estar vacio")
        return motivo


class AprobarReserva(BaseModel):
    """Datos opcionales con los que un administrador aprueba una reserva."""

    id_admin_decision: Optional[UUID] = None


class ActualizarReserva(BaseModel):
    id_proveedor: Optional[UUID] = None
    id_servicio: Optional[UUID] = None
    id_mayorista: Optional[UUID] = None
    nombre_servicio: Optional[str] = None
    descripcion: Optional[str] = None
    tipo_servicio: Optional[str] = None
    precio: Optional[float] = None
    ciudad: Optional[str] = None
    activo: Optional[bool] = None
    estado: Optional[str] = None
    observaciones: Optional[str] = None
    fecha_creacion: Optional[datetime] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    cantidad: Optional[int] = None

class RespuestaReserva(DatosReserva):
    id: UUID
    class Config:
        from_attributes = True

class ResponseMessage(BaseModel):
    message: str
    status: int = 200

class ResponseList(BaseModel):
    reservas: List[RespuestaReserva]
    total: int
    page: int
    size: int