from fastapi import APIRouter, HTTPException, Depends, status, Request, BackgroundTasks
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import select, and_, text, func
from datetime import datetime, timedelta, date, timezone
import json
import logging
import uuid
from uuid import UUID
from fastapi.responses import JSONResponse
from config.db2 import DB
from config.notificaciones import enviar_correos_de_reserva
from config.precios import calcular_total
from config.auth import (
    obtener_usuario_actual,
    exigir_administrador,
    exigir_propietario_o_admin,
    es_administrador,
    ROL_MAYORISTA,
)
from models.reservas_model import (
    ReservaModel,
    ServicioModel,
    ProveedorModel,
    MayoristaModel,
    FechaBloqueadaModel,
    ESTADO_PENDIENTE,
    ESTADO_APROBADA,
    ESTADO_RECHAZADA,
    ESTADOS_VALIDOS,
)
from schemas.reservas_schema import (
    DatosReserva,
    ActualizarReserva,
    AprobarReserva,
    RechazarReserva,
    RespuestaReserva,
    ResponseMessage,
    ResponseList,
)
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

reservas = APIRouter()


def cargar_nombres(reservas, db: Session) -> dict:
    """Nombres de proveedor, mayorista y servicio de un lote de reservas.

    Se resuelven en dos consultas para todo el lote y no una por reserva:
    un listado de 100 reservas haria 300 consultas de otro modo.
    """
    ids_proveedor = {str(r.id_proveedor) for r in reservas if r.id_proveedor}
    ids_mayorista = {str(r.id_mayorista) for r in reservas if r.id_mayorista}

    proveedores = {}
    if ids_proveedor:
        proveedores = {
            str(p.id_proveedor): p.nombre
            for p in db.query(ProveedorModel)
            .filter(ProveedorModel.id_proveedor.in_(ids_proveedor))
            .all()
        }

    mayoristas = {}
    if ids_mayorista:
        mayoristas = {
            str(m.id): " ".join(filter(None, [m.nombre, m.apellidos])).strip()
            for m in db.query(MayoristaModel)
            .filter(MayoristaModel.id.in_(ids_mayorista))
            .all()
        }

    return {"proveedores": proveedores, "mayoristas": mayoristas}


def serializar_reserva(reserva: ReservaModel, nombres: dict = None) -> dict:
    """Representacion JSON de una reserva, unica para todos los endpoints.

    `nombres` viene de cargar_nombres(); sin el, los nombres salen vacios y
    el cliente muestra el identificador como respaldo.
    """
    nombres = nombres or {}
    id_proveedor = str(reserva.id_proveedor) if reserva.id_proveedor else None
    id_mayorista = str(reserva.id_mayorista) if reserva.id_mayorista else None

    return {
        "id": str(reserva.id_reserva),
        "id_proveedor": id_proveedor,
        "id_servicio": str(reserva.id_servicio) if reserva.id_servicio else None,
        "id_mayorista": id_mayorista,
        "nombre_proveedor": nombres.get("proveedores", {}).get(id_proveedor),
        "nombre_mayorista": nombres.get("mayoristas", {}).get(id_mayorista),
        "nombre_servicio": reserva.nombre_servicio,
        "descripcion": reserva.descripcion,
        "tipo_servicio": reserva.tipo_servicio,
        "precio": reserva.precio,
        "ciudad": reserva.ciudad,
        "activo": reserva.activo,
        "estado": reserva.estado,
        "observaciones": reserva.observaciones,
        "fecha_creacion": reserva.fecha_creacion,
        "fecha_inicio": reserva.fecha_inicio,
        "fecha_fin": reserva.fecha_fin,
        "cantidad": reserva.cantidad,
        "hora": reserva.hora.strftime("%H:%M") if reserva.hora else None,
        "total": calcular_total(reserva),
        "motivo_rechazo": reserva.motivo_rechazo,
        "fecha_decision": reserva.fecha_decision,
        "id_admin_decision": (
            str(reserva.id_admin_decision) if reserva.id_admin_decision else None
        ),
    }


