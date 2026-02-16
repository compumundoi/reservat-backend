"""
Configuración del MCP Server para ReservaT.
Maneja la conexión a PostgreSQL y la seguridad por API Key.
Incluye modelos SQLAlchemy para todas las tablas (excepto usuarios).
"""

import os
from sqlalchemy import (
    create_engine, Column, String, DateTime, Boolean,
    Numeric, Integer, Float, Date, Time, Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# ─── Configuración de Base de Datos ──────────────────────────────────────────

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "reservat")

# ─── Seguridad ───────────────────────────────────────────────────────────────

MCP_API_KEY = os.getenv("MCP_API_KEY", "")

# ─── SQLAlchemy Engine ───────────────────────────────────────────────────────

_connection_url = URL.create(
    drivername="postgresql+psycopg2",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=int(DB_PORT),
    database=DB_NAME,
)

engine = create_engine(
    _connection_url,
    pool_size=5,
    max_overflow=2,
    pool_recycle=300,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(bind=engine)

# ─── Modelos SQLAlchemy (read-only) ─────────────────────────────────────────
# NOTA: La tabla 'usuarios' está EXCLUIDA deliberadamente por seguridad.

Base = declarative_base()


class ProveedorModel(Base):
    __tablename__ = "proveedores"
    __table_args__ = {"schema": "usr_app"}

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
    fecha_registro = Column(DateTime(timezone=True))
    ubicacion = Column(String)
    redes_sociales = Column(String)
    relevancia = Column(String)
    usuario_creador = Column(String)
    tipo_documento = Column(String)
    numero_documento = Column(String)
    activo = Column(Boolean, default=True)


class ExperienciaModel(Base):
    __tablename__ = "experiencias"
    __table_args__ = {"schema": "usr_app"}

    id_experiencia = Column(UUID(as_uuid=True), primary_key=True)
    duracion = Column(Integer)
    dificultad = Column(String)
    idioma = Column(String)
    incluye_transporte = Column(Boolean)
    grupo_maximo = Column(Integer)
    guia_incluido = Column(Boolean)
    equipamiento_requerido = Column(String)
    punto_de_encuentro = Column(String)
    numero_rnt = Column(String)


class HotelModel(Base):
    __tablename__ = "hoteles"
    __table_args__ = {"schema": "usr_app"}

    id_hotel = Column(UUID(as_uuid=True), primary_key=True)
    estrellas = Column(Integer)
    numero_habitaciones = Column(Integer)
    servicios_incluidos = Column(String)
    check_in = Column(Time)
    check_out = Column(Time)
    admite_mascotas = Column(Boolean)
    tiene_estacionamiento = Column(Boolean)
    tipo_habitacion = Column(String)
    precio_ascendente = Column(Numeric(10, 2))
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


class RestauranteModel(Base):
    __tablename__ = "restaurantes"
    __table_args__ = {"schema": "usr_app"}

    id_restaurante = Column(UUID(as_uuid=True), primary_key=True)
    tipo_cocina = Column(String)
    horario_apertura = Column(Time)
    horario_cierre = Column(Time)
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
    precio_ascendente = Column(Numeric(10, 2))


class ServicioModel(Base):
    __tablename__ = "servicios"
    __table_args__ = {"schema": "usr_app"}

    id_servicio = Column(UUID(as_uuid=True), primary_key=True)
    proveedor_id = Column(UUID(as_uuid=True))
    nombre = Column(String)
    descripcion = Column(String)
    tipo_servicio = Column(String)
    precio = Column(Numeric(10, 2))
    moneda = Column(String)
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime(timezone=True))
    fecha_actualizacion = Column(DateTime(timezone=True))
    relevancia = Column(String)
    ciudad = Column(String)
    departamento = Column(String)
    ubicacion = Column(String)
    detalles_del_servicio = Column(String)


class FotoModel(Base):
    __tablename__ = "fotos"
    __table_args__ = {"schema": "usr_app"}

    id = Column(UUID(as_uuid=True), primary_key=True)
    servicio_id = Column(UUID(as_uuid=True))
    url = Column(String)
    descripcion = Column(String)
    orden = Column(Integer)
    es_portada = Column(Boolean)
    fecha_subida = Column(DateTime(timezone=True))
    eliminado = Column(Boolean)


