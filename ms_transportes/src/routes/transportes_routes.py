from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import select, and_, or_, func, text
from datetime import datetime, timedelta
import logging
import uuid
from uuid import UUID
from fastapi.responses import JSONResponse
from config.db2 import DB
from models.transportes_model import TransporteModel, ProveedorModel
from schemas.transportes_schema import DatosTransporte, CrearTransporteRequest, ResponseMessage, ResponseList, DatosProveedor, ListarTransporteResponse, ListarDatosProveedor, ListarDatosTransporte
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

transportes = APIRouter()

def crear_registro(model, datos, uuid=None):
    """Crea un registro en la base de datos usando los datos del schema"""
    # Filtrar los campos que están en el modelo
    campos_modelo = {k: v for k, v in datos.items() if hasattr(model, k)}
    if uuid:
        # Obtener el nombre del campo ID del modelo
        for column in model.__table__.columns:
            if column.primary_key:
                campos_modelo[column.name] = uuid
                break
    return model(**campos_modelo)

@transportes.post("/transportes/crear/", response_model=ResponseMessage)
async def crear_transporte(request: CrearTransporteRequest, db: Session = Depends(get_db)):
    """Crea un nuevo transporte y su proveedor asociado en la base de datos"""
    
    # Verificar si el proveedor ya existe
    if db.query(ProveedorModel).filter(ProveedorModel.email == request.proveedor.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El proveedor ya existe"
        )
    
    try:
        # Generar UUID único
        nuevo_uuid = uuid.uuid4()
        
        # Crear y guardar proveedor
        proveedor_datos = request.proveedor.model_dump()
        nuevo_proveedor = crear_registro(ProveedorModel, proveedor_datos, nuevo_uuid)
        db.add(nuevo_proveedor)
        db.commit()
        
        # Crear y guardar transporte
        transporte_datos = request.transporte.model_dump()
        nuevo_transporte = crear_registro(TransporteModel, transporte_datos, nuevo_uuid)
        db.add(nuevo_transporte)
        db.commit()
        
        return ResponseMessage(message="Proveedor y transporte creados exitosamente")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error en registro: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear el proveedor y transporte"
        )

def _filtro_busqueda(busqueda):
    """Arma el filtro de texto libre del listado.

    unaccent en ambos lados: quien escribe "medellin" sin tilde espera
    encontrar "Medellin". Devuelve None cuando no hay termino, para que el
    listado sin busqueda no pague el costo del OR.
    """
    if not busqueda or not busqueda.strip():
        return None

    patron = func.unaccent(f"%{busqueda.strip()}%")
    campos = (
        TransporteModel.tipo_vehiculo,
        TransporteModel.modelo,
        TransporteModel.placa,
        ProveedorModel.nombre,
        ProveedorModel.email,
        ProveedorModel.ciudad,
        ProveedorModel.pais,
        ProveedorModel.descripcion,
        ProveedorModel.direccion,
    )
    return or_(*[func.unaccent(campo).ilike(patron) for campo in campos])


