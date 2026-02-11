from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import select, and_, text
from datetime import datetime, timedelta
import logging
import uuid
from uuid import UUID
from fastapi.responses import JSONResponse
from config.db2 import DB
from models.servicios_model import ServicioModel, ProveedorModel
from schemas.servicios_schema import DatosServicio, ActualizarServicio, RespuestaServicio, ResponseMessage, ResponseList
from typing import List
from pydantic import ValidationError

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

servicios = APIRouter()

@servicios.post("/servicios/crear/", response_model=ResponseMessage)
async def crear_servicio(servicio: DatosServicio, db: Session = Depends(get_db)):
    """Crea un nuevas servicios  en la base de datos"""
    existing_proveedor = db.query(ProveedorModel).filter(ProveedorModel.id_proveedor == servicio.proveedor_id).first()

    if existing_proveedor is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="el proveedor no existe"
        )
    try:
        nuevo_servicio = ServicioModel(**servicio.model_dump())
        db.add(nuevo_servicio)
        db.commit()
        db.refresh(nuevo_servicio)
        return ResponseMessage(message="Servicio creado exitosamente")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error en registro: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear el servicio"
        )

@servicios.get("/servicios/listar/", response_model=ResponseList)
async def listar_servicios(pagina: int = 0, limite: int = 100, db: Session = Depends(get_db)):
    """Lista todas las fechas bloqueadas con paginación"""
    try:
        skip = pagina * limite
        total = db.query(ServicioModel).filter(ServicioModel.activo == True).count()
        servicios = db.query(ServicioModel).filter(ServicioModel.activo == True).offset(skip).limit(limite).all()
                
        return ResponseList(
            servicios=servicios,
            total=total,
            page=pagina,
            size=limite
        )
        
    except Exception as e:
        logger.error(f"Error en listado: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al listar los servicios"
        )

@servicios.get("/servicios/proveedor/{id_proveedor}", response_model=ResponseList)
async def listar_fotos(id_proveedor: str, pagina: int = 0, limite: int = 100, db: Session = Depends(get_db)):
    """Lista todos los servicios por proveedor con paginación"""
   
    existing_proveedor = db.query(ProveedorModel).filter(and_(ProveedorModel.id_proveedor == id_proveedor, ProveedorModel.activo == True)).first()

    if existing_proveedor is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="el proveedor no existe"
        )
    try:
        skip = pagina * limite
        total = db.query(ServicioModel).filter(ServicioModel.activo == True, ServicioModel.proveedor_id == id_proveedor).count()
        servicios = db.query(ServicioModel).filter(ServicioModel.activo == True, ServicioModel.proveedor_id == id_proveedor).offset(skip).limit(limite).all()
        
        return ResponseList(
            servicios=servicios,
            total=total,
            page=pagina,
            size=limite
        )
        
    except Exception as e:
        logger.error(f"Error en listado: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al listar los servicios para el proveedor: " + id_proveedor
        )

@servicios.get("/servicios/consultar/{id_servicio}", response_model=RespuestaServicio)
async def consultar_servicio(id_servicio: str, db: Session = Depends(get_db)):
    """Consulta un mayorista específico por su ID"""
    try:
        uuid_obj = UUID(id_servicio)

        db_servicio = db.query(ServicioModel).filter(ServicioModel.id_servicio == id_servicio).filter(ServicioModel.activo == True).first()

        if db_servicio is None:
            raise HTTPException(status_code=404, detail="Servicio no encontrado")

        return db_servicio

    except (ValueError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El ID proporcionado no es un UUID válido"
        )
    
@servicios.put("/servicios/editar/{id_servicio}", response_model=RespuestaServicio)
async def actualizar_servicio(id_servicio: str, datos: ActualizarServicio, db: Session = Depends(get_db)):
    """Actualiza los datos de un servicio existente"""

    db_servicio = db.query(ServicioModel).filter(ServicioModel.id_servicio == id_servicio).filter(ServicioModel.activo == True).first()
    if db_servicio is None:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")

    existing_servicio = db.query(ServicioModel).filter(and_(ServicioModel.id_servicio == datos.id_servicio)).first()
    if existing_servicio is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="el servicio no existe"
        )
    
    for key, value in datos.model_dump(exclude_unset=True).items():
        setattr(db_servicio, key, value)
    
    db.commit()
    db.refresh(db_servicio)
    return db_servicio

@servicios.delete("/servicios/eliminar/{id_servicio}", response_model=ResponseMessage)
async def eliminar_servicio(id_servicio: str, db: Session = Depends(get_db)):
    
    try:
        uuid_obj = UUID(id_servicio)
        db_servicio = db.query(ServicioModel).filter(ServicioModel.id_servicio == id_servicio).first()
        if not db_servicio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Servicio no encontrado"
            )
        if db_servicio.activo is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El servicio ya ha sido eliminado"
            )  
        try:
            db_servicio.activo = False
            db.commit()
            return ResponseMessage(message="Servicio eliminado exitosamente") 
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error en eliminación: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar el servicio"
            )
    except (ValueError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El ID proporcionado no es un UUID válido"
        )

# Endpoint de Health Check
@servicios.get("/servicios/healthchecker")
def get_live():
    return {"message": "Servicios service is LIVE!!"}

# Endpoint de Readiness
@servicios.get("/servicios/readiness")
def check_readiness(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT 1")).fetchone()
        if result and result[0] == 1:
            return {"status": "Ready"}
        return {"status": "Not Ready"}
    except Exception as e:
        logger.error(f"Error en readiness check: {str(e)}")
        return {"status": "Not Ready"}