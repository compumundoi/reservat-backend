from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import select, and_, or_, func, text
from datetime import datetime, timedelta
import logging
import uuid
from uuid import UUID
from fastapi.responses import JSONResponse
from config.db2 import DB
from models.viajes_model import ViajesModel, RutasModel, TransportesModel
from schemas.viajes_schema import DatosViaje, ActualizarViaje, RespuestaViaje, ResponseMessage, ResponseList
from typing import List, Optional
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

viajes = APIRouter()

@viajes.post("/viajes/crear/", response_model=ResponseMessage)
async def crear_viaje(viaje: DatosViaje, db: Session = Depends(get_db)):
    """Crea un nuevas viajes  en la base de datos"""
    existing_ruta = db.query(RutasModel).filter(RutasModel.id == viaje.ruta_id).first()
    existing_transportador = db.query(TransportesModel).filter(and_(TransportesModel.id_transporte == viaje.id_transportador)).first()

    if existing_ruta is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="la ruta no existe"
        )
    if existing_transportador is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="el transportador no existe"
        )
    try:
        nuevo_viaje = ViajesModel(**viaje.model_dump())
        db.add(nuevo_viaje)
        db.commit()
        db.refresh(nuevo_viaje)
        return ResponseMessage(message="Viaje creado exitosamente")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error en registro: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear el viaje"
        )

def _filtro_busqueda(busqueda):
    """Arma el filtro de texto libre del listado.

    unaccent en ambos lados: quien escribe sin tildes espera encontrar
    igual. Devuelve None cuando no hay termino, para que el listado sin
    busqueda no pague el costo del OR.
    """
    if not busqueda or not busqueda.strip():
        return None

    patron = func.unaccent(f"%{busqueda.strip()}%")
    # El buscador de la UI promete "guía, estado, ruta": el nombre de la
    # ruta y el tipo de vehiculo viven en sus propias tablas, no en viajes.
    campos = (
        ViajesModel.guia_asignado,
        ViajesModel.estado,
        RutasModel.nombre,
        TransportesModel.tipo_vehiculo,
    )
    return or_(*[func.unaccent(campo).ilike(patron) for campo in campos])


def _query_viajes(db):
    """Consulta base de viajes con sus relaciones de texto.

    LEFT OUTER JOIN para que un viaje sin ruta o sin transportador asociado
    siga apareciendo en el listado.
    """
    return (
        db.query(ViajesModel)
        .outerjoin(RutasModel, ViajesModel.ruta_id == RutasModel.id)
        .outerjoin(
            TransportesModel,
            ViajesModel.id_transportador == TransportesModel.id_transporte,
        )
    )


@viajes.get("/viajes/listar/", response_model=ResponseList)
async def listar_viajes(
    pagina: int = 0,
    limite: int = 100,
    busqueda: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Lista todas las fechas bloqueadas con paginación"""
    try:
        # (pagina - 1) * pagina no paginaba: repetia la primera pagina y
        # saltaba registros. El frontend envia paginas 0-based.
        skip = max(0, pagina) * limite
        filtros = [ViajesModel.activo == True]
        filtro_texto = _filtro_busqueda(busqueda)
        if filtro_texto is not None:
            filtros.append(filtro_texto)

        # Mismo filtro en el conteo y en la pagina.
        total = _query_viajes(db).filter(*filtros).count()
        viajes = _query_viajes(db).filter(*filtros).offset(skip).limit(limite).all()
        
        return ResponseList(
            viajes=viajes,
            total=total,
            page=pagina,
            size=limite
        )
        
    except Exception as e:
        logger.error(f"Error en listado: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al listar los viajes"
        )

@viajes.get("/viajes/proveedor/{id_proveedor}", response_model=ResponseList)
async def listar_viajes(id_proveedor: str, pagina: int = 0, limite: int = 100, db: Session = Depends(get_db)):
    """Lista todas las fechas bloqueadas con paginación"""
   
    existing_proveedor = db.query(TransportesModel).filter(and_(TransportesModel.id_transporte == id_proveedor)).first()

    if existing_proveedor is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="el proveedor no existe"
        )
    try:
        # (pagina - 1) * pagina no paginaba: repetia la primera pagina y
        # saltaba registros. El frontend envia paginas 0-based.
        skip = max(0, pagina) * limite
        total = db.query(ViajesModel).filter(ViajesModel.activo == True, ViajesModel.id_transportador == id_proveedor).count()
        viajes = db.query(ViajesModel).filter(ViajesModel.activo == True, ViajesModel.id_transportador == id_proveedor).offset(skip).limit(limite).all()
        
        return ResponseList(
            viajes=viajes,
            total=total,
            page=pagina,
            size=limite
        )
        
    except Exception as e:
        logger.error(f"Error en listado: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al listar los viajes para el proveedor: " + id_proveedor
        )

@viajes.get("/viajes/consultar/{id_viaje}", response_model=RespuestaViaje)
async def consultar_viaje(id_viaje: str, db: Session = Depends(get_db)):
    """Consulta un mayorista específico por su ID"""
    try:
        uuid_obj = UUID(id_viaje)

        db_viaje = db.query(ViajesModel).filter(ViajesModel.id == id_viaje).filter(ViajesModel.activo == True).first()

        if db_viaje is None:
            raise HTTPException(status_code=404, detail="Viaje no encontrado")

        return db_viaje

    except (ValueError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El ID proporcionado no es un UUID válido"
        )
    
@viajes.put("/viajes/editar/{id_viaje}", response_model=RespuestaViaje)
async def actualizar_viaje(id_viaje: str, datos: ActualizarViaje, db: Session = Depends(get_db)):
    """Actualiza los datos de una fecha bloqueada existente"""

    db_viaje = db.query(ViajesModel).filter(ViajesModel.id == id_viaje).filter(ViajesModel.activo == True).first()
    if db_viaje is None:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")
  
    for key, value in datos.model_dump(exclude_unset=True).items():
        setattr(db_viaje, key, value)
    
    db.commit()
    db.refresh(db_viaje)
    return db_viaje

@viajes.delete("/viajes/eliminar/{id_viaje}", response_model=ResponseMessage)
async def eliminar_viaje(id_viaje: str, db: Session = Depends(get_db)):
    
    try:
        uuid_obj = UUID(id_viaje)
        db_viaje = db.query(ViajesModel).filter(ViajesModel.id == id_viaje).first()
        if not db_viaje:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Viaje no encontrada"
            )
        if db_viaje.activo == False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="EL viaje ya ha sido eliminada"
            )  
        try:
            db_viaje.activo = False
            db.commit()
            return ResponseMessage(message="Viaje eliminada exitosamente") 
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error en eliminación: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar el viaje"
            )
    except (ValueError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El ID proporcionado no es un UUID válido"
        )

# Endpoint de Health Check
@viajes.get("/viajes/healthchecker")
def get_live():
    return {"message": "Viajes service is LIVE!!"}

# Endpoint de Readiness
@viajes.get("/viajes/readiness")
def check_readiness(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT 1")).fetchone()
        if result and result[0] == 1:
            return {"status": "Ready"}
        return {"status": "Not Ready"}
    except Exception as e:
        logger.error(f"Error en readiness check: {str(e)}")
        return {"status": "Not Ready"}
