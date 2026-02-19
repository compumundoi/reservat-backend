"""
MCP Server para ReservaT — Base de datos completa (SSE)
=======================================================
Servidor MCP seguro de solo lectura accesible por internet vía SSE.
Consulta TODAS las tablas de ReservaT (excepto usuarios).

Tablas disponibles:
  proveedores, experiencias, hoteles, restaurantes, servicios,
  fotos, rutas, viajes, fechas_bloqueadas, transportes, mayoristas, reservas

Ejecutar localmente:
    python server.py

El servidor arranca en http://0.0.0.0:8080/sse (configurable via MCP_HOST / MCP_PORT).

Conectar desde un cliente remoto:
    URL SSE:  http://<tu-ip-o-dominio>:8080/sse
"""

import json
import logging
import os
from datetime import date, datetime, time
from decimal import Decimal
from uuid import UUID as PyUUID

from mcp.server.fastmcp import FastMCP
from sqlalchemy import or_, func, inspect

from config import (
    get_db_session,
    validate_api_key,
    ProveedorModel,
    ExperienciaModel,
    HotelModel,
    RestauranteModel,
    ServicioModel,
    FotoModel,
    RutaModel,
    ViajeModel,
    FechaBloqueadaModel,
    TransporteModel,
    MayoristaModel,
    ReservaModel,
)

# ─── Logging ─────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
logger = logging.getLogger("mcp_reservat")

# ─── MCP Server ──────────────────────────────────────────────────────────────

MCP_HOST = os.getenv("MCP_HOST", "0.0.0.0")
MCP_PORT = int(os.getenv("MCP_PORT", "8080"))

mcp = FastMCP(
    "ReservaT Database",
    instructions=(
        "Servidor MCP para consultar la base de datos de ReservaT. "
        "Permite acceso de solo lectura a todas las tablas: proveedores, "
        "experiencias, hoteles, restaurantes, servicios, fotos, rutas, "
        "viajes, fechas_bloqueadas, transportes, mayoristas y reservas. "
        "Todas las tools requieren el parámetro 'api_key' para autenticación. "
        "La tabla de usuarios está EXCLUIDA por seguridad."
    ),
)

# ─── Helpers ─────────────────────────────────────────────────────────────────


def _json_serial(obj):
    """Serializa tipos especiales a JSON."""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, time):
        return obj.strftime("%H:%M:%S")
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, PyUUID):
        return str(obj)
    raise TypeError(f"Tipo no serializable: {type(obj)}")


def _model_to_dict(obj) -> dict:
    """Convierte un objeto SQLAlchemy a diccionario serializable."""
    result = {}
    for col in inspect(obj).mapper.column_attrs:
        value = getattr(obj, col.key)
        if isinstance(value, PyUUID):
            value = str(value)
        elif isinstance(value, (datetime, date)):
            value = value.isoformat() if value else None
        elif isinstance(value, time):
            value = value.strftime("%H:%M:%S") if value else None
        elif isinstance(value, Decimal):
            value = float(value)
        result[col.key] = value
    return result


def _check_auth(api_key: str) -> str | None:
    """Valida la API key. Retorna mensaje de error o None si es válida."""
    try:
        if not validate_api_key(api_key):
            return "❌ API key inválida. Acceso denegado."
    except ValueError as e:
        return f"❌ Error de configuración: {e}"
    return None


def _paginate_query(query, pagina: int, limite: int):
    """Aplica paginación a una query y retorna (resultados, total)."""
    pagina = max(1, pagina)
    limite = min(max(1, limite), 100)
    total = query.count()
    resultados = query.offset((pagina - 1) * limite).limit(limite).all()
    return resultados, total, pagina, limite


def _format_response(data, total=None, pagina=None, limite=None, **extra) -> str:
    """Formatea la respuesta como JSON."""
    response = {**extra}
    if total is not None:
        response.update({"total": total, "pagina": pagina, "limite": limite})
    response["data"] = data
    return json.dumps(response, ensure_ascii=False, indent=2, default=_json_serial)