def notificar_cambio_de_estado(
    reserva: ReservaModel,
    evento: str,
    db: Session,
    tareas: BackgroundTasks = None,
) -> None:
    """Punto unico de enganche para las notificaciones por correo.

    Se invoca siempre DESPUES del commit: un fallo notificando no puede
    deshacer una reserva ya persistida. Y se despacha en segundo plano para
    que quien reserva no espere a que salgan tres correos.
    """
    logger.info(
        "Evento de reserva '%s' para %s (estado=%s)",
        evento,
        reserva.id_reserva,
        reserva.estado,
    )

    if tareas is not None:
        tareas.add_task(enviar_correos_de_reserva, reserva, evento, db)
    else:
        enviar_correos_de_reserva(reserva, evento, db)


# Tipos que se reservan por rango de fechas; el resto va por fecha y hora.
TIPOS_POR_RANGO = ("alojamiento", "hoteles", "hotel")


def capacidad_del_servicio(servicio: ServicioModel):
    """Capacidad declarada en detalles_del_servicio, o None si no la trae.

    El campo es texto libre: en algunos servicios es un JSON con 'capacidad'
    y en otros es una descripcion suelta. Sin un numero utilizable no se
    valida nada, para no rechazar reservas por un dato que el proveedor
    nunca cargo.
    """
    detalles = getattr(servicio, "detalles_del_servicio", None)
    if not detalles:
        return None

    try:
        datos = json.loads(detalles)
    except (TypeError, ValueError):
        return None

    if not isinstance(datos, dict):
        return None

    capacidad = datos.get("capacidad")
    try:
        capacidad = int(capacidad)
    except (TypeError, ValueError):
        return None

    return capacidad if capacidad > 0 else None


def exigir_capacidad_suficiente(servicio: ServicioModel, cantidad: int) -> None:
    capacidad = capacidad_del_servicio(servicio)
    if capacidad is not None and cantidad > capacidad:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"El servicio admite hasta {capacidad} persona(s) y se "
                f"solicitaron {cantidad}."
            ),
        )


def exigir_fechas_disponibles(
    id_servicio: str, fecha_inicio, fecha_fin, db: Session
) -> None:
    """Rechaza la reserva si el proveedor bloqueo alguna fecha del rango.

    Se valida aca y no solo en el cliente: el bloqueo puede cargarse entre
    que el mayorista abre la ficha y confirma la solicitud.
    """
    if fecha_inicio is None:
        return

    fin = fecha_fin or fecha_inicio

    bloqueos = (
        db.query(FechaBloqueadaModel)
        .filter(FechaBloqueadaModel.servicio_id == id_servicio)
        .filter(FechaBloqueadaModel.bloqueo_activo == True)
        .filter(func.date(FechaBloqueadaModel.fecha) >= fecha_inicio)
        .filter(func.date(FechaBloqueadaModel.fecha) <= fin)
        .all()
    )

    if bloqueos:
        fechas = sorted({b.fecha.date().isoformat() for b in bloqueos})
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "El servicio no esta disponible en estas fechas: "
                + ", ".join(fechas)
            ),
        )


def obtener_reserva_o_404(id_reserva: str, db: Session) -> ReservaModel:
    """Busca una reserva validando previamente que el ID sea un UUID."""
    try:
        _ = UUID(id_reserva)
    except (ValueError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El ID de la reserva no es un UUID valido",
        )

    reserva = (
        db.query(ReservaModel).filter(ReservaModel.id_reserva == id_reserva).first()
    )
    if reserva is None:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    return reserva


def exigir_reserva_pendiente(reserva: ReservaModel, accion: str) -> None:
    """Solo una reserva pendiente admite una decision del administrador."""
    if reserva.estado != ESTADO_PENDIENTE:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"No se puede {accion} la reserva porque ya esta "
                f"'{reserva.estado}'. Solo las reservas pendientes admiten "
                "una decision."
            ),
        )

