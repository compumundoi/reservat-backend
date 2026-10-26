import logging
import os
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
import sqlalchemy
from passlib.context import CryptContext

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Contexto para hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class DB:
    _instance = None

    def __init__(self):
        if DB._instance is not None:
            raise ValueError("This class is a singleton, use DB.create()")
        else:
            DB._instance = self
        self.engine = self.create_engine()

    @staticmethod
    def create():
        if DB._instance is None:
            DB._instance = DB()
        return DB._instance

    def create_engine(self):
        # Prioridad: Variables de entorno
        db_user = os.getenv('DB_USER', 'postgres')
        db_password = os.getenv('DB_PASSWORD', 'postgres')
        db_host = os.getenv('DB_HOST', 'db')
        db_port = os.getenv('DB_PORT', '5432')
        db_name = os.getenv('DB_NAME', 'reservat')
        
        try:
            # Construir la URL de conexión de forma más robusta
            connection_url = URL.create(
                drivername="postgresql+psycopg2",
                username=db_user,
                password=db_password,
                host=db_host,
                port=int(db_port),
                database=db_name
            )
            
            logger.info(f"Conectando a la base de datos en {db_host}:{db_port}/{db_name} como {db_user}")
            
            # Todos los servicios comparten un Postgres de max_connections=100.
            # Con pool_size=200 el pool retenia cada conexion abierta en un
            # pico y terminaba agotando la base para todos. Ahora quedan 2
            # abiertas por worker y las de un pico se cierran al devolverse.
            # max_overflow es alto a proposito: los endpoints son async con
            # consultas sincronas, y esperar una conexion bloquea el event
            # loop del worker entero, que es quien debe liberarlas.
            engine = create_engine(
                connection_url,
                pool_size=2,
                max_overflow=60,
                pool_timeout=10,
                pool_recycle=60
            )
            return engine
            
        except Exception as e:
            logger.error(f"Error al conectar a la base de datos: {str(e)}")
            raise

meta = sqlalchemy.MetaData(schema="usr_app")