# ══════════════════════════════════════════════════════════════════════════════
#  PROVEEDORES
# ══════════════════════════════════════════════════════════════════════════════


@mcp.tool()
def listar_proveedores(api_key: str, pagina: int = 1, limite: int = 20) -> str:
    """
    Lista todos los proveedores activos (hoteles, restaurantes, tours, transportes).

    Args:
        api_key: Clave de autenticación.
        pagina: Número de página (default: 1).
        limite: Resultados por página (max: 100, default: 20).
    """
    auth_error = _check_auth(api_key)
    if auth_error:
        return auth_error

    session = get_db_session()
    try:
        query = session.query(ProveedorModel).filter(ProveedorModel.activo == True)  # noqa
        resultados, total, pagina, limite = _paginate_query(query, pagina, limite)
        data = [_model_to_dict(r) for r in resultados]
        return _format_response(data, total, pagina, limite)
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"❌ Error al listar proveedores: {e}"
    finally:
        session.close()


@mcp.tool()
def buscar_proveedores(api_key: str, termino: str, tipo: str = "", pagina: int = 1, limite: int = 20) -> str:
    """
    Busca proveedores por nombre, ciudad, país o descripción. Opcionalmente filtra por tipo.

    Args:
        api_key: Clave de autenticación.
        termino: Texto a buscar.
        tipo: Filtrar por tipo: 'hotel', 'restaurante', 'tour', 'transporte' (vacío = todos).
        pagina: Número de página (default: 1).
        limite: Resultados por página (max: 100, default: 20).
    """
    auth_error = _check_auth(api_key)
    if auth_error:
        return auth_error

    session = get_db_session()
    try:
        pattern = f"%{termino}%"
        query = session.query(ProveedorModel).filter(
            ProveedorModel.activo == True,  # noqa
            or_(
                func.lower(ProveedorModel.nombre).like(func.lower(pattern)),
                func.lower(ProveedorModel.ciudad).like(func.lower(pattern)),
                func.lower(ProveedorModel.pais).like(func.lower(pattern)),
                func.lower(ProveedorModel.descripcion).like(func.lower(pattern)),
            ),
        )
        if tipo:
            query = query.filter(ProveedorModel.tipo == tipo)

        resultados, total, pagina, limite = _paginate_query(query, pagina, limite)
        data = [_model_to_dict(r) for r in resultados]
        return _format_response(data, total, pagina, limite, busqueda=termino, tipo_filtro=tipo or "todos")
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"❌ Error al buscar proveedores: {e}"
    finally:
        session.close()


# ══════════════════════════════════════════════════════════════════════════════
#  EXPERIENCIAS (proveedor + experiencia)
# ══════════════════════════════════════════════════════════════════════════════


@mcp.tool()
def listar_experiencias(api_key: str, pagina: int = 1, limite: int = 20) -> str:
    """
    Lista todas las experiencias turísticas activas con su proveedor.

    Args:
        api_key: Clave de autenticación.
        pagina: Número de página (default: 1).
        limite: Resultados por página (max: 100, default: 20).
    """
    auth_error = _check_auth(api_key)
    if auth_error:
        return auth_error

    session = get_db_session()
    try:
        query = (
            session.query(ExperienciaModel, ProveedorModel)
            .join(ProveedorModel, ExperienciaModel.id_experiencia == ProveedorModel.id_proveedor)
            .filter(ProveedorModel.activo == True)  # noqa
        )
        resultados, total, pagina, limite = _paginate_query(query, pagina, limite)
        data = [
            {"proveedor": _model_to_dict(prov), "experiencia": _model_to_dict(exp)}
            for exp, prov in resultados
        ]
        return _format_response(data, total, pagina, limite)
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"❌ Error al listar experiencias: {e}"
    finally:
        session.close()


