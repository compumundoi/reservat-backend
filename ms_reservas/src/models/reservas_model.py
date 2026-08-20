from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Numeric, Integer, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid
from datetime import datetime
from sqlalchemy import Date

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

# Estados validos de una reserva. Replican el CHECK
# 'reservas_estado_check' de usr_app.reservas.
ESTADO_PENDIENTE = "pendiente"
ESTADO_APROBADA = "aprobada"
ESTADO_RECHAZADA = "rechazada"

ESTADOS_VALIDOS = (ESTADO_PENDIENTE, ESTADO_APROBADA, ESTADO_RECHAZADA)

class ReservaModel(Base):
    __tablename__ = "reservas"
    __table_args__ = {'schema': 'usr_app'}

    id_reserva = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    id_proveedor = Column(UUID(as_uuid=True), nullable=False)
    id_servicio = Column(UUID(as_uuid=True), nullable=False)
    id_mayorista = Column(UUID(as_uuid=True), nullable=True)
    nombre_servicio = Column(String, nullable=False)
    descripcion = Column(String, nullable=True)
    tipo_servicio = Column(String, nullable=False)
    # En la BD 'precio' es character varying, se mapea como String
    precio = Column(String, nullable=False)
    ciudad = Column(String, nullable=False)
    # 'activo' ahora es booleano en BD
    activo = Column(Boolean, default=True)
    estado = Column(String, nullable=False, default=ESTADO_PENDIENTE)
    observaciones = Column(String, nullable=True)
    # En la BD 'fecha_creacion' es date
    fecha_creacion = Column(Date, default=datetime.utcnow)
    # La columna ahora es 'cantidad' correctamente nombrada
    cantidad = Column(Integer, nullable=False)
    # Nuevas columnas de rango de fechas
    fecha_inicio = Column(Date, nullable=True)
    fecha_fin = Column(Date, nullable=True)
    # Solo para experiencias y restaurantes: el alojamiento va por rango
    hora = Column(Time, nullable=True)
    # Decision del administrador sobre la reserva
    motivo_rechazo = Column(String, nullable=True)
    fecha_decision = Column(DateTime(timezone=True), nullable=True)
    id_admin_decision = Column(UUID(as_uuid=True), nullable=True)

class ServicioModel(Base):
    __tablename__ = "servicios"
    __table_args__ = {'schema': 'usr_app'}

    id_servicio = Column(UUID(as_uuid=True), primary_key=True)
    proveedor_id = Column(UUID(as_uuid=True), nullable=False)
    nombre = Column(String)
    descripcion = Column(String)
    tipo_servicio = Column(String)
    precio = Column(Numeric(10,2), nullable=False)
    moneda = Column(String, default='USD')
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime(timezone=True), default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime(timezone=True))
    relevancia = Column(String)
    ciudad = Column(String)
    departamento = Column(String)
    ubicacion = Column(String)
    detalles_del_servicio = Column(String)

class FechaBloqueadaModel(Base):
    __tablename__ = "fechas_bloqueadas"
    __table_args__ = {'schema': 'usr_app'}

    id = Column(UUID(as_uuid=True), primary_key=True)
    servicio_id = Column(UUID(as_uuid=True), nullable=True)
    fecha = Column(DateTime(timezone=True), nullable=False)
    motivo = Column(String)
    bloqueado_por = Column(String)
    bloqueo_activo = Column(Boolean)


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

class MayoristaModel(Base):
    __tablename__ = "mayoristas"
    __table_args__ = {'schema': 'usr_app'}

    id = Column(UUID(as_uuid=True), primary_key=True)
    nombre = Column(String)
    apellidos = Column(String)
    descripcion = Column(String)
    email = Column(String, unique=True)
    telefono = Column(String)
    direccion = Column(String)
    ciudad = Column(String)
    pais = Column(String)
    recurente = Column(Boolean)
    usuario_creador = Column(String)
    verificado = Column(Boolean)
    intereses = Column(String)
    tipo_documento = Column(String)
    numero_documento = Column(String)
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
