from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import select, and_, or_, func, text
from datetime import datetime, timedelta
import logging
import uuid
from uuid import UUID
from fastapi.responses import JSONResponse
from config.db2 import DB
from models.experiencias_model import ExperienciaModel, ProveedorModel, UsuarioModel
from schemas.experiencias_schema import DatosExperiencia, CrearExperienciaRequest, ResponseMessage, ResponseList, DatosProveedor, ListarExperienciaResponse, ListarDatosProveedor, ListarDatosExperiencia
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

experiencias = APIRouter()

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

@experiencias.post("/experiencias/crear/", response_model=ResponseMessage)
async def crear_experiencia(request: CrearExperienciaRequest, db: Session = Depends(get_db)):
    """Crea un nuevo restaurante y su proveedor asociado en la base de datos"""
    
    # El alta se hace sobre un usuario proveedor que ya existe en el sistema.
    usuario = db.query(UsuarioModel).filter(
        UsuarioModel.email == request.proveedor.email,
        UsuarioModel.tipo_usuario == "proveedor",
        UsuarioModel.activo == True,
    ).first()

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo no corresponde a un usuario proveedor activo"
        )

    # Un usuario proveedor puede tener un solo registro asociado.
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
        # La ubicacion en texto nunca se toma del cliente: se deriva del
        # municipio elegido para que no entren ciudades inventadas.
        proveedor_datos.update(
            campos_ubicacion(db, proveedor_datos.get("municipio_id"))
        )
        nuevo_proveedor = crear_registro(ProveedorModel, proveedor_datos, nuevo_uuid)
        db.add(nuevo_proveedor)
        db.commit()
        
        # Crear y guardar experiencia
        experiencia_datos = request.experiencia.model_dump()
        nuevo_experiencia = crear_registro(ExperienciaModel, experiencia_datos, nuevo_uuid)
        db.add(nuevo_experiencia)
        db.commit()
        
        return ResponseMessage(message="Proveedor y experiencia creados exitosamente")
        
    except HTTPException:
        # Un municipio inexistente es un 400 del cliente, no un 500.
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error en registro: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear el proveedor y experiencia"
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
        ProveedorModel.nombre,
        ProveedorModel.email,
        ProveedorModel.ciudad,
        ProveedorModel.pais,
        ProveedorModel.descripcion,
        ExperienciaModel.idioma,
        ExperienciaModel.dificultad,
        ExperienciaModel.punto_de_encuentro,
    )
    return or_(*[func.unaccent(campo).ilike(patron) for campo in campos])