@mcp.tool()
def consultar_experiencia(api_key: str, id_experiencia: str) -> str:
    """
    Consulta una experiencia específica por su UUID.

    Args:
        api_key: Clave de autenticación.
        id_experiencia: UUID de la experiencia.
    """
    auth_error = _check_auth(api_key)
    if auth_error:
        return auth_error

    session = get_db_session()
    try:
        result = (
            session.query(ExperienciaModel, ProveedorModel)
            .join(ProveedorModel, ExperienciaModel.id_experiencia == ProveedorModel.id_proveedor)
            .filter(ProveedorModel.activo == True, ExperienciaModel.id_experiencia == id_experiencia)  # noqa
            .first()
        )
        if not result:
            return f"❌ No se encontró la experiencia con ID: {id_experiencia}"
        exp, prov = result
        return _format_response({"proveedor": _model_to_dict(prov), "experiencia": _model_to_dict(exp)})
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"❌ Error: {e}"
    finally:
        session.close()


# ══════════════════════════════════════════════════════════════════════════════
#  HOTELES (proveedor + hotel)
# ══════════════════════════════════════════════════════════════════════════════


@mcp.tool()
def listar_hoteles(api_key: str, pagina: int = 1, limite: int = 20) -> str:
    """
    Lista todos los hoteles activos con su información de proveedor.

    Args:
        api_key: Clave de autenticación.
        pagina: Número de página (default: 1).
        limite: Resultados por página (max: 100, default: 20).
    """
    auth_error = _check_auth(api_key)
    if auth_error:
        return auth_error

    session = get_db_session()
    try:
        query = (
            session.query(HotelModel, ProveedorModel)
            .join(ProveedorModel, HotelModel.id_hotel == ProveedorModel.id_proveedor)
            .filter(ProveedorModel.activo == True)  # noqa
        )
        resultados, total, pagina, limite = _paginate_query(query, pagina, limite)
        data = [
            {"proveedor": _model_to_dict(prov), "hotel": _model_to_dict(h)}
            for h, prov in resultados
        ]
        return _format_response(data, total, pagina, limite)
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"❌ Error al listar hoteles: {e}"
    finally:
        session.close()


@mcp.tool()
def consultar_hotel(api_key: str, id_hotel: str) -> str:
    """
    Consulta un hotel específico por su UUID.

    Args:
        api_key: Clave de autenticación.
        id_hotel: UUID del hotel.
    """
    auth_error = _check_auth(api_key)
    if auth_error:
        return auth_error

    session = get_db_session()
    try:
        result = (
            session.query(HotelModel, ProveedorModel)
            .join(ProveedorModel, HotelModel.id_hotel == ProveedorModel.id_proveedor)
            .filter(ProveedorModel.activo == True, HotelModel.id_hotel == id_hotel)  # noqa
            .first()
        )
        if not result:
            return f"❌ No se encontró el hotel con ID: {id_hotel}"
        h, prov = result
        return _format_response({"proveedor": _model_to_dict(prov), "hotel": _model_to_dict(h)})
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"❌ Error: {e}"
    finally:
        session.close()


# ══════════════════════════════════════════════════════════════════════════════
#  RESTAURANTES (proveedor + restaurante)
# ══════════════════════════════════════════════════════════════════════════════


@mcp.tool()
def listar_restaurantes(api_key: str, pagina: int = 1, limite: int = 20) -> str:
    """
    Lista todos los restaurantes activos con su información de proveedor.

    Args:
        api_key: Clave de autenticación.
        pagina: Número de página (default: 1).
        limite: Resultados por página (max: 100, default: 20).
    """
    auth_error = _check_auth(api_key)
    if auth_error:
        return auth_error

    session = get_db_session()
    try:
        query = (
            session.query(RestauranteModel, ProveedorModel)
            .join(ProveedorModel, RestauranteModel.id_restaurante == ProveedorModel.id_proveedor)
            .filter(ProveedorModel.activo == True)  # noqa
        )
        resultados, total, pagina, limite = _paginate_query(query, pagina, limite)
        data = [
            {"proveedor": _model_to_dict(prov), "restaurante": _model_to_dict(r)}
            for r, prov in resultados
        ]
        return _format_response(data, total, pagina, limite)
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"❌ Error al listar restaurantes: {e}"
    finally:
        session.close()


