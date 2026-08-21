"""Envío de correo a través de Resend.

Se usa la API HTTP directamente con la biblioteca estándar: el servicio no
necesita una dependencia nueva para hacer un POST con un JSON.

Dos reglas que gobiernan este módulo:

1. Un fallo enviando correo NUNCA interrumpe la operación que lo disparó.
   La reserva ya está guardada cuando esto corre; si el correo no sale, se
   registra en el log y el flujo continúa.
2. Sin RESEND_API_KEY el servicio no se rompe: registra lo que habría
   enviado y sigue. Así el stack local funciona sin credenciales y los
   correos se pueden revisar en el log.
"""

import json
import logging
import os
import urllib.error
import urllib.request

logger = logging.getLogger()

RESEND_API_URL = "https://api.resend.com/emails"
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "").strip()

# Remitente. Sin un dominio verificado en Resend sólo funciona su dirección
# de pruebas, que permite enviar únicamente al correo del dueño de la cuenta.
CORREO_REMITENTE = os.getenv("CORREO_REMITENTE", "Reservat <onboarding@resend.dev>")

TIEMPO_LIMITE_SEGUNDOS = 10

# Lista blanca de desarrollo. Con CORREOS_PERMITIDOS definida, sólo se
# escribe a esas direcciones y el resto se descarta con un registro en el
# log. Evita que una prueba le escriba a un proveedor real sin tener que
# falsear los correos en la base, que es de donde depende el inicio de
# sesión. En produccion se deja vacia y no filtra nada.
CORREOS_PERMITIDOS = {
    c.strip().lower()
    for c in os.getenv("CORREOS_PERMITIDOS", "").split(",")
    if c.strip()
}


def _filtrar_permitidos(destinos, asunto):
    """Descarta los destinatarios que la lista blanca no autoriza."""
    if not CORREOS_PERMITIDOS:
        return destinos

    permitidos = [d for d in destinos if d.lower() in CORREOS_PERMITIDOS]
    descartados = [d for d in destinos if d.lower() not in CORREOS_PERMITIDOS]

    if descartados:
        logger.warning(
            "Modo desarrollo: correo %r NO enviado a %s (fuera de "
            "CORREOS_PERMITIDOS)",
            asunto,
            descartados,
        )

    return permitidos


def correo_habilitado() -> bool:
    return bool(RESEND_API_KEY)


def enviar_correo(destinatarios, asunto: str, html: str) -> bool:
    """Envía un correo. Devuelve si salió, pero nunca lanza excepción."""
    destinos = sorted({d.strip() for d in destinatarios if d and d.strip()})

    if not destinos:
        logger.info("Correo '%s' omitido: no hay destinatarios", asunto)
        return False

    destinos = _filtrar_permitidos(destinos, asunto)
    if not destinos:
        return False

    if not correo_habilitado():
        logger.warning(
            "RESEND_API_KEY no configurada. Correo NO enviado -> "
            "asunto=%r destinatarios=%s",
            asunto,
            destinos,
        )
        return False

    cuerpo = json.dumps(
        {
            "from": CORREO_REMITENTE,
            "to": destinos,
            "subject": asunto,
            "html": html,
        }
    ).encode("utf-8")

    peticion = urllib.request.Request(
        RESEND_API_URL,
        data=cuerpo,
        method="POST",
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json",
            # urllib se identifica como "Python-urllib/3.x" y el escudo que
            # protege la API responde 403 ante ese agente. Se declara uno
            # propio, que ademas identifica al servicio en sus registros.
            "User-Agent": "Reservat/1.0 (ms_reservas)",
            "Accept": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(
            peticion, timeout=TIEMPO_LIMITE_SEGUNDOS
        ) as respuesta:
            datos = json.loads(respuesta.read().decode("utf-8") or "{}")
            logger.info(
                "Correo enviado: asunto=%r destinatarios=%s id=%s",
                asunto,
                destinos,
                datos.get("id"),
            )
            return True

    except urllib.error.HTTPError as e:
        # El detalle de Resend explica por qué lo rechazó (dominio sin
        # verificar, destinatario no permitido en modo de pruebas, etc.).
        detalle = e.read().decode("utf-8", errors="replace")[:500]
        logger.error(
            "Resend rechazo el correo %r (%s): %s", asunto, e.code, detalle
        )
    except Exception as e:
        logger.error("No se pudo enviar el correo %r: %s", asunto, e)

    return False
