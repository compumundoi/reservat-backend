from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File, Form
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import select, and_, or_, func, text
from datetime import datetime, timedelta
import logging
import uuid
from uuid import UUID
from fastapi.responses import JSONResponse
from config.db2 import DB
from config.s3 import almacenamiento, detectar_tipo_imagen, AlmacenamientoNoConfigurado, TAMANO_MAXIMO_BYTES
from models.fotos_model import FotoModel, Servicio
from schemas.fotos_schema import DatosFoto, ActualizarFoto, RespuestaFoto, ResponseMessage, ResponseList
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

fotos = APIRouter()

def _con_nombre_servicio(foto, nombre=None):
    """Adjunta el nombre del servicio a la respuesta de la foto."""
    datos = RespuestaFoto.model_validate(foto).model_dump()
    datos["servicio_nombre"] = nombre
    return RespuestaFoto(**datos)


def _listar_con_servicio(db, filtros, skip, limite):
    """Lista fotos junto al nombre de su servicio.

    LEFT OUTER JOIN para que una foto siga listandose aunque su servicio
    no se pueda resolver; el nombre viaja vacio en ese caso.
    """
    filas = (
        db.query(FotoModel, Servicio.nombre)
        .outerjoin(Servicio, FotoModel.servicio_id == Servicio.id_servicio)
        .filter(*filtros)
        .offset(skip)
        .limit(limite)
        .all()
    )
    return [_con_nombre_servicio(f, nombre) for f, nombre in filas]


@fotos.post("/fotos/crear/", response_model=ResponseMessage)
async def crear_foto(foto: DatosFoto, db: Session = Depends(get_db)):
    """Crea un nuevas fotos  en la base de datos"""
    existing_url = db.query(FotoModel).filter(FotoModel.url == foto.url).first()
    existing_servicio = db.query(Servicio).filter(and_(Servicio.id_servicio == foto.servicio_id)).first()

    if existing_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="la URL de la foto ya existe"
        )
    if existing_servicio is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="el servicio no existe"
        )
    try:
        nuevo_foto = FotoModel(**foto.model_dump())
        db.add(nuevo_foto)
        db.commit()
        db.refresh(nuevo_foto)
        return ResponseMessage(message="Foto creada exitosamente")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error en registro: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear la foto"
        )

@fotos.post("/fotos/subir/", response_model=RespuestaFoto, status_code=status.HTTP_201_CREATED)
async def subir_foto(
    archivo: UploadFile = File(...),
    servicio_id: UUID = Form(...),
    descripcion: str = Form(""),
    orden: int = Form(0),
    es_portada: bool = Form(False),
    eliminado: bool = Form(False),
    fecha_subida: Optional[datetime] = Form(None),
    db: Session = Depends(get_db),
):
    """Sube la imagen al bucket S3 y registra la foto con la URL resultante."""
    if not almacenamiento.configurado:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El almacenamiento de imagenes no esta configurado"
        )

    existing_servicio = db.query(Servicio).filter(Servicio.id_servicio == servicio_id).first()
    if existing_servicio is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="el servicio no existe"
        )

    # Se lee un byte de mas para detectar el exceso sin cargar archivos enormes.
    contenido = await archivo.read(TAMANO_MAXIMO_BYTES + 1)
    if len(contenido) > TAMANO_MAXIMO_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"La imagen supera el maximo de {TAMANO_MAXIMO_BYTES // (1024 * 1024)} MB"
        )
    if not contenido:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo esta vacio"
        )

    content_type = detectar_tipo_imagen(contenido)
    if content_type is None:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Formato no soportado. Usa JPG, PNG, WEBP o GIF"
        )

    try:
        clave, url = almacenamiento.subir(contenido, content_type, servicio_id)
    except AlmacenamientoNoConfigurado:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El almacenamiento de imagenes no esta configurado"
        )
    except Exception as e:
        logger.error(f"Error subiendo imagen a S3: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="No se pudo subir la imagen al almacenamiento"
        )

    try:
        nueva_foto = FotoModel(
            servicio_id=servicio_id,
            url=url,
            descripcion=descripcion,
            orden=orden,
            es_portada=es_portada,
            eliminado=eliminado,
            fecha_subida=fecha_subida or datetime.utcnow(),
        )
        db.add(nueva_foto)
        db.commit()
        db.refresh(nueva_foto)
        return _con_nombre_servicio(nueva_foto, existing_servicio.nombre)
    except Exception as e:
        db.rollback()
        # Sin registro en BD el objeto quedaria huerfano en el bucket.
        almacenamiento.borrar(clave)
        logger.error(f"Error registrando foto subida: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear la foto"
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
        FotoModel.descripcion,
        FotoModel.url,
        Servicio.nombre,
    )
    return or_(*[func.unaccent(campo).ilike(patron) for campo in campos])


