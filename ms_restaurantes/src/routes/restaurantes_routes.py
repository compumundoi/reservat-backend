from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import select, and_, or_, func, text
from datetime import datetime, timedelta
import logging
import uuid
from uuid import UUID
from fastapi.responses import JSONResponse
from config.db2 import DB
from models.restaurantes_model import restauranteModel, ProveedorModel
from schemas.restaurantes_schema import DatosRestaurante, CrearRestauranteRequest, ResponseMessage, ResponseList, DatosProveedor, ListarRestauranteResponse, ListarDatosProveedor, ListarDatosRestaurante
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

restaurantes = APIRouter()

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

@restaurantes.post("/restaurantes/crear/", response_model=ResponseMessage)
async def crear_restaurante(request: CrearRestauranteRequest, db: Session = Depends(get_db)):
    """Crea un nuevo restaurante y su proveedor asociado en la base de datos"""
    
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
        
        # Crear y guardar restaurante
        restaurante_datos = request.restaurante.model_dump()
        nuevo_restaurante = crear_registro(restauranteModel, restaurante_datos, nuevo_uuid)
        db.add(nuevo_restaurante)
        db.commit()
        
        return ResponseMessage(message="Proveedor y restaurante creados exitosamente")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error en registro: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear el proveedor y restaurante"
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
        restauranteModel.tipo_cocina,
        restauranteModel.tipo_comida,
        ProveedorModel.nombre,
        ProveedorModel.email,
        ProveedorModel.ciudad,
        ProveedorModel.pais,
        ProveedorModel.descripcion,
        ProveedorModel.direccion,
    )
    return or_(*[func.unaccent(campo).ilike(patron) for campo in campos])


@restaurantes.get("/restaurantes/listar/", response_model=ResponseList)
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

        query = db.query(restauranteModel, ProveedorModel)\
            .join(ProveedorModel, restauranteModel.id_restaurante == ProveedorModel.id_proveedor)\
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

            item = ListarRestauranteResponse(
                proveedor=ListarDatosProveedor(**proveedor_dict),
                restaurante=ListarDatosRestaurante(**restaurante_dict)
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

@restaurantes.get("/restaurantes/consultar/{id_restaurante}", response_model=ListarRestauranteResponse)
async def listar_restaurantes(id_restaurante: str,db: Session = Depends(get_db)):
    """Lista todos los restaurantes con su información de proveedor"""
    try:

        query = db.query(restauranteModel, ProveedorModel)\
            .join(ProveedorModel, restauranteModel.id_restaurante == ProveedorModel.id_proveedor)\
            .filter(ProveedorModel.activo == True, restauranteModel.id_restaurante == id_restaurante)

        resultados = query.all()

        if not resultados:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="restaurante no encontrado")

        try:
            for restaurante, proveedor in resultados:
                proveedor_dict = proveedor.__dict__.copy()
                restaurante_dict = restaurante.__dict__.copy()

            return ListarRestauranteResponse(
                    proveedor=ListarDatosProveedor(**proveedor_dict),
                    restaurante=ListarDatosRestaurante(**restaurante_dict)
                )
        except Exception as e:
            print("Error:", e)
            raise HTTPException(status_code=500, detail="Error al listar restaurantes")

    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail="Error al listar restaurantes")
   
@restaurantes.put("/restaurantes/editar/{id_restaurante}", response_model=ListarRestauranteResponse)
async def actualizar_restaurante(id_restaurante: str, datos: CrearRestauranteRequest, db: Session = Depends(get_db)):
    """Actualiza los datos de un restaurante y su proveedor"""
    try:
        # Obtener el restaurante y proveedor existentes
        db_restaurante, db_proveedor = db.query(restauranteModel, ProveedorModel)\
            .join(ProveedorModel, restauranteModel.id_restaurante == ProveedorModel.id_proveedor)\
            .filter(ProveedorModel.activo == True, restauranteModel.id_restaurante == id_restaurante).first()
        
        if db_restaurante is None:
            raise HTTPException(status_code=404, detail="Restaurante no encontrado")

        # Actualizar los campos del restaurante
        for key, value in datos.restaurante.model_dump(exclude_unset=True).items():
            setattr(db_restaurante, key, value)

        # Actualizar los campos del proveedor
        for key, value in datos.proveedor.model_dump(exclude_unset=True).items():
            setattr(db_proveedor, key, value)

        # Guardar cambios
        db.commit()
        
        # Refrescar los objetos
        db.refresh(db_restaurante)
        db.refresh(db_proveedor)

        # Devolver la respuesta con los datos actualizados
        return ListarRestauranteResponse(
            proveedor=ListarDatosProveedor(**db_proveedor.__dict__),
            restaurante=ListarDatosRestaurante(**db_restaurante.__dict__)
        )

    except Exception as e:
        logger.error(f"Error al actualizar restaurante: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al actualizar el restaurante"
        )

@restaurantes.delete("/restaurantes/eliminar/{id_restaurante}", response_model=ResponseMessage)
async def eliminar_restaurante(id_restaurante: str, db: Session = Depends(get_db)):
    
    try:
        uuid_obj = UUID(id_restaurante)
        
        db_proveedor = db.query(ProveedorModel)\
            .filter(ProveedorModel.id_proveedor == id_restaurante).first()

        if not db_proveedor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurante no encontrado"
            )
        if db_proveedor.activo == False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El restaurante ya ha sido eliminado"
            )  
        try:
            db_proveedor.activo = False
            db.commit()
            return ResponseMessage(message="Restaurante eliminado exitosamente") 
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error en eliminación: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar el restaurante"
            )
    except (ValueError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El ID proporcionado no es un UUID válido"
        )

# Endpoint de Health Check
@restaurantes.get("/restaurantes/healthchecker")
def get_live():
    return {"message": "Restaurantes service is LIVE!!"}

# Endpoint de Readiness
@restaurantes.get("/restaurantes/readiness")
def check_readiness(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT 1")).fetchone()
        if result and result[0] == 1:
            return {"status": "Ready"}
        return {"status": "Not Ready"}
    except Exception as e:
        logger.error(f"Error en readiness check: {str(e)}")
        return {"status": "Not Ready"}