@experiencias.get("/experiencias/listar/", response_model=ResponseList)
async def listar_experiencias(
    pagina: int = 1,
    limite: int = 100,
    busqueda: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Lista todos los restaurantes con su información de proveedor"""
    try:
        pagina = max(1, pagina)
        skip = (pagina - 1) * limite

        query = db.query(ExperienciaModel, ProveedorModel)\
            .join(ProveedorModel, ExperienciaModel.id_experiencia == ProveedorModel.id_proveedor)\
            .filter(ProveedorModel.activo == True)

        # El mismo filtro va al conteo y a la pagina: filtrar solo la pagina
        # dejaria mintiendo al total y al numero de paginas.
        filtro_texto = _filtro_busqueda(busqueda)
        if filtro_texto is not None:
            query = query.filter(filtro_texto)

        total = query.count()
        print("Total de experiencias:", total)
    
        resultados = query.offset(skip).limit(limite).all()

        lista_respuesta = []

        for experiencia, proveedor in resultados:

            proveedor_dict = proveedor.__dict__.copy()
            experiencia_dict = experiencia.__dict__.copy()

            item = ListarExperienciaResponse(
                proveedor=ListarDatosProveedor(**proveedor_dict),
                experiencia=ListarDatosExperiencia(**experiencia_dict)
            )
            lista_respuesta.append(item)

        return ResponseList(
            data=lista_respuesta,
            total=total,
            page=pagina,
            size=limite
        )

    except HTTPException:
        # Un municipio inexistente es un 400 del cliente, no un 500.
        raise
    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail="Error al listar experiencias")

@experiencias.get("/experiencias/consultar/{id_experiencia}", response_model=ListarExperienciaResponse)
async def listar_experiencias(id_experiencia: str,db: Session = Depends(get_db)):
    """Lista todos los restaurantes con su información de proveedor"""
    try:

        query = db.query(ExperienciaModel, ProveedorModel)\
            .join(ProveedorModel, ExperienciaModel.id_experiencia == ProveedorModel.id_proveedor)\
            .filter(ProveedorModel.activo == True, ExperienciaModel.id_experiencia == id_experiencia)

        resultados = query.all()

        if not resultados:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="restaurante no encontrado")

        try:
            for experiencia, proveedor in resultados:
                proveedor_dict = proveedor.__dict__.copy()
                experiencia_dict = experiencia.__dict__.copy()

            return ListarExperienciaResponse(
                    proveedor=ListarDatosProveedor(**proveedor_dict),
                    experiencia=ListarDatosExperiencia(**experiencia_dict)
                )
        except HTTPException:
            # Un municipio inexistente es un 400 del cliente, no un 500.
            raise
        except Exception as e:
            print("Error:", e)
            raise HTTPException(status_code=500, detail="Error al listar experiencias")

    except HTTPException:
        # Un municipio inexistente es un 400 del cliente, no un 500.
        raise
    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail="Error al listar experiencias")
   
@experiencias.put("/experiencias/editar/{id_experiencia}", response_model=ListarExperienciaResponse)
async def actualizar_experiencia(id_experiencia: str, datos: CrearExperienciaRequest, db: Session = Depends(get_db)):
    """Actualiza los datos de un restaurante y su proveedor"""
    try:
        # Obtener el restaurante y proveedor existentes
        db_experiencia, db_proveedor = db.query(ExperienciaModel, ProveedorModel)\
            .join(ProveedorModel, ExperienciaModel.id_experiencia == ProveedorModel.id_proveedor)\
            .filter(ProveedorModel.activo == True, ExperienciaModel.id_experiencia == id_experiencia).first()
        
        if db_experiencia is None:
            raise HTTPException(status_code=404, detail="Experiencia no encontrada")

        # Actualizar los campos del restaurante
        for key, value in datos.experiencia.model_dump(exclude_unset=True).items():
            setattr(db_experiencia, key, value)

        # Actualizar los campos del proveedor
        cambios_proveedor = datos.proveedor.model_dump(exclude_unset=True)
        # Si viene municipio_id se recalcula toda la ubicacion; si no, se
        # ignoran los campos de texto para que nadie los pise a mano.
        if cambios_proveedor.get("municipio_id") is not None:
            cambios_proveedor.update(
                campos_ubicacion(db, cambios_proveedor["municipio_id"])
            )
        else:
            for campo in ("ciudad", "departamento", "pais", "pais_id", "departamento_id"):
                cambios_proveedor.pop(campo, None)

        for key, value in cambios_proveedor.items():
            setattr(db_proveedor, key, value)

        # Guardar cambios
        db.commit()
        
        # Refrescar los objetos
        db.refresh(db_experiencia)
        db.refresh(db_proveedor)

        # Devolver la respuesta con los datos actualizados
        return ListarExperienciaResponse(
            proveedor=ListarDatosProveedor(**db_proveedor.__dict__),
            experiencia=ListarDatosExperiencia(**db_experiencia.__dict__)
        )

    except HTTPException:
        # Un municipio inexistente es un 400 del cliente, no un 500.
        raise
    except Exception as e:
        logger.error(f"Error al actualizar restaurante: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al actualizar la experiencia"
        )

@experiencias.delete("/experiencias/eliminar/{id_experiencia}", response_model=ResponseMessage)
async def eliminar_experiencia(id_experiencia: str, db: Session = Depends(get_db)):
    
    try:
        uuid_obj = UUID(id_experiencia)
        
        db_proveedor = db.query(ProveedorModel)\
            .filter(ProveedorModel.id_proveedor == id_experiencia).first()

        if not db_proveedor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Experiencia no encontrada"
            )
        if db_proveedor.activo == False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La experiencia ya ha sido eliminada"
            )  
        try:
            db_proveedor.activo = False
            db.commit()
            return ResponseMessage(message="Experiencia eliminada exitosamente") 
            
        except HTTPException:
            # Un municipio inexistente es un 400 del cliente, no un 500.
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error en eliminación: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar la experiencia"
            )
    except (ValueError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El ID proporcionado no es un UUID válido"
        )
# Endpoint de Health Check
@experiencias.get("/experiencias/healthchecker")
def get_live():
    return {"message": "experiencias service is LIVE!!"}

# Endpoint de Readiness
@experiencias.get("/experiencias/readiness")
def check_readiness(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT 1")).fetchone()
        if result and result[0] == 1:
            return {"status": "Ready"}
        return {"status": "Not Ready"}
    except HTTPException:
        # Un municipio inexistente es un 400 del cliente, no un 500.
        raise
    except Exception as e:
        logger.error(f"Error en readiness check: {str(e)}")
        return {"status": "Not Ready"}