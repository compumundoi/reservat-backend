from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid
from datetime import datetime

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class Mayorista(Base):
    __tablename__ = "mayoristas"
    __table_args__ = {'schema': 'usr_app'}

    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    nombre = Column(String)
    apellidos = Column(String, nullable=True)
    descripcion = Column(String, nullable=True)
    email = Column(String, unique=True)
    telefono = Column(String)
    direccion = Column(String)
    ciudad = Column(String)
    pais = Column(String)
    recurente = Column(Boolean, default=False)
    usuario_creador = Column(String, nullable=True)
    verificado = Column(Boolean, default=False)
    intereses = Column(String, nullable=True)
    tipo_documento = Column(String)
    numero_documento = Column(String)
    contacto_principal = Column(String, nullable=True)
    telefono_contacto = Column(String, nullable=True)
    email_contacto = Column(String, nullable=True)
    comision_porcentaje = Column(Float, nullable=True)
    limite_credito = Column(Float, nullable=True)
    estado = Column(String, default="activo")
    observaciones = Column(String, nullable=True)
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
