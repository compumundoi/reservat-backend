from fastapi import APIRouter, HTTPException, Depends, status, Response, Cookie
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import select, and_, text
from datetime import datetime, timedelta
from config.db2 import DB
import logging
import uuid
from uuid import UUID
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from models.user_model import UserModel, ProveedorModel, MayoristaModel
from schemas.user_schama import (
    UsuarioBase,
    UsuarioCreate,
    UsuarioUpdate,
    Usuario,
    LoginRequest,
    ChangePasswordRequest,
    Token,
    ResponseMessage,
    ResponseList,
    pwd_context
)
from typing import List
from pydantic import EmailStr, BaseModel
from passlib.context import CryptContext

# Configuración de la cookie
COOKIE_NAME = "auth_token"
COOKIE_DOMAIN = "localhost"  # Cambiar según el dominio real
COOKIE_PATH = "/"
COOKIE_SECURE = False  # Cambiar a True en producción
COOKIE_HTTPONLY = True
COOKIE_SAMESITE = "lax"

# Configuración del JWT
JWT_SECRET = "Hola-mundo-xd"#"your-secret-key-here"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_MINUTES = 30

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

db = DB.create()
Session = sessionmaker(bind=db.engine)

# Función para obtener la sesión de la base de datos
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()

user = APIRouter()

# Endpoint de Login
@user.post("/usuarios/login", response_model=Token)
async def login_user(request: LoginRequest, db: Session = Depends(get_db), response: Response = None):
    try:
        # Verificar si el email existe
        user = db.query(UserModel).filter(UserModel.email == request.email).first()

        # Verificar si el usuario existe
        if user == None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El usuario no existe"
            )
        
        # Verificar si el usuario esta activo
        if user.activo == False:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="El usuario no esta activo, comunicate con el administrador"
            )
            
        # Verificar si las credenciales son correctas
        if not pwd_context.verify(request.contraseña, user.contraseña):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas"
            )
            
        # Actualizar último login
        user.ultimo_login = datetime.now()
        db.commit()

        # Default values from the base user model
        userEmail = user.email
        userId = user.id
        tipo_u = user.tipo_usuario

        if user.tipo_usuario == "proveedor":
            db_user = db.query(ProveedorModel).filter(ProveedorModel.email == request.email).first()  
            if db_user:
                userEmail = db_user.email
                userId = db_user.id_proveedor
                tipo_u = db_user.tipo
            else:
                logger.warning(f"User with role 'proveedor' not found in proveedores table: {request.email}")
            
        elif user.tipo_usuario == "mayorista":
            db_user = db.query(MayoristaModel).filter(MayoristaModel.email == request.email).first()
            if db_user:
                userEmail = db_user.email
                userId = db_user.id
                tipo_u = user.tipo_usuario
            else:
                logger.warning(f"User with role 'mayorista' not found in mayoristas table: {request.email}")

        
        # Generar token JWT
        expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_MINUTES)
        to_encode = {
            "id": str(userId),  # Convertimos el UUID a string
            "email": userEmail,
            "tipo_usuario": tipo_u,
            "exp": expire
        }
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
        
        # Configurar la cookie de sesión
        response = Response(
            content=Token(
                access_token=encoded_jwt,
                token_type="bearer"
            ).model_dump_json(),
            media_type="application/json"
        )
        
        # Configurar la cookie
        response.set_cookie(
            key=COOKIE_NAME,
            value=encoded_jwt,
            domain=COOKIE_DOMAIN,
            path=COOKIE_PATH,
            secure=COOKIE_SECURE,
            httponly=COOKIE_HTTPONLY,
            samesite=COOKIE_SAMESITE,
            max_age=JWT_EXPIRATION_MINUTES * 60,
            expires=expire.timestamp()
        )
        
        return response
        
    except HTTPException as e:
        logger.error(f"Error en login: {str(e.detail)}")
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error inesperado en login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


# Endpoint de Registro
@user.post("/usuarios/crear/", response_model=ResponseMessage)
async def create_user(user: UsuarioCreate, db: Session = Depends(get_db)):
    # Verificar si el email ya existe
    existing_user = db.query(UserModel).filter(UserModel.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email ya registrado"
        )

    try:
        # Crear nuevo usuario
        new_user = UserModel(
            nombre=user.nombre,
            apellido=user.apellido,
            email=user.email,
            contraseña=user.hashed_password,  # Aquí se usa el hash de la contraseña
            fecha_registro=datetime.now(),
            ultimo_login=datetime.now(),
            activo=True,
            tipo_usuario=user.tipo_usuario
        )
        
        db.add(new_user)
        db.commit()
        
        logger.info(f"Usuario creado exitosamente: {new_user.id}")
        return ResponseMessage(message="Usuario creado exitosamente")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error en registro: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear usuario"
        )