@mcp.tool()
def consultar_restaurante(api_key: str, id_restaurante: str) -> str:
    """
    Consulta un restaurante específico por su UUID.

    Args:
        api_key: Clave de autenticación.
        id_restaurante: UUID del restaurante.
    """
    auth_error = _check_auth(api_key)
    if auth_error:
        return auth_error

    session = get_db_session()
    try:
        result = (
            session.query(RestauranteModel, ProveedorModel)
            .join(ProveedorModel, RestauranteModel.id_restaurante == ProveedorModel.id_proveedor)
            .filter(ProveedorModel.activo == True, RestauranteModel.id_restaurante == id_restaurante)  # noqa
            .first()
        )
        if not result:
            return f"❌ No se encontró el restaurante con ID: {id_restaurante}"
        r, prov = result
        return _format_response({"proveedor": _model_to_dict(prov), "restaurante": _model_to_dict(r)})
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"❌ Error: {e}"
    finally:
        session.close()


# ══════════════════════════════════════════════════════════════════════════════
#  SERVICIOS
# ══════════════════════════════════════════════════════════════════════════════


@mcp.tool()
def listar_servicios(api_key: str, tipo: str = "", ciudad: str = "", pagina: int = 1, limite: int = 20) -> str:
    """
    Lista todos los servicios activos. Filtra opcionalmente por tipo o ciudad.

    Args:
        api_key: Clave de autenticación.
        tipo: Filtrar por tipo_servicio: 'alojamiento', 'experiencias', 'restaurante' (vacío = todos).
        ciudad: Filtrar por ciudad (vacío = todas).
        pagina: Número de página (default: 1).
        limite: Resultados por página (max: 100, default: 20).
    """
    auth_error = _check_auth(api_key)
    if auth_error:
        return auth_error

    session = get_db_session()
    try:
        query = session.query(ServicioModel).filter(ServicioModel.activo == True)  # noqa
        if tipo:
            query = query.filter(ServicioModel.tipo_servicio == tipo)
        if ciudad:
            query = query.filter(func.lower(ServicioModel.ciudad).like(func.lower(f"%{ciudad}%")))

        resultados, total, pagina, limite = _paginate_query(query, pagina, limite)
        data = [_model_to_dict(r) for r in resultados]
        return _format_response(data, total, pagina, limite)
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"❌ Error al listar servicios: {e}"
    finally:
        session.close()


@mcp.tool()
def consultar_servicio(api_key: str, id_servicio: str) -> str:
    """
    Consulta un servicio específico por su UUID, incluyendo el proveedor asociado.

    Args:
        api_key: Clave de autenticación.
        id_servicio: UUID del servicio.
    """
    auth_error = _check_auth(api_key)
    if auth_error:
        return auth_error

    session = get_db_session()
    try:
        servicio = (
            session.query(ServicioModel)
            .filter(ServicioModel.id_servicio == id_servicio)
            .first()
        )
        if not servicio:
            return f"❌ No se encontró el servicio con ID: {id_servicio}"

        data = _model_to_dict(servicio)

        # Intentar obtener el proveedor
        prov = session.query(ProveedorModel).filter(ProveedorModel.id_proveedor == servicio.proveedor_id).first()
        if prov:
            data["proveedor"] = _model_to_dict(prov)

        return _format_response(data)
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"❌ Error: {e}"
    finally:
        session.close()