@fotos.get("/fotos/listar/", response_model=ResponseList)
async def listar_fotos(
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
        filtros = [FotoModel.eliminado == False]
        filtro_texto = _filtro_busqueda(busqueda)
        if filtro_texto is not None:
            filtros.append(filtro_texto)

        # El conteo repite el outerjoin porque la busqueda toca el nombre
        # del servicio, que vive en la otra tabla.
        total = (
            db.query(FotoModel)
            .outerjoin(Servicio, FotoModel.servicio_id == Servicio.id_servicio)
            .filter(*filtros)
            .count()
        )
        fotos = _listar_con_servicio(db, filtros, skip, limite)
        
        return ResponseList(
            fotos=fotos,
            total=total,
            page=pagina,
            size=limite
        )
        
    except Exception as e:
        logger.error(f"Error en listado: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al listar las fotos"
        )

@fotos.get("/fotos/servicios/{id_servicio}", response_model=ResponseList)
async def listar_fotos(id_servicio: str, pagina: int = 0, limite: int = 100, db: Session = Depends(get_db)):
    """Lista todas las fechas bloqueadas con paginación"""
   
    existing_servicio = db.query(Servicio).filter(and_(Servicio.id_servicio == id_servicio)).first()

    if existing_servicio is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="el servicio no existe"
        )
    try:
        # (pagina - 1) * pagina no paginaba: repetia la primera pagina y
        # saltaba registros. El frontend envia paginas 0-based.
        skip = max(0, pagina) * limite
        total = db.query(FotoModel).filter(FotoModel.eliminado == False, FotoModel.servicio_id == id_servicio).count()
        fotos = _listar_con_servicio(
            db,
            [FotoModel.eliminado == False, FotoModel.servicio_id == id_servicio],
            skip,
            limite,
        )
        
        return ResponseList(
            fotos=fotos,
            total=total,
            page=pagina,
            size=limite
        )
        
    except Exception as e:
        logger.error(f"Error en listado: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al listar las fotos para el servicio: " + id_servicio
        )

@fotos.get("/fotos/consultar/{id_foto}", response_model=RespuestaFoto)
async def consultar_foto(id_foto: str, db: Session = Depends(get_db)):
    """Consulta un mayorista específico por su ID"""
    try:
        uuid_obj = UUID(id_foto)

        db_foto = db.query(FotoModel).filter(FotoModel.id == id_foto).filter(FotoModel.eliminado == False).first()

        if db_foto is None:
            raise HTTPException(status_code=404, detail="Foto no encontrado")

        return db_foto

    except (ValueError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El ID proporcionado no es un UUID válido"
        )
    
@fotos.put("/fotos/editar/{id_foto}", response_model=RespuestaFoto)
async def actualizar_foto(id_foto: str, datos: ActualizarFoto, db: Session = Depends(get_db)):
    """Actualiza los datos de una fecha bloqueada existente"""

    db_foto = db.query(FotoModel).filter(FotoModel.id == id_foto).filter(FotoModel.eliminado == False).first()
    if db_foto is None:
        raise HTTPException(status_code=404, detail="Foto no encontrado")

    existing_servicio = db.query(Servicio).filter(and_(Servicio.id_servicio == datos.servicio_id)).first()
    if existing_servicio is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="el servicio no existe"
        )
    
    for key, value in datos.model_dump(exclude_unset=True).items():
        setattr(db_foto, key, value)

    db.commit()
    db.refresh(db_foto)
    # "Marcar como eliminada" desde el formulario de edicion tambien es un borrado.
    if db_foto.eliminado:
        almacenamiento.borrar_por_url(db_foto.url)
    return db_foto

@fotos.delete("/fotos/eliminar/{id_foto}", response_model=ResponseMessage)
async def eliminar_foto(id_foto: str, db: Session = Depends(get_db)):
    
    try:
        uuid_obj = UUID(id_foto)
        db_fecha = db.query(FotoModel).filter(FotoModel.id == id_foto).first()
        if not db_fecha:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Foto no encontrada"
            )
        if db_fecha.eliminado:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La foto ya ha sido eliminada"
            )  
        try:
            db_fecha.eliminado = True
            db.commit()
            # Primero la BD: si falla S3 queda un objeto huerfano (se registra en
            # el log), nunca una foto activa apuntando a un archivo inexistente.
            almacenamiento.borrar_por_url(db_fecha.url)
            return ResponseMessage(message="Foto eliminada exitosamente")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error en eliminación: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar la foto"
            )
    except (ValueError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El ID proporcionado no es un UUID válido"
        )

# Endpoint de Health Check
@fotos.get("/fotos/healthchecker")
def get_live():
    return {"message": "Fotos service is LIVE!!"}

# Endpoint de Readiness
@fotos.get("/fotos/readiness")
def check_readiness(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT 1")).fetchone()
        if result and result[0] == 1:
            return {"status": "Ready"}
        return {"status": "Not Ready"}
    except Exception as e:
        logger.error(f"Error en readiness check: {str(e)}")
        return {"status": "Not Ready"}