@reservas.post("/reservas/crear")
async def crear_reserva(
    datos: DatosReserva,
    tareas: BackgroundTasks,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual),
):
    """Crea una nueva reserva validando proveedor y mayorista"""
    # Un mayorista solo reserva a su propio nombre: el id sale del token y no
    # del cuerpo, que el cliente puede escribir a voluntad. El administrador
    # sí puede cargar una reserva para otro.
    if usuario["tipo_usuario"] == ROL_MAYORISTA:
        datos.id_mayorista = usuario["id"]
    elif not es_administrador(usuario):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo un mayorista puede solicitar reservas",
        )

    try:
        # Validar existencia de proveedor
        prov = db.query(ProveedorModel).filter(ProveedorModel.id_proveedor == str(datos.id_proveedor)).first()
        if prov is None or (hasattr(ProveedorModel, "activo") and prov.activo is not None and prov.activo is False):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proveedor no encontrado o inactivo")

        # Validar existencia de mayorista (opcional si viene)
        if datos.id_mayorista is not None:
            may = db.query(MayoristaModel).filter(MayoristaModel.id == str(datos.id_mayorista)).first()
            if may is None or (hasattr(MayoristaModel, "activo") and may.activo is not None and may.activo is False):
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mayorista no encontrado o inactivo")

        # Validar existencia de servicio
        serv = db.query(ServicioModel).filter(ServicioModel.id_servicio == str(datos.id_servicio)).first()
        if serv is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Servicio no encontrado")

        exigir_capacidad_suficiente(serv, datos.cantidad)
        exigir_fechas_disponibles(
            str(datos.id_servicio), datos.fecha_inicio, datos.fecha_fin, db
        )

        # La hora solo tiene sentido donde se reserva un turno; en alojamiento
        # el rango de fechas ya define la estadia.
        tipo = str(datos.tipo_servicio or "").lower()
        if tipo in TIPOS_POR_RANGO:
            hora_val = None
        else:
            if datos.hora is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La hora es obligatoria para este tipo de servicio",
                )
            hora_val = datos.hora

        # Normalizar tipos según esquema real de BD
        precio_str = str(datos.precio) if datos.precio is not None else None
        # activo ahora es booleano
        activo_val = bool(getattr(datos, 'activo', True))
        # fechas
        fecha_crea = datos.fecha_creacion.date() if hasattr(datos, 'fecha_creacion') and datos.fecha_creacion else None
        fecha_inicio_val = datos.fecha_inicio if hasattr(datos, 'fecha_inicio') else None
        fecha_fin_val = datos.fecha_fin if hasattr(datos, 'fecha_fin') else None

        nueva = ReservaModel(
            id_proveedor=str(datos.id_proveedor),
            id_servicio=str(datos.id_servicio),
            id_mayorista=str(datos.id_mayorista) if datos.id_mayorista is not None else None,
            nombre_servicio=datos.nombre_servicio,
            descripcion=datos.descripcion,
            tipo_servicio=datos.tipo_servicio,
            precio=precio_str,
            ciudad=datos.ciudad,
            activo=activo_val,
            # El estado no lo decide el cliente: toda reserva nace pendiente
            # y solo un administrador la mueve con aprobar/rechazar.
            estado=ESTADO_PENDIENTE,
            observaciones=datos.observaciones,
            fecha_creacion=fecha_crea,
            fecha_inicio=fecha_inicio_val,
            fecha_fin=fecha_fin_val,
            hora=hora_val,
            cantidad=datos.cantidad,
        )

        db.add(nueva)
        db.commit()
        db.refresh(nueva)

        notificar_cambio_de_estado(nueva, "reserva_creada", db, tareas)

        return {
            "message": "Reserva creada exitosamente",
            "id_reserva": str(nueva.id_reserva),
            "estado": nueva.estado,
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error al crear reserva: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear la reserva")

@reservas.get("/reservas/listar/")
async def listar_reservas(
    pagina: int = 1,
    limite: int = 100,
    estado: Optional[str] = None,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual),
):
    """Lista todas las reservas con paginación, opcionalmente por estado"""
    # El listado completo cruza a todos los mayoristas y proveedores.
    exigir_administrador(usuario)

    if estado is not None and estado not in ESTADOS_VALIDOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estado invalido. Valores permitidos: {', '.join(ESTADOS_VALIDOS)}",
        )

    try:
        if pagina < 1:
            pagina = 1
        if limite < 1:
            limite = 100
        skip = (pagina - 1) * limite

        base_query = db.query(ReservaModel).filter(ReservaModel.activo == True)
        if estado is not None:
            base_query = base_query.filter(ReservaModel.estado == estado)
        total = base_query.count()
        reservas_db = base_query.offset(skip).limit(limite).all()

        # Serialización manual para evitar inconsistencias de schema
        nombres = cargar_nombres(reservas_db, db)
        reservas_list = [serializar_reserva(r, nombres) for r in reservas_db]

        return {
            "reservas": reservas_list,
            "total": total,
            "page": pagina,
            "size": limite,
        }

    except Exception as e:
        logger.error(f"Error en listado: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al listar las reservas",
        )