@mcp.tool()
def buscar_servicios(api_key: str, termino: str, pagina: int = 1, limite: int = 20) -> str:
    """
    Busca servicios por nombre, descripción o ciudad.

    Args:
        api_key: Clave de autenticación.
        termino: Texto a buscar.
        pagina: Número de página (default: 1).
        limite: Resultados por página (max: 100, default: 20).
    """
    auth_error = _check_auth(api_key)
    if auth_error:
        return auth_error

    session = get_db_session()
    try:
        pattern = f"%{termino}%"
        query = session.query(ServicioModel).filter(
            ServicioModel.activo == True,  # noqa
            or_(
                func.lower(ServicioModel.nombre).like(func.lower(pattern)),
                func.lower(ServicioModel.descripcion).like(func.lower(pattern)),
                func.lower(ServicioModel.ciudad).like(func.lower(pattern)),
            ),
        )
        resultados, total, pagina, limite = _paginate_query(query, pagina, limite)
        data = [_model_to_dict(r) for r in resultados]
        return _format_response(data, total, pagina, limite, busqueda=termino)
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"❌ Error: {e}"
    finally:
        session.close()


# ══════════════════════════════════════════════════════════════════════════════
#  FOTOS
# ══════════════════════════════════════════════════════════════════════════════


@mcp.tool()
def listar_fotos_servicio(api_key: str, id_servicio: str) -> str:
    """
    Lista todas las fotos activas de un servicio.

    Args:
        api_key: Clave de autenticación.
        id_servicio: UUID del servicio.
    """
    auth_error = _check_auth(api_key)
    if auth_error:
        return auth_error

    session = get_db_session()
    try:
        fotos = (
            session.query(FotoModel)
            .filter(FotoModel.servicio_id == id_servicio, FotoModel.eliminado == False)  # noqa
            .order_by(FotoModel.orden)
            .all()
        )
        data = [_model_to_dict(f) for f in fotos]
        return _format_response(data, total=len(data))
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"❌ Error: {e}"
    finally:
        session.close()


# ══════════════════════════════════════════════════════════════════════════════
#  RUTAS
# ══════════════════════════════════════════════════════════════════════════════


@mcp.tool()
def listar_rutas(api_key: str, pagina: int = 1, limite: int = 20) -> str:
    """
    Lista todas las rutas turísticas activas.

    Args:
        api_key: Clave de autenticación.
        pagina: Número de página (default: 1).
        limite: Resultados por página (max: 100, default: 20).
    """
    auth_error = _check_auth(api_key)
    if auth_error:
        return auth_error

    session = get_db_session()
    try:
        query = session.query(RutaModel).filter(RutaModel.activo == True)  # noqa
        resultados, total, pagina, limite = _paginate_query(query, pagina, limite)
        data = [_model_to_dict(r) for r in resultados]
        return _format_response(data, total, pagina, limite)
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"❌ Error al listar rutas: {e}"
    finally:
        session.close()


@mcp.tool()
def consultar_ruta(api_key: str, id_ruta: str) -> str:
    """
    Consulta una ruta específica por su UUID.

    Args:
        api_key: Clave de autenticación.
        id_ruta: UUID de la ruta.
    """
    auth_error = _check_auth(api_key)
    if auth_error:
        return auth_error

    session = get_db_session()
    try:
        ruta = session.query(RutaModel).filter(RutaModel.id == id_ruta).first()
        if not ruta:
            return f"❌ No se encontró la ruta con ID: {id_ruta}"
        return _format_response(_model_to_dict(ruta))
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"❌ Error: {e}"
    finally:
        session.close()


# ══════════════════════════════════════════════════════════════════════════════
#  VIAJES
# ══════════════════════════════════════════════════════════════════════════════