class RutaModel(Base):
    __tablename__ = "rutas"
    __table_args__ = {"schema": "usr_app"}

    id = Column(UUID(as_uuid=True), primary_key=True)
    nombre = Column(String)
    descripcion = Column(String)
    puntos_interes = Column(String)
    recomendada = Column(Boolean)
    origen = Column(String)
    destino = Column(String)
    precio = Column(String)
    duracion_estimada = Column(Integer)
    activo = Column(Boolean, default=True)


class ViajeModel(Base):
    __tablename__ = "viajes"
    __table_args__ = {"schema": "usr_app"}

    id = Column(UUID(as_uuid=True), primary_key=True)
    ruta_id = Column(UUID(as_uuid=True))
    fecha_inicio = Column(DateTime(timezone=True))
    fecha_fin = Column(DateTime(timezone=True))
    capacidad_total = Column(Integer)
    capacidad_disponible = Column(Integer)
    precio = Column(Numeric(10, 2))
    guia_asignado = Column(String)
    estado = Column(String)
    id_transportador = Column(UUID(as_uuid=True))
    activo = Column(Boolean, default=True)


class FechaBloqueadaModel(Base):
    __tablename__ = "fechas_bloqueadas"
    __table_args__ = {"schema": "usr_app"}

    id = Column(UUID(as_uuid=True), primary_key=True)
    servicio_id = Column(UUID(as_uuid=True))
    fecha = Column(DateTime(timezone=True))
    motivo = Column(String)
    bloqueado_por = Column(String)
    bloqueo_activo = Column(Boolean)


class TransporteModel(Base):
    __tablename__ = "transportes"
    __table_args__ = {"schema": "usr_app"}

    id_transporte = Column(UUID(as_uuid=True), primary_key=True)
    tipo_vehiculo = Column(String)
    modelo = Column(String)
    anio = Column(Integer)
    placa = Column(String)
    capacidad = Column(Integer)
    aire_acondicionado = Column(Boolean)
    wifi = Column(Boolean)
    disponible = Column(Boolean, default=True)
    combustible = Column(String)
    seguro_vigente = Column(Boolean, default=True)
    fecha_mantenimiento = Column(DateTime(timezone=True))


class MayoristaModel(Base):
    __tablename__ = "mayoristas"
    __table_args__ = {"schema": "usr_app"}

    id = Column(UUID(as_uuid=True), primary_key=True)
    nombre = Column(String)
    apellidos = Column(String)
    descripcion = Column(String)
    email = Column(String)
    telefono = Column(String)
    direccion = Column(String)
    ciudad = Column(String)
    pais = Column(String)
    recurente = Column(Boolean)
    usuario_creador = Column(String)
    verificado = Column(Boolean)
    fecha_creacion = Column(DateTime(timezone=True))
    intereses = Column(String)
    tipo_documento = Column(String)
    numero_documento = Column(String)
    contacto_principal = Column(String)
    telefono_contacto = Column(String)
    email_contacto = Column(String)
    comision_porcentaje = Column(Float)
    limite_credito = Column(Float)
    estado = Column(String)
    observaciones = Column(String)
    activo = Column(Boolean, default=True)
    fecha_actualizacion = Column(DateTime(timezone=True))


class ReservaModel(Base):
    __tablename__ = "reservas"
    __table_args__ = {"schema": "usr_app"}

    id_reserva = Column(UUID(as_uuid=True), primary_key=True)
    id_proveedor = Column(UUID(as_uuid=True))
    id_servicio = Column(UUID(as_uuid=True))
    id_mayorista = Column(UUID(as_uuid=True))
    nombre_servicio = Column(String)
    descripcion = Column(String)
    tipo_servicio = Column(String)
    precio = Column(String)
    ciudad = Column(String)
    activo = Column(Boolean, default=True)
    estado = Column(String)
    observaciones = Column(String)
    fecha_creacion = Column(Date)
    cantidad = Column(Integer)
    fecha_inicio = Column(Date)
    fecha_fin = Column(Date)


# ─── Helpers ─────────────────────────────────────────────────────────────────


def get_db_session():
    """Crea y retorna una sesión de base de datos."""
    return SessionLocal()


def validate_api_key(api_key: str) -> bool:
    """Valida que la API key proporcionada sea correcta."""
    if not MCP_API_KEY:
        raise ValueError(
            "MCP_API_KEY no está configurada. "
            "Define la variable de entorno MCP_API_KEY en tu archivo .env"
        )
    return api_key == MCP_API_KEY
