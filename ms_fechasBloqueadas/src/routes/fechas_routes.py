from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import select, and_, text
from datetime import datetime, timedelta
import logging
import uuid
from uuid import UUID
from fastapi.responses import JSONResponse
from config.db2 import DB
from models.fechas_model import FechaBloqueada, Servicio
from schemas.fechas_schema import DatosFechaBloqueada, ActualizarFechaBloqueada, RespuestaFechaBloqueada, ResponseMessage, ResponseList
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

fechas = APIRouter()

@fechas.post("/fechas/crear/", response_model=ResponseMessage)
async def crear_fecha(fecha: DatosFechaBloqueada, db: Session = Depends(get_db)):
    """Crea un nuevo fecha bloqueada en la base de datos"""
    existing_fecha = db.query(FechaBloqueada).filter(and_(FechaBloqueada.servicio_id == fecha.servicio_id, FechaBloqueada.fecha == fecha.fecha)).first()
    existing_servicio = db.query(Servicio).filter(and_(Servicio.id_servicio == fecha.servicio_id)).first()

    if existing_fecha:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="la fecha ya esta bloqueada"
        )
    if existing_servicio is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="el servicio no existe"
        )
    try:
        nuevo_fecha = FechaBloqueada(**fecha.model_dump())
        db.add(nuevo_fecha)
        db.commit()
        db.refresh(nuevo_fecha)
        return ResponseMessage(message="Fecha bloqueada exitosamente")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error en registro: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al bloquear la fecha"
        )

@fechas.get("/fechas/listar/", response_model=ResponseList)
async def listar_mayoristas(pagina: int = 0, limite: int = 100, db: Session = Depends(get_db)):
    """Lista todas las fechas bloqueadas con paginación"""
    try:
        # (pagina - 1) * pagina no paginaba: repetia la primera pagina y
        # saltaba registros. El frontend envia paginas 0-based.
        skip = max(0, pagina) * limite
        total = db.query(FechaBloqueada).filter(FechaBloqueada.bloqueo_activo == True).count()
        fechas_bloqueadas = db.query(FechaBloqueada).filter(FechaBloqueada.bloqueo_activo == True).offset(skip).limit(limite).all()
        
        return ResponseList(
            fechas_bloqueadas=fechas_bloqueadas,
            total=total,
            page=pagina,
            size=limite
        )
        
    except Exception as e:
        logger.error(f"Error en listado: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al listar fechas bloqueadas"
        )

@fechas.get("/fechas/consultar/{id_fecha}", response_model=RespuestaFechaBloqueada)
async def consultar_mayorista(id_fecha: str, db: Session = Depends(get_db)):
    """Consulta un mayorista específico por su ID"""
    try:
        uuid_obj = UUID(id_fecha)

        db_fecha = db.query(FechaBloqueada).filter(FechaBloqueada.id == id_fecha).filter(FechaBloqueada.bloqueo_activo == True).first()

        if db_fecha is None:
            raise HTTPException(status_code=404, detail="Fecha bloqueada no encontrado")

        return db_fecha

    except (ValueError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El ID proporcionado no es un UUID válido"
        )
    
@fechas.put("/fechas/editar/{id_fecha}", response_model=RespuestaFechaBloqueada)
async def actualizar_fecha_bloqueada(id_fecha: str, datos: ActualizarFechaBloqueada, db: Session = Depends(get_db)):
    """Actualiza los datos de una fecha bloqueada existente"""

    db_fecha = db.query(FechaBloqueada).filter(FechaBloqueada.id == id_fecha).filter(FechaBloqueada.bloqueo_activo == True).first()
    if db_fecha is None:
        raise HTTPException(status_code=404, detail="Fecha bloqueada no encontrado")

    existing_servicio = db.query(Servicio).filter(and_(Servicio.id_servicio == datos.servicio_id)).first()
    if existing_servicio is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="el servicio no existe"
        )
    
    for key, value in datos.model_dump(exclude_unset=True).items():
        setattr(db_fecha, key, value)
    
    db.commit()
    db.refresh(db_fecha)
    return db_fecha

@fechas.delete("/fechas/eliminar/{id_fecha}", response_model=ResponseMessage)
async def eliminar_fecha_bloqueada(id_fecha: str, db: Session = Depends(get_db)):
    
    try:
        uuid_obj = UUID(id_fecha)
        db_fecha = db.query(FechaBloqueada).filter(FechaBloqueada.id == id_fecha).first()
        if not db_fecha:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fecha bloqueada no encontrada"
            )
        if not db_fecha.bloqueo_activo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La fecha bloqueada ya ha sido eliminada"
            )  
        try:
            db_fecha.bloqueo_activo = False
            db.commit()
            return ResponseMessage(message="Fecha bloqueada eliminada exitosamente") 
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error en eliminación: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar fecha bloqueada"
            )
    except (ValueError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El ID proporcionado no es un UUID válido"
        )

# Endpoint de Health Check
@fechas.get("/fechas/healthchecker")
def get_live():
    return {"message": "Fechas service is LIVE!!"}

# Endpoint de Readiness
@fechas.get("/fechas/readiness")
def check_readiness(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT 1")).fetchone()
        if result and result[0] == 1:
            return {"status": "Ready"}
        return {"status": "Not Ready"}
    except Exception as e:
        logger.error(f"Error en readiness check: {str(e)}")
        return {"status": "Not Ready"}