@mcp.tool()
def listar_viajes(api_key: str, estado: str = "", pagina: int = 1, limite: int = 20) -> str:
    """
    Lista todos los viajes activos. Filtra opcionalmente por estado.

    Args:
        api_key: Clave de autenticación.
        estado: Filtrar por estado: 'programado', 'en_curso', 'finalizado', 'cancelado' (vacío = todos).
        pagina: Número de página (default: 1).
        limite: Resultados por página (max: 100, default: 20).
    """
    auth_error = _check_auth(api_key)
    if auth_error:
        return auth_error

    session = get_db_session()
    try:
        query = session.query(ViajeModel).filter(ViajeModel.activo == True)  # noqa
        if estado:
            query = query.filter(ViajeModel.estado == estado)

        resultados, total, pagina, limite = _paginate_query(query, pagina, limite)
        data = [_model_to_dict(r) for r in resultados]
        return _format_response(data, total, pagina, limite)
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"❌ Error al listar viajes: {e}"
    finally:
        session.close()


@mcp.tool()
def consultar_viaje(api_key: str, id_viaje: str) -> str:
    """
    Consulta un viaje específico por su UUID, incluyendo la ruta asociada.

    Args:
        api_key: Clave de autenticación.
        id_viaje: UUID del viaje.
    """
    auth_error = _check_auth(api_key)
    if auth_error:
        return auth_error

    session = get_db_session()
    try:
        viaje = session.query(ViajeModel).filter(ViajeModel.id == id_viaje).first()
        if not viaje:
            return f"❌ No se encontró el viaje con ID: {id_viaje}"
        data = _model_to_dict(viaje)
        # Incluir ruta si existe
        if viaje.ruta_id:
            ruta = session.query(RutaModel).filter(RutaModel.id == viaje.ruta_id).first()
            if ruta:
                data["ruta"] = _model_to_dict(ruta)
        return _format_response(data)
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"❌ Error: {e}"
    finally:
        session.close()


# ══════════════════════════════════════════════════════════════════════════════
#  TRANSPORTES
# ══════════════════════════════════════════════════════════════════════════════


@mcp.tool()
def listar_transportes(api_key: str, disponible: str = "", pagina: int = 1, limite: int = 20) -> str:
    """
    Lista todos los vehículos de transporte. Filtra opcionalmente por disponibilidad.

    Args:
        api_key: Clave de autenticación.
        disponible: 'si' para disponibles, 'no' para no disponibles, vacío = todos.
        pagina: Número de página (default: 1).
        limite: Resultados por página (max: 100, default: 20).
    """
    auth_error = _check_auth(api_key)
    if auth_error:
        return auth_error

    session = get_db_session()
    try:
        query = session.query(TransporteModel)
        if disponible == "si":
            query = query.filter(TransporteModel.disponible == True)  # noqa
        elif disponible == "no":
            query = query.filter(TransporteModel.disponible == False)  # noqa

        resultados, total, pagina, limite = _paginate_query(query, pagina, limite)
        data = [_model_to_dict(r) for r in resultados]
        return _format_response(data, total, pagina, limite)
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"❌ Error al listar transportes: {e}"
    finally:
        session.close()


# ══════════════════════════════════════════════════════════════════════════════
#  MAYORISTAS
# ══════════════════════════════════════════════════════════════════════════════


@mcp.tool()
def listar_mayoristas(api_key: str, pagina: int = 1, limite: int = 20) -> str:
    """
    Lista todos los mayoristas activos.

    Args:
        api_key: Clave de autenticación.
        pagina: Número de página (default: 1).
        limite: Resultados por página (max: 100, default: 20).
    """
    auth_error = _check_auth(api_key)
    if auth_error:
        return auth_error

    session = get_db_session()
    try:
        query = session.query(MayoristaModel).filter(MayoristaModel.activo == True)  # noqa
        resultados, total, pagina, limite = _paginate_query(query, pagina, limite)
        data = [_model_to_dict(r) for r in resultados]
        return _format_response(data, total, pagina, limite)
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"❌ Error al listar mayoristas: {e}"
    finally:
        session.close()


