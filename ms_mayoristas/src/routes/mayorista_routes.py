from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import select, and_, or_, func, text
from datetime import datetime, timedelta
import logging
import uuid
from uuid import UUID
from fastapi.responses import JSONResponse
from config.db2 import DB
from models.mayorista_model import Mayorista
from schemas.mayorista_schema import DatosMayorista, ActualizarMayorista, RespuestaMayorista, ResponseMessage, ResponseList
from utils.ubicacion import campos_ubicacion
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

mayorista = APIRouter()

@mayorista.post("/mayorista/crear", response_model=ResponseMessage)
async def crear_mayorista(mayorista: DatosMayorista, db: Session = Depends(get_db)):
    """Crea un nuevo mayorista en la base de datos"""
    existing_mayorista = db.query(Mayorista).filter(Mayorista.email == mayorista.email).first()
    if existing_mayorista:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email ya registrado"
        )
    datos = mayorista.model_dump()
    # La ubicacion en texto nunca se toma del cliente: se deriva del municipio
    # elegido para que no entren ciudades inventadas. Fuera del try para que un
    # municipio invalido devuelva 400 y no el 500 generico.
    datos.update(campos_ubicacion(db, datos.get("municipio_id")))

    try:
        nuevo_mayorista = Mayorista(**datos)
        db.add(nuevo_mayorista)
        db.commit()
        db.refresh(nuevo_mayorista)
        return ResponseMessage(message="Mayorista creado exitosamente")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error en registro: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear mayorista"
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
        Mayorista.nombre,
        Mayorista.apellidos,
        Mayorista.email,
        Mayorista.ciudad,
        Mayorista.pais,
        Mayorista.numero_documento,
        Mayorista.telefono,
        Mayorista.descripcion,
        Mayorista.intereses,
    )
    return or_(*[func.unaccent(campo).ilike(patron) for campo in campos])


@mayorista.get("/mayorista/listar", response_model=ResponseList)
async def listar_mayoristas(
    pagina: int = 0,
    limite: int = 100,
    busqueda: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Lista todos los mayoristas con paginación"""
    try:
        # El salto se calcula con el tamano de pagina, no con el numero de
        # pagina: (pagina - 1) * pagina devolvia registros equivocados.
        # El frontend envia paginas 0-based.
        skip = max(0, pagina) * limite

        filtros = [Mayorista.activo == True]
        filtro_texto = _filtro_busqueda(busqueda)
        if filtro_texto is not None:
            filtros.append(filtro_texto)

        # Mismo filtro en el conteo y en la pagina.
        total = db.query(Mayorista).filter(*filtros).count()
        mayoristas = db.query(Mayorista).filter(*filtros).offset(skip).limit(limite).all()
        
        return ResponseList(
            mayoristas=mayoristas,
            total=total,
            page=pagina,
            size=limite
        )
        
    except Exception as e:
        logger.error(f"Error en listado: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al listar mayoristas"
        )

@mayorista.get("/mayorista/consultar/{id_mayorista}", response_model=RespuestaMayorista)
async def consultar_mayorista(id_mayorista: str, db: Session = Depends(get_db)):
    """Consulta un mayorista específico por su ID"""
    try:
        uuid_obj = UUID(id_mayorista)

        db_mayorista = db.query(Mayorista).filter(Mayorista.id == id_mayorista).filter(Mayorista.activo == True).first()

        if db_mayorista is None:
            raise HTTPException(status_code=404, detail="Mayorista no encontrado")

        return db_mayorista

    except (ValueError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El ID proporcionado no es un UUID válido"
        )
        

@mayorista.put("/mayorista/editar/{id_mayorista}", response_model=RespuestaMayorista)
async def actualizar_mayorista(id_mayorista: str, datos: ActualizarMayorista, db: Session = Depends(get_db)):
    """Actualiza los datos de un mayorista existente"""
    db_mayorista = db.query(Mayorista).filter(Mayorista.id == id_mayorista).filter(Mayorista.activo == True).first()
    if db_mayorista is None:
        raise HTTPException(status_code=404, detail="Mayorista no encontrado")
    
    cambios = datos.model_dump(exclude_unset=True)
    # Si viene municipio_id se recalcula toda la ubicacion; si no, se ignoran
    # los campos de texto para que nadie los pise a mano.
    if cambios.get("municipio_id") is not None:
        cambios.update(campos_ubicacion(db, cambios["municipio_id"]))
    else:
        for campo in ("ciudad", "departamento", "pais", "pais_id", "departamento_id"):
            cambios.pop(campo, None)

    for key, value in cambios.items():
        setattr(db_mayorista, key, value)
    
    db.commit()
    db.refresh(db_mayorista)
    return db_mayorista

@mayorista.delete("/mayorista/eliminar/{id_mayorista}", response_model=ResponseMessage)
async def eliminar_mayorista(id_mayorista: str, db: Session = Depends(get_db)):
    
    try:
        uuid_obj = UUID(id_mayorista)
        db_mayorista = db.query(Mayorista).filter(Mayorista.id == id_mayorista).first()
        if not db_mayorista:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mayorista no encontrado"
            )
        if not db_mayorista.activo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El mayorista ya ha sido eliminado"
            )  
        try:
            db_mayorista.activo = False
            db.commit()
            return ResponseMessage(message="Mayorista eliminado exitosamente") 
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error en eliminación: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar mayorista"
            )
    except (ValueError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El ID proporcionado no es un UUID válido"
        )

# Endpoint de Health Check
@mayorista.get("/mayorista/healthchecker")
def get_live():
    return {"message": "Mayorista service is LIVE!!"}

# Endpoint de Readiness
@mayorista.get("/mayorista/readiness")
def check_readiness(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT 1")).fetchone()
        if result and result[0] == 1:
            return {"status": "Ready"}
        return {"status": "Not Ready"}
    except Exception as e:
        logger.error(f"Error en readiness check: {str(e)}")
        return {"status": "Not Ready"}
