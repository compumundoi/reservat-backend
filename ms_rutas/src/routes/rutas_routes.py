from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import select, and_, or_, func, text
from datetime import datetime, timedelta
import logging
import uuid
from uuid import UUID
from fastapi.responses import JSONResponse
from config.db2 import DB
from models.rutas_model import RutaModel
from schemas.rutas_schema import DatosRuta, ActualizarRuta, RespuestaRuta, ResponseMessage, ResponseList, DatosOrigenDestino
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

rutas = APIRouter()

@rutas.post("/rutas/crear/", response_model=ResponseMessage)
async def crear_ruta(ruta: DatosRuta, db: Session = Depends(get_db)):
    """Crea un nuevas rutas  en la base de datos"""

    try:
        nuevo_ruta = RutaModel(**ruta.model_dump())
        db.add(nuevo_ruta)
        db.commit()
        db.refresh(nuevo_ruta)
        return ResponseMessage(message="Ruta creada exitosamente")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error en registro: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear la ruta"
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
    campos = (
        RutaModel.nombre,
        RutaModel.descripcion,
        RutaModel.origen,
        RutaModel.destino,
        RutaModel.puntos_interes,
    )
    return or_(*[func.unaccent(campo).ilike(patron) for campo in campos])


@rutas.get("/rutas/listar/", response_model=ResponseList)
async def listar_rutas(
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
        filtros = [RutaModel.activo == True]
        filtro_texto = _filtro_busqueda(busqueda)
        if filtro_texto is not None:
            filtros.append(filtro_texto)

        # Mismo filtro en el conteo y en la pagina.
        total = db.query(RutaModel).filter(*filtros).count()
        rutas = db.query(RutaModel).filter(*filtros).offset(skip).limit(limite).all()
        
        return ResponseList(
            rutas=rutas,
            total=total,
            page=pagina,
            size=limite
        )
        
    except Exception as e:
        logger.error(f"Error en listado: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al listar las rutas"
        )

@rutas.get("/rutas/consultar/{id_ruta}", response_model=RespuestaRuta)
async def consultar_ruta(id_ruta: str, db: Session = Depends(get_db)):
    """Consulta un mayorista específico por su ID"""
    try:
        uuid_obj = UUID(id_ruta)

        db_ruta = db.query(RutaModel).filter(RutaModel.id == id_ruta).filter(RutaModel.activo == True).first()

        if db_ruta is None:
            raise HTTPException(status_code=404, detail="Ruta no encontrado")

        return db_ruta

    except (ValueError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El ID proporcionado no es un UUID válido"
        )

@rutas.post("/rutas/origen-destino/", response_model=ResponseList)
async def crear_ruta(ruta: DatosOrigenDestino, pagina: int = 0, limite: int = 100, db: Session = Depends(get_db)):
    """consultar una ruta por origen y destino """
    try:
        # (pagina - 1) * pagina no paginaba: repetia la primera pagina y
        # saltaba registros. El frontend envia paginas 0-based.
        skip = max(0, pagina) * limite
        total = db.query(RutaModel).filter(RutaModel.origen == ruta.origen).filter(RutaModel.destino == ruta.destino).filter(RutaModel.activo == True).count()
        rutas = db.query(RutaModel).filter(RutaModel.origen == ruta.origen).filter(RutaModel.destino == ruta.destino).filter(RutaModel.activo == True).offset(skip).limit(limite).all()
        
        return ResponseList(
            rutas=rutas,
            total=total,
            page=pagina,
            size=limite
        )
        
    except Exception as e:
        logger.error(f"Error en listado: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al listar las rutas"
        )

    
@rutas.put("/rutas/editar/{id_ruta}", response_model=RespuestaRuta)
async def actualizar_ruta(id_ruta: str, datos: ActualizarRuta, db: Session = Depends(get_db)):
    """Actualiza los datos de una fecha bloqueada existente"""

    db_ruta = db.query(RutaModel).filter(RutaModel.id == id_ruta).filter(RutaModel.activo == True).first()
    if db_ruta is None:
        raise HTTPException(status_code=404, detail="Ruta no encontrado")
    
    for key, value in datos.model_dump(exclude_unset=True).items():
        setattr(db_ruta, key, value)
    
    db.commit()
    db.refresh(db_ruta)
    return db_ruta

@rutas.delete("/rutas/eliminar/{id_ruta}", response_model=ResponseMessage)
async def eliminar_ruta(id_ruta: str, db: Session = Depends(get_db)):
    
    try:
        uuid_obj = UUID(id_ruta)
        db_ruta = db.query(RutaModel).filter(RutaModel.id == id_ruta).first()
        if not db_ruta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ruta no encontrada"
            )
        if db_ruta.activo == False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La ruta ya ha sido eliminada"
            )  
        try:
            db_ruta.activo = False    
            db.commit()
            return ResponseMessage(message="Ruta eliminada exitosamente") 
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error en eliminación: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar la ruta"
            )
    except (ValueError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El ID proporcionado no es un UUID válido"
        )

# Endpoint de Health Check
@rutas.get("/rutas/healthchecker")
def get_live():
    return {"message": "Rutas service is LIVE!!"}

# Endpoint de Readiness
@rutas.get("/rutas/readiness")
def check_readiness(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT 1")).fetchone()
        if result and result[0] == 1:
            return {"status": "Ready"}
        return {"status": "Not Ready"}
    except Exception as e:
        logger.error(f"Error en readiness check: {str(e)}")
        return {"status": "Not Ready"}