# Endpoint de Listar
@user.get("/usuarios/listar/", response_model=ResponseList)
async def list_users(page: int = 1, size: int = 10, db: Session = Depends(get_db)):
    try:
        skip = (page - 1) * size
        total = db.query(UserModel).filter(UserModel.activo == True).count()
        
        usuarios = db.query(UserModel).filter(UserModel.activo == True).offset(skip).limit(size).all()
        
        return ResponseList(
            usuarios=usuarios,
            total=total,
            page=page,
            size=size
        )
        
    except Exception as e:
        logger.error(f"Error en listado: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al listar usuarios"
        )

# Endpoint de Eliminación Lógica
@user.delete("/usuarios/eliminar/{user_id}", response_model=ResponseMessage)
async def delete_user(user_id: uuid.UUID, db: Session = Depends(get_db)):
    # Primero buscamos el usuario sin filtrar por activo
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
        
    if not db_user.activo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario ya ha sido eliminado"
        )
    
    try:
        # Realizar eliminación lógica
        db_user.activo = False
        db.commit()
        
        return ResponseMessage(message="Usuario eliminado exitosamente")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error en eliminación: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al eliminar usuario"
        )

# Endpoint para cambiar contraseña
@user.put("/usuarios/cambiar-contrasena", response_model=ResponseMessage)
async def change_password(request: ChangePasswordRequest, db: Session = Depends(get_db)):
    try:
        # Buscar usuario por email
        user = db.query(UserModel).filter(UserModel.email == request.email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
            
        # Verificar contraseña actual
        is_valid = pwd_context.verify(request.contraseña_actual, user.contraseña)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Contraseña actual incorrecta"
            )
            
        # Verificar si la nueva contraseña es diferente
        if request.contraseña_actual == request.nueva_contraseña:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La nueva contraseña debe ser diferente a la actual"
            )
            
        # Actualizar contraseña
        user.contraseña = pwd_context.hash(request.nueva_contraseña)
        user.ultimo_login = datetime.now()
        db.commit()
        
        return ResponseMessage(message="Contraseña cambiada exitosamente")
        
    except HTTPException as e:
        logger.error(f"Error HTTP al cambiar contraseña: {str(e.detail)}")
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error inesperado al cambiar contraseña: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al cambiar contraseña"
        )

# Endpoint de Health Check
@user.get("/usuarios/healthchecker")
def get_live():
    return {"message": "Usuarios service is LIVE!!"}

# Endpoint de Readiness
@user.get("/usuarios/readiness")
def check_readiness(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT 1")).fetchone()
        if result and result[0] == 1:
            return {"status": "Ready"}
        return {"status": "Not Ready"}
    except Exception as e:
        logger.error(f"Error en readiness check: {str(e)}")
        return {"status": "Not Ready"}

# Endpoint de Login administrador
@user.post("/usuarios/admin", response_model=Token)
async def login_admin(request: LoginRequest, db: Session = Depends(get_db), response: Response = None):

    try:
        # Verificar si el email existe
        user = db.query(UserModel).filter(UserModel.email == request.email).first()

        # Verificar si el usuario es admin
        if user.tipo_usuario != "admin":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El usuario no es administrador"
            )
        
        # Verificar si el usuario esta activo
        if user.activo == False:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El usuario no esta activo, comunicate con el administrador"
            )
        
        # Verificar si el usuario esta activo
        if user == None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El usuario no existe"
            )
            
        # Verificar si las credenciales son correctas
        if not pwd_context.verify(request.contraseña, user.contraseña):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas"
            )
            
        # Actualizar último login
        user.ultimo_login = datetime.now()
        db.commit()

        userEmail = user.email
        userId = user.id
        
        # Generar token JWT
        expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_MINUTES)
        to_encode = {
            "id": str(userId),  # Convertimos el UUID a string
            "email": userEmail,
            "tipo_usuario": "admin",
            "exp": expire
        }
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
        
        # Configurar la cookie de sesión
        response = Response(
            content=Token(
                access_token=encoded_jwt,
                token_type="bearer"
            ).model_dump_json(),
            media_type="application/json"
        )
        
        # Configurar la cookie
        response.set_cookie(
            key=COOKIE_NAME,
            value=encoded_jwt,
            domain=COOKIE_DOMAIN,
            path=COOKIE_PATH,
            secure=COOKIE_SECURE,
            httponly=COOKIE_HTTPONLY,
            samesite=COOKIE_SAMESITE,
            max_age=JWT_EXPIRATION_MINUTES * 60,
            expires=expire.timestamp()
        )
        
        return response
        
    except HTTPException as e:
        logger.error(f"Error en login: {str(e.detail)}")
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error inesperado en login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