@reservas.get("/reservas/listar/proveedor/{id_proveedor}")
async def listar_reservas_por_proveedor(
    id_proveedor: str,
    pagina: int = 1,
    limite: int = 100,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual),
):
    """Lista reservas por proveedor con paginación"""
    exigir_propietario_o_admin(usuario, id_proveedor)

    try:
        # Validar UUID
        _ = UUID(id_proveedor)

        if pagina < 1:
            pagina = 1
        if limite < 1:
            limite = 100
        skip = (pagina - 1) * limite

        base_query = (
            db.query(ReservaModel)
            .filter(ReservaModel.id_proveedor == id_proveedor)
            .filter(ReservaModel.activo == True)
        )
        total = base_query.count()
        reservas_db = base_query.offset(skip).limit(limite).all()

        nombres = cargar_nombres(reservas_db, db)
        reservas_list = [serializar_reserva(r, nombres) for r in reservas_db]

        return {
            "reservas": reservas_list,
            "total": total,
            "page": pagina,
            "size": limite,
        }
    except (ValueError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El ID de proveedor no es un UUID válido",
        )
    except Exception as e:
        logger.error(f"Error al listar por proveedor: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al listar reservas por proveedor",
        )


@reservas.get("/reservas/listar/mayorista/{id_mayorista}")
async def listar_reservas_por_mayorista(
    id_mayorista: str,
    pagina: int = 1,
    limite: int = 100,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual),
):
    """Lista reservas por mayorista con paginación"""
    exigir_propietario_o_admin(usuario, id_mayorista)

    try:
        # Validar UUID
        _ = UUID(id_mayorista)

        if pagina < 1:
            pagina = 1
        if limite < 1:
            limite = 100
        skip = (pagina - 1) * limite

        base_query = (
            db.query(ReservaModel)
            .filter(ReservaModel.id_mayorista == id_mayorista)
            .filter(ReservaModel.activo == True)
        )
        total = base_query.count()
        reservas_db = base_query.offset(skip).limit(limite).all()

        nombres = cargar_nombres(reservas_db, db)
        reservas_list = [serializar_reserva(r, nombres) for r in reservas_db]

        return {
            "reservas": reservas_list,
            "total": total,
            "page": pagina,
            "size": limite,
        }
    except (ValueError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El ID de mayorista no es un UUID válido",
        )
    except Exception as e:
        logger.error(f"Error al listar por mayorista: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al listar reservas por mayorista",
        )


@reservas.patch("/reservas/{id_reserva}/aprobar")
async def aprobar_reserva(
    id_reserva: str,
    tareas: BackgroundTasks,
    datos: AprobarReserva = AprobarReserva(),
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual),
):
    """Un administrador aprueba una reserva pendiente"""
    exigir_administrador(usuario)
    reserva = obtener_reserva_o_404(id_reserva, db)
    exigir_reserva_pendiente(reserva, "aprobar")

    try:
        reserva.estado = ESTADO_APROBADA
        reserva.motivo_rechazo = None
        reserva.fecha_decision = datetime.now(timezone.utc)
        # Quien decide es quien esta autenticado, no lo que diga el cuerpo.
        reserva.id_admin_decision = usuario["id"]

        db.commit()
        db.refresh(reserva)
    except Exception as e:
        db.rollback()
        logger.error(f"Error al aprobar reserva: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al aprobar la reserva",
        )

    notificar_cambio_de_estado(reserva, "reserva_aprobada", db, tareas)

    return {
        "message": "Reserva aprobada exitosamente",
        "reserva": serializar_reserva(reserva, cargar_nombres([reserva], db)),
    }


