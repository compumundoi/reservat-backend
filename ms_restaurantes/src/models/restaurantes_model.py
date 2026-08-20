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
    # Ubicacion: los *_id son la fuente de verdad, el texto se deriva de ellos.
    ciudad = Column(String)
    departamento = Column(String)
    pais = Column(String)
    pais_id = Column(Integer)
    departamento_id = Column(Integer)
    municipio_id = Column(Integer)
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

class restauranteModel(Base):
    __tablename__ = "restaurantes"
    __table_args__ = {'schema': 'usr_app'}

    id_restaurante = Column(UUID(as_uuid=True), ForeignKey('usr_app.proveedores.id_proveedor'), primary_key=True)
    tipo_cocina = Column(String)
    horario_apertura = Column(DateTime(timezone=True))
    horario_cierre = Column(DateTime(timezone=True))
    capacidad = Column(Integer)
    menu_url = Column(String)
    tiene_terraza = Column(Boolean)
    apto_celiacos = Column(Boolean)
    apto_vegetarianos = Column(Boolean)
    reservas_requeridas = Column(Boolean)
    entrega_a_domicilio = Column(Boolean)
    wifi = Column(Boolean)
    zonas_comunes = Column(Boolean)
    auditorio = Column(Boolean)
    pet_friendly = Column(Boolean)
    eventos = Column(Boolean)
    menu_vegana = Column(Boolean)
    bufete = Column(Boolean)
    catering = Column(Boolean)
    menu_infantil = Column(Boolean)
    parqueadero = Column(Boolean)
    terraza = Column(Boolean)
    sillas_bebe = Column(Boolean)
    decoraciones_fechas_especiales = Column(Boolean)
    rampa_discapacitados = Column(Boolean)
    aforo_maximo = Column(Integer)
    tipo_comida = Column(String)
    precio_ascendente = Column(Integer)


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
