"""Validación del JWT que emite ms_autenticacion.

El token viaja en el header `Authorization: Bearer <token>` o, si el cliente
no lo envía ahí, en la cookie de sesión. El secreto se comparte por entorno
con ms_autenticacion: si difiere, todos los tokens se rechazan.

Sobre el claim `tipo_usuario`: para un administrador vale "administrador" y
para un mayorista "mayorista", pero para un proveedor ms_autenticacion
guarda el tipo del negocio ("hotel", "restaurante", ...), no la palabra
"proveedor". Por eso el rol de proveedor no se deduce del claim sino de que
el id del token coincida con el proveedor del recurso.
"""

import logging
import os

from fastapi import HTTPException, Request, status
from jose import JWTError, jwt

logger = logging.getLogger()

JWT_SECRET = os.getenv("JWT_SECRET", "Hola-mundo-xd")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
COOKIE_NAME = os.getenv("AUTH_COOKIE_NAME", "auth_token")

# La base guarda "admin" en usuarios.tipo_usuario, pero los tipos del
# dashboard declaran "administrador": se aceptan los dos para que el rol no
# dependa de cuál de las dos convenciones mire cada quien.
ROLES_ADMINISTRADOR = ("admin", "administrador")
ROL_MAYORISTA = "mayorista"


def _token_de_la_peticion(request: Request):
    autorizacion = request.headers.get("Authorization") or ""
    if autorizacion.lower().startswith("bearer "):
        return autorizacion[7:].strip()

    return request.cookies.get(COOKIE_NAME)


def obtener_usuario_actual(request: Request) -> dict:
    """Usuario del token, o 401 si no hay token válido.

    Se usa como dependencia de FastAPI en los endpoints que exigen sesión.
    """
    token = _token_de_la_peticion(request)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Necesitas iniciar sesion para realizar esta accion",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        datos = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError as e:
        # El detalle exacto (expirado, firma invalida) se registra pero no se
        # devuelve: no hay que darle pistas a quien esta probando tokens.
        logger.warning("Token rechazado: %s", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tu sesion no es valida o expiro. Inicia sesion nuevamente",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not datos.get("id"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El token no identifica a ningun usuario",
        )

    return {
        "id": str(datos.get("id")),
        "email": datos.get("email"),
        "tipo_usuario": str(datos.get("tipo_usuario") or "").lower(),
    }


def es_administrador(usuario: dict) -> bool:
    return usuario.get("tipo_usuario") in ROLES_ADMINISTRADOR


def exigir_administrador(usuario: dict) -> dict:
    """403 si quien llama no es administrador."""
    if not es_administrador(usuario):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo un administrador puede realizar esta accion",
        )
    return usuario


def exigir_propietario_o_admin(usuario: dict, *ids_permitidos) -> dict:
    """Deja pasar al administrador o a quien sea dueño del recurso.

    `ids_permitidos` son los ids que, si coinciden con el del token,
    habilitan el acceso: el mayorista que solicitó la reserva o el proveedor
    que la debe atender.
    """
    if es_administrador(usuario):
        return usuario

    permitidos = {str(i) for i in ids_permitidos if i}
    if usuario["id"] in permitidos:
        return usuario

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="No tienes permiso para acceder a esta informacion",
    )