@reservas.patch("/reservas/{id_reserva}/rechazar")
async def rechazar_reserva(
    id_reserva: str,
    datos: RechazarReserva,
    tareas: BackgroundTasks,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual),
):
    """Un administrador rechaza una reserva pendiente indicando el motivo"""
    exigir_administrador(usuario)
    reserva = obtener_reserva_o_404(id_reserva, db)
    exigir_reserva_pendiente(reserva, "rechazar")

    try:
        reserva.estado = ESTADO_RECHAZADA
        reserva.motivo_rechazo = datos.motivo_rechazo
        reserva.fecha_decision = datetime.now(timezone.utc)
        # Quien decide es quien esta autenticado, no lo que diga el cuerpo.
        reserva.id_admin_decision = usuario["id"]

        db.commit()
        db.refresh(reserva)
    except Exception as e:
        db.rollback()
        logger.error(f"Error al rechazar reserva: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al rechazar la reserva",
        )

    notificar_cambio_de_estado(reserva, "reserva_rechazada", db, tareas)

    return {
        "message": "Reserva rechazada exitosamente",
        "reserva": serializar_reserva(reserva, cargar_nombres([reserva], db)),
    }


@reservas.put("/reservas/editar/{id_reserva}")
async def editar_reserva(
    id_reserva: str,
    datos: ActualizarReserva,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual),
):
    """Edita una reserva existente"""
    exigir_administrador(usuario)

    try:
        _ = UUID(id_reserva)
    except (ValueError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El ID de la reserva no es un UUID válido",
        )

    reserva = db.query(ReservaModel).filter(ReservaModel.id_reserva == id_reserva).first()
    if reserva is None:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")

    try:
        cambios = datos.model_dump(exclude_unset=True)
        # La transicion de estado tiene sus propios endpoints (aprobar /
        # rechazar), que son los que validan el flujo y dejan trazabilidad.
        # Editar no puede ser una puerta trasera para saltarselo.
        cambios.pop("estado", None)

        for key, value in cambios.items():
            # Asignación directa de campos del schema al modelo
            setattr(reserva, key, value)

        db.commit()
        db.refresh(reserva)

        return {"message": "Reserva actualizada exitosamente"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error al actualizar reserva: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al editar la reserva",
        )


@reservas.delete("/reservas/eliminar/{id_reserva}")
async def eliminar_reserva(
    id_reserva: str,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual),
):
    """Elimina lógicamente una reserva (activo = False)"""
    exigir_administrador(usuario)

    try:
        _ = UUID(id_reserva)
    except (ValueError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El ID de la reserva no es un UUID válido",
        )

    reserva = db.query(ReservaModel).filter(ReservaModel.id_reserva == id_reserva).first()
    if reserva is None:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")

    if getattr(reserva, "activo", True) is False:
        raise HTTPException(status_code=400, detail="La reserva ya está eliminada")

    try:
        # Eliminación lógica
        setattr(reserva, "activo", False)
        db.commit()
        return {"message": "Reserva eliminada exitosamente"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error al eliminar reserva: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al eliminar la reserva",
        )


@reservas.get("/reservas/consultar/{id_reserva}")
async def obtener_reserva(
    id_reserva: str,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obtener_usuario_actual),
):
    """Obtiene una reserva por su ID"""
    try:
        _ = UUID(id_reserva)
    except (ValueError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El ID de la reserva no es un UUID válido",
        )

    reserva = db.query(ReservaModel).filter(ReservaModel.id_reserva == id_reserva).first()
    if reserva is None:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")

    # La ve el administrador, el mayorista que la solicitó y el proveedor que
    # la debe atender. Nadie más.
    exigir_propietario_o_admin(usuario, reserva.id_mayorista, reserva.id_proveedor)

    return serializar_reserva(reserva, cargar_nombres([reserva], db))


# Endpoint de Health Check
@reservas.get("/reservas/healthchecker")
def get_live():
    return {"message": "Reservas service is LIVE!!"}

# Endpoint de Readiness
@reservas.get("/reservas/readiness")
def check_readiness(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT 1")).fetchone()
        if result and result[0] == 1:
            return {"status": "Ready"}
        return {"status": "Not Ready"}
    except Exception as e:
        logger.error(f"Error en readiness check: {str(e)}")
        return {"status": "Not Ready"}