@transportes.get("/transportes/listar/", response_model=ResponseList)
async def listar_restaurantes(
    pagina: int = 1,
    limite: int = 100,
    busqueda: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Lista todos los restaurantes con su información de proveedor"""
    try:
        pagina = max(1, pagina)
        skip = (pagina - 1) * limite

        query = db.query(TransporteModel, ProveedorModel)\
            .join(ProveedorModel, TransporteModel.id_transporte == ProveedorModel.id_proveedor)\
            .filter(ProveedorModel.activo == True)

        # El mismo filtro va al conteo y a la pagina: filtrar solo la pagina
        # dejaria mintiendo al total y al numero de paginas.
        filtro_texto = _filtro_busqueda(busqueda)
        if filtro_texto is not None:
            query = query.filter(filtro_texto)

        total = query.count()
        print("Total de restaurantes:", total)
    
        resultados = query.offset(skip).limit(limite).all()

        lista_respuesta = []

        for restaurante, proveedor in resultados:

            proveedor_dict = proveedor.__dict__.copy()
            restaurante_dict = restaurante.__dict__.copy()

            item = ListarTransporteResponse(
                proveedor=ListarDatosProveedor(**proveedor_dict),
                transporte=ListarDatosTransporte(**restaurante_dict)
            )
            lista_respuesta.append(item)

        return ResponseList(
            data=lista_respuesta,
            total=total,
            page=pagina,
            size=limite
        )

    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail="Error al listar hoteles")

@transportes.get("/transportes/consultar/{id_transporte}", response_model=ListarTransporteResponse)
async def listar_restaurantes(id_transporte: str,db: Session = Depends(get_db)):
    """Lista todos los restaurantes con su información de proveedor"""
    try:

        query = db.query(TransporteModel, ProveedorModel)\
            .join(ProveedorModel, TransporteModel.id_transporte == ProveedorModel.id_proveedor)\
            .filter(ProveedorModel.activo == True, TransporteModel.id_transporte == id_transporte)

        resultados = query.all()

        if not resultados:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="transporte no encontrado")

        try:
            for transporte, proveedor in resultados:
                proveedor_dict = proveedor.__dict__.copy()
                transporte_dict = transporte.__dict__.copy()

            return ListarTransporteResponse(
                    proveedor=ListarDatosProveedor(**proveedor_dict),
                    transporte=ListarDatosTransporte(**transporte_dict)
                )
        except Exception as e:
            print("Error:", e)
            raise HTTPException(status_code=500, detail="Error al listar transportes")

    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail="Error al listar transportes")
   
@transportes.put("/transportes/editar/{id_transporte}", response_model=ListarTransporteResponse)
async def actualizar_restaurante(id_transporte: str, datos: CrearTransporteRequest, db: Session = Depends(get_db)):
    """Actualiza los datos de un restaurante y su proveedor"""
    try:
        # Obtener el restaurante y proveedor existentes
        db_transporte, db_proveedor = db.query(TransporteModel, ProveedorModel)\
            .join(ProveedorModel, TransporteModel.id_transporte == ProveedorModel.id_proveedor)\
            .filter(ProveedorModel.activo == True, TransporteModel.id_transporte == id_transporte).first()
        
        if db_transporte is None:
            raise HTTPException(status_code=404, detail="transporte no encontrado")

        # Actualizar los campos del restaurante
        for key, value in datos.transporte.model_dump(exclude_unset=True).items():
            setattr(db_transporte, key, value)

        # Actualizar los campos del proveedor
        for key, value in datos.proveedor.model_dump(exclude_unset=True).items():
            setattr(db_proveedor, key, value)

        # Guardar cambios
        db.commit()
        
        # Refrescar los objetos
        db.refresh(db_transporte)
        db.refresh(db_proveedor)

        # Devolver la respuesta con los datos actualizados
        return ListarTransporteResponse(
            proveedor=ListarDatosProveedor(**db_proveedor.__dict__),
            transporte=ListarDatosTransporte(**db_transporte.__dict__)
        )

    except Exception as e:
        logger.error(f"Error al actualizar transporte: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al actualizar el transporte"
        )

@transportes.delete("/transportes/eliminar/{id_transporte}", response_model=ResponseMessage)
async def eliminar_restaurante(id_transporte: str, db: Session = Depends(get_db)):
    
    try:
        uuid_obj = UUID(id_transporte)
        
        db_proveedor = db.query(ProveedorModel)\
            .filter(ProveedorModel.id_proveedor == id_transporte).first()

        if not db_proveedor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transporte no encontrado"
            )
        if db_proveedor.activo == False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El transporte ya ha sido eliminado"
            )  
        try:
            db_proveedor.activo = False
            db.commit()
            return ResponseMessage(message="Transporte eliminado exitosamente") 
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error en eliminación: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar el transporte"
            )
    except (ValueError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El ID proporcionado no es un UUID válido"
        )

# Endpoint de Health Check
@transportes.get("/transportes/healthchecker")
def get_live():
    return {"message": "Transportes service is LIVE!!"}

# Endpoint de Readiness
@transportes.get("/transportes/readiness")
def check_readiness(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT 1")).fetchone()
        if result and result[0] == 1:
            return {"status": "Ready"}
        return {"status": "Not Ready"}
    except Exception as e:
        logger.error(f"Error en readiness check: {str(e)}")
        return {"status": "Not Ready"}