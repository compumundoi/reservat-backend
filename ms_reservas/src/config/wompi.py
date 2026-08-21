"""Integración con Wompi: enlaces de pago y verificación de sus avisos.

El cobro se hace con un enlace de pago que se genera cuando un administrador
aprueba la reserva. Wompi avisa el resultado por webhook.

Sobre la verificación de la firma: el webhook es un endpoint público, así
que cualquiera puede llamarlo diciendo que una reserva fue pagada. Wompi
firma cada aviso concatenando los valores de las propiedades que él mismo
indica, seguidos del sello de tiempo y del secreto de eventos, y aplicando
SHA-256. Sin comprobar ese resumen, el endpoint es una forma de marcar
reservas como pagadas sin pagar.
"""

import hashlib
import hmac
import json
import logging
import os
import urllib.error
import urllib.request

logger = logging.getLogger()

WOMPI_API_URL = os.getenv("WOMPI_API_URL", "https://sandbox.wompi.co/v1").rstrip("/")
WOMPI_PRIVATE_KEY = os.getenv("WOMPI_PRIVATE_KEY", "").strip()
WOMPI_EVENTS_SECRET = os.getenv("WOMPI_EVENTS_SECRET", "").strip()

# A dónde vuelve la persona después de pagar.
WOMPI_REDIRECT_URL = os.getenv(
    "WOMPI_REDIRECT_URL", "http://reservatonline.com:8000"
)

# Los enlaces se comparten en un correo: el checkout vive en otro dominio.
WOMPI_CHECKOUT_URL = os.getenv(
    "WOMPI_CHECKOUT_URL", "https://checkout.wompi.co/l"
).rstrip("/")

TIEMPO_LIMITE_SEGUNDOS = 15


def pagos_habilitados() -> bool:
    return bool(WOMPI_PRIVATE_KEY)


def _peticion(ruta: str, metodo: str, cuerpo: dict):
    """Llama a la API de Wompi. Devuelve el JSON o None si falla."""
    peticion = urllib.request.Request(
        f"{WOMPI_API_URL}{ruta}",
        data=json.dumps(cuerpo).encode("utf-8"),
        method=metodo,
        headers={
            "Authorization": f"Bearer {WOMPI_PRIVATE_KEY}",
            "Content-Type": "application/json",
            # Igual que con el correo: el agente por defecto de urllib es
            # rechazado por el escudo que protege la API.
            "User-Agent": "Reservat/1.0 (ms_reservas)",
            "Accept": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(
            peticion, timeout=TIEMPO_LIMITE_SEGUNDOS
        ) as respuesta:
            return json.loads(respuesta.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as e:
        detalle = e.read().decode("utf-8", errors="replace")[:500]
        logger.error("Wompi rechazo %s %s (%s): %s", metodo, ruta, e.code, detalle)
    except Exception as e:
        logger.error("Fallo llamando a Wompi %s %s: %s", metodo, ruta, e)

    return None


def crear_enlace_de_pago(reserva, total: float) -> dict:
    """Crea el enlace de cobro de una reserva.

    Devuelve {'id': ..., 'url': ...} o None si no se pudo crear. Un fallo
    acá no invalida la aprobación: la reserva ya fue aprobada y el enlace
    se puede generar después.
    """
    if not pagos_habilitados():
        logger.warning(
            "WOMPI_PRIVATE_KEY no configurada: la reserva %s queda aprobada "
            "sin enlace de pago",
            reserva.id_reserva,
        )
        return None

    # Wompi cobra en centavos y sólo acepta enteros.
    centavos = int(round(total * 100))
    if centavos <= 0:
        logger.error(
            "No se genera enlace para la reserva %s: total invalido (%s)",
            reserva.id_reserva,
            total,
        )
        return None

    respuesta = _peticion(
        "/payment_links",
        "POST",
        {
            "name": f"Reserva: {reserva.nombre_servicio}"[:255],
            "description": (
                f"Reserva {str(reserva.id_reserva)[:8]} · "
                f"{reserva.cantidad} persona(s) · {reserva.ciudad}"
            )[:255],
            # Un enlace por reserva: no debe poder pagarse dos veces.
            "single_use": True,
            "collect_shipping": False,
            "currency": "COP",
            "amount_in_cents": centavos,
            "redirect_url": WOMPI_REDIRECT_URL,
        },
    )

    identificador = (respuesta or {}).get("data", {}).get("id")
    if not identificador:
        return None

    return {
        "id": identificador,
        "url": f"{WOMPI_CHECKOUT_URL}/{identificador}",
    }


def desactivar_enlace_de_pago(link_id: str) -> bool:
    """Desactiva un enlace para que no se pueda volver a usar."""
    if not link_id or not pagos_habilitados():
        return False

    return _peticion(f"/payment_links/{link_id}", "PATCH", {"active": False}) is not None


def _valor_anidado(datos: dict, ruta: str):
    """Lee 'transaction.status' recorriendo el diccionario por puntos."""
    actual = datos
    for parte in ruta.split("."):
        if not isinstance(actual, dict):
            return None
        actual = actual.get(parte)
    return actual


def firma_valida(aviso: dict) -> bool:
    """Comprueba que el aviso venga realmente de Wompi.

    El resumen se calcula concatenando, en el orden indicado por el propio
    aviso, los valores de sus propiedades firmadas, más el sello de tiempo
    y el secreto de eventos.
    """
    if not WOMPI_EVENTS_SECRET:
        # Sin secreto no hay forma de distinguir un aviso legítimo de uno
        # inventado. Se rechaza: es preferible no registrar un pago a
        # registrar uno falso.
        logger.error(
            "WOMPI_EVENTS_SECRET no configurada: se rechaza el aviso de pago"
        )
        return False

    firma = aviso.get("signature") or {}
    propiedades = firma.get("properties") or []
    checksum_recibido = (firma.get("checksum") or "").lower()
    datos = aviso.get("data") or {}

    if not propiedades or not checksum_recibido:
        logger.warning("Aviso de pago sin firma utilizable")
        return False

    concatenado = ""
    for propiedad in propiedades:
        valor = _valor_anidado(datos, propiedad)
        if valor is None:
            logger.warning("El aviso no trae la propiedad firmada %r", propiedad)
            return False
        concatenado += str(valor)

    concatenado += str(aviso.get("timestamp", ""))
    concatenado += WOMPI_EVENTS_SECRET

    calculado = hashlib.sha256(concatenado.encode("utf-8")).hexdigest()

    # Comparacion en tiempo constante, para no filtrar el resumen.
    if not hmac.compare_digest(calculado, checksum_recibido):
        logger.warning("Aviso de pago con firma invalida: se descarta")
        return False

    return True
