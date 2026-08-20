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
    activo = Column(Boolean, default=True)

class ExperienciaModel(Base):
    __tablename__ = "experiencias"
    __table_args__ = {'schema': 'usr_app'}

    id_experiencia = Column(UUID(as_uuid=True), ForeignKey('usr_app.proveedores.id_proveedor'), primary_key=True)
    duracion = Column(Integer)
    dificultad = Column(String)
    idioma = Column(String)
    incluye_transporte = Column(Boolean)
    grupo_maximo = Column(Integer)
    guia_incluido = Column(Boolean)
    equipamiento_requerido = Column(String)
    punto_de_encuentro = Column(String)
    numero_rnt = Column(String)


class UsuarioModel(Base):
    """Vista minima de usr_app.usuarios.

    Solo se usa para comprobar que el email pertenece a un usuario de tipo
    proveedor antes de darle de alta un registro. El vinculo entre usuarios y
    proveedores es por email: no hay llave foranea entre las dos tablas.
    """

    __tablename__ = "usuarios"
    __table_args__ = {"schema": "usr_app"}

    id = Column(UUID(as_uuid=True), primary_key=True)
    email = Column(String, unique=True)
    tipo_usuario = Column(String)
    activo = Column(Boolean)