@mcp.tool()
def consultar_mayorista(api_key: str, id_mayorista: str) -> str:
    """
    Consulta un mayorista específico por su UUID.

    Args:
        api_key: Clave de autenticación.
        id_mayorista: UUID del mayorista.
    """
    auth_error = _check_auth(api_key)
    if auth_error:
        return auth_error

    session = get_db_session()
    try:
        m = session.query(MayoristaModel).filter(MayoristaModel.id == id_mayorista).first()
        if not m:
            return f"❌ No se encontró el mayorista con ID: {id_mayorista}"
        return _format_response(_model_to_dict(m))
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"❌ Error: {e}"
    finally:
        session.close()


# ══════════════════════════════════════════════════════════════════════════════
#  RESERVAS
# ══════════════════════════════════════════════════════════════════════════════


@mcp.tool()
def listar_reservas(api_key: str, estado: str = "", pagina: int = 1, limite: int = 20) -> str:
    """
    Lista todas las reservas activas. Filtra opcionalmente por estado.

    Args:
        api_key: Clave de autenticación.
        estado: Filtrar por estado (vacío = todos).
        pagina: Número de página (default: 1).
        limite: Resultados por página (max: 100, default: 20).
    """
    auth_error = _check_auth(api_key)
    if auth_error:
        return auth_error

    session = get_db_session()
    try:
        query = session.query(ReservaModel).filter(ReservaModel.activo == True)  # noqa
        if estado:
            query = query.filter(ReservaModel.estado == estado)

        resultados, total, pagina, limite = _paginate_query(query, pagina, limite)
        data = [_model_to_dict(r) for r in resultados]
        return _format_response(data, total, pagina, limite)
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"❌ Error al listar reservas: {e}"
    finally:
        session.close()


@mcp.tool()
def consultar_reserva(api_key: str, id_reserva: str) -> str:
    """
    Consulta una reserva específica por su UUID.

    Args:
        api_key: Clave de autenticación.
        id_reserva: UUID de la reserva.
    """
    auth_error = _check_auth(api_key)
    if auth_error:
        return auth_error

    session = get_db_session()
    try:
        reserva = session.query(ReservaModel).filter(ReservaModel.id_reserva == id_reserva).first()
        if not reserva:
            return f"❌ No se encontró la reserva con ID: {id_reserva}"
        return _format_response(_model_to_dict(reserva))
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"❌ Error: {e}"
    finally:
        session.close()


# ══════════════════════════════════════════════════════════════════════════════
#  FECHAS BLOQUEADAS
# ══════════════════════════════════════════════════════════════════════════════


@mcp.tool()
def listar_fechas_bloqueadas(api_key: str, id_servicio: str = "", pagina: int = 1, limite: int = 20) -> str:
    """
    Lista las fechas bloqueadas. Filtra opcionalmente por servicio.

    Args:
        api_key: Clave de autenticación.
        id_servicio: UUID del servicio para filtrar (vacío = todos).
        pagina: Número de página (default: 1).
        limite: Resultados por página (max: 100, default: 20).
    """
    auth_error = _check_auth(api_key)
    if auth_error:
        return auth_error

    session = get_db_session()
    try:
        query = session.query(FechaBloqueadaModel).filter(FechaBloqueadaModel.bloqueo_activo == True)  # noqa
        if id_servicio:
            query = query.filter(FechaBloqueadaModel.servicio_id == id_servicio)

        resultados, total, pagina, limite = _paginate_query(query, pagina, limite)
        data = [_model_to_dict(r) for r in resultados]
        return _format_response(data, total, pagina, limite)
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"❌ Error: {e}"
    finally:
        session.close()


# ─── Entrypoint ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    logger.info(
        f"🚀 Iniciando MCP Server de ReservaT en http://{MCP_HOST}:{MCP_PORT}/sse"
    )
    mcp.run(transport="sse", host=MCP_HOST, port=MCP_PORT)
