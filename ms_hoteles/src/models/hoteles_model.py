from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Numeric, Integer, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid
from datetime import datetime

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

id_gen_hotel = generate_uuid()

class ProveedorModel(Base):
    __tablename__ = "proveedores"
    __table_args__ = {'schema': 'usr_app'}

    id_proveedor = Column(UUID(as_uuid=True), primary_key=True)    
    tipo = Column(String)
    nombre = Column(String)
    descripcion = Column(String)
    email = Column(String)
    telefono = Column(String)
    direccion = Column(String)
    ciudad = Column(String)
    pais = Column(String)
    sitio_web = Column(String)
    rating_promedio = Column(Numeric)
    verificado = Column(Boolean)
    fecha_registro = Column(DateTime(timezone=True), default=datetime.utcnow)
    ubicacion = Column(String)
    redes_sociales = Column(String)
    relevancia = Column(String)
    usuario_creador = Column(String)
    tipo_documento = Column(String)
    numero_documento = Column(String)
    rnt = Column(String)
    activo = Column(Boolean, default=True)

class HotelModel(Base):
    __tablename__ = "hoteles"
    __table_args__ = {'schema': 'usr_app'}

    id_hotel = Column(UUID(as_uuid=True), ForeignKey('usr_app.proveedores.id_proveedor'), primary_key=True)
    estrellas = Column(Integer)
    numero_habitaciones = Column(Integer)
    servicios_incluidos = Column(String)
    check_in = Column(DateTime(timezone=True))
    check_out = Column(DateTime(timezone=True))
    admite_mascotas = Column(Boolean)
    tiene_estacionamiento = Column(Boolean)
    tipo_habitacion = Column(String)
    precio_ascendente = Column(Float)
    servicio_restaurante = Column(Boolean)
    recepcion_24_horas = Column(Boolean)
    bar = Column(Boolean)
    room_service = Column(Boolean)
    asensor = Column(Boolean)
    rampa_discapacitado = Column(Boolean)
    pet_friendly = Column(Boolean)
    auditorio = Column(Boolean)
    parqueadero = Column(Boolean)
    piscina = Column(Boolean)
    planta_energia = Column(Boolean)
    