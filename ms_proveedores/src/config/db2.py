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
        db_user = os.getenv('DB_USER', 'postgres')
        db_password = os.getenv('DB_PASSWORD', 'postgres')
        db_host = os.getenv('DB_HOST', 'db')
        db_port = os.getenv('DB_PORT', '5432')
        db_name = os.getenv('DB_NAME', 'reservat')
        
        try:
            connection_url = URL.create(
                drivername="postgresql+psycopg2",
                username=db_user,
                password=db_password,
                host=db_host,
                port=int(db_port),
                database=db_name
            )
            
            logger.info(f"Conectando a la base de datos en {db_host}:{db_port}/{db_name} como {db_user}")
            
            engine = create_engine(
                connection_url,
                pool_size=200,
                max_overflow=0,
                pool_recycle=60
            )
            return engine
            
        except Exception as e:
            logger.error(f"Error al conectar a la base de datos: {str(e)}")
            raise

meta = sqlalchemy.MetaData(schema="usr_app")
