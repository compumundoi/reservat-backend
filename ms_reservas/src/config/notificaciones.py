"""Correos del ciclo de vida de una reserva.

Quién recibe qué:

- Creada:    administradores (hay que decidir), proveedor (hay que preparar)
             y mayorista (acuse de recibo).
- Aprobada:  proveedor (confirmar) y mayorista (con el pago, que llega en la
             siguiente fase).
- Rechazada: mayorista y proveedor, ambos con el motivo. Un rechazo sin
             explicación obliga a preguntar por otro canal.
"""

import logging

from config.correo import enviar_correo
from config.precios import calcular_total, formatear_moneda
from models.reservas_model import (
    MayoristaModel,
    ProveedorModel,
    UsuarioModel,
    ROLES_ADMINISTRADOR,
)

logger = logging.getLogger()

COLOR_PRINCIPAL = "#263DBF"


def _formatear_fecha(fecha):
    return fecha.strftime("%d/%m/%Y") if fecha else "—"


def _destinatarios(reserva, db) -> dict:
    """Correos de las tres partes involucradas en la reserva."""
    proveedor = (
        db.query(ProveedorModel)
        .filter(ProveedorModel.id_proveedor == str(reserva.id_proveedor))
        .first()
    )
    mayorista = (
        db.query(MayoristaModel)
        .filter(MayoristaModel.id == str(reserva.id_mayorista))
        .first()
        if reserva.id_mayorista
        else None
    )
    administradores = (
        db.query(UsuarioModel)
        .filter(UsuarioModel.tipo_usuario.in_(ROLES_ADMINISTRADOR))
        .filter(UsuarioModel.activo == True)
        .all()
    )

    return {
        "proveedor": getattr(proveedor, "email", None),
        "mayorista": getattr(mayorista, "email", None),
        "administradores": [u.email for u in administradores if u.email],
        "nombre_proveedor": getattr(proveedor, "nombre", "el proveedor"),
        "nombre_mayorista": " ".join(
            filter(None, [getattr(mayorista, "nombre", None), getattr(mayorista, "apellidos", None)])
        ).strip()
        or "el mayorista",
    }


def _tabla_detalle(reserva) -> str:
    """Los datos de la reserva, iguales en todos los correos."""
    filas = [
        ("Servicio", reserva.nombre_servicio or "—"),
        ("Ciudad", reserva.ciudad or "—"),
        ("Fecha de inicio", _formatear_fecha(reserva.fecha_inicio)),
    ]

    if reserva.fecha_fin and reserva.fecha_fin != reserva.fecha_inicio:
        filas.append(("Fecha de fin", _formatear_fecha(reserva.fecha_fin)))

    if reserva.hora:
        filas.append(("Hora", reserva.hora.strftime("%H:%M")))

    filas.append(("Personas", str(reserva.cantidad or 1)))
    filas.append(("Total", formatear_moneda(calcular_total(reserva))))

    celdas = "".join(
        f'<tr>'
        f'<td style="padding:6px 12px 6px 0;color:#6b7280;font-size:14px">{etiqueta}</td>'
        f'<td style="padding:6px 0;color:#111827;font-size:14px;font-weight:600">{valor}</td>'
        f'</tr>'
        for etiqueta, valor in filas
    )

    return f'<table style="border-collapse:collapse;margin:16px 0">{celdas}</table>'


def _plantilla(titulo: str, saludo: str, cuerpo: str, reserva, extra: str = "") -> str:
    return f"""\
<div style="font-family:system-ui,-apple-system,'Segoe UI',sans-serif;max-width:560px;margin:0 auto;padding:24px;color:#111827">
  <h1 style="color:{COLOR_PRINCIPAL};font-size:22px;margin:0 0 16px">{titulo}</h1>
  <p style="font-size:15px;line-height:1.6;margin:0 0 8px">{saludo}</p>
  <p style="font-size:15px;line-height:1.6;margin:0">{cuerpo}</p>
  {_tabla_detalle(reserva)}
  {extra}
  <p style="font-size:13px;color:#6b7280;margin-top:24px;border-top:1px solid #e5e7eb;padding-top:16px">
    Reserva {str(reserva.id_reserva)[:8]} · Reservat
  </p>
</div>"""


def _boton(url: str, texto: str) -> str:
    """Botón de acción. Los clientes de correo no admiten estilos externos."""
    return (
        f'<div style="margin:20px 0">'
        f'<a href="{url}" style="display:inline-block;background:{COLOR_PRINCIPAL};'
        f'color:#ffffff;text-decoration:none;padding:12px 24px;border-radius:8px;'
        f'font-weight:600;font-size:15px">{texto}</a>'
        f'<p style="font-size:12px;color:#6b7280;margin:8px 0 0">'
        f'Si el botón no funciona, copia este enlace: {url}</p>'
        f"</div>"
    )


def _aviso(texto: str, color_fondo: str, color_texto: str) -> str:
    return (
        f'<div style="background:{color_fondo};border-radius:8px;padding:12px 16px;margin:16px 0">'
        f'<p style="margin:0;font-size:14px;color:{color_texto}">{texto}</p>'
        f"</div>"
    )


def enviar_correos_de_reserva(reserva, evento: str, db) -> None:
    """Despacha los correos del evento. Nunca interrumpe el flujo."""
    try:
        partes = _destinatarios(reserva, db)
    except Exception as e:
        logger.error("No se pudieron resolver los destinatarios: %s", e)
        return

    servicio = reserva.nombre_servicio or "un servicio"

    if evento == "reserva_creada":
        enviar_correo(
            partes["administradores"],
            f"Nueva solicitud de reserva: {servicio}",
            _plantilla(
                "Nueva solicitud de reserva",
                "Hola,",
                f"<b>{partes['nombre_mayorista']}</b> solicitó una reserva para "
                f"<b>{servicio}</b> de {partes['nombre_proveedor']}. "
                "Queda pendiente de tu aprobación.",
                reserva,
            ),
        )

        enviar_correo(
            [partes["proveedor"]],
            f"Nueva solicitud para {servicio}",
            _plantilla(
                "Tienes una nueva solicitud",
                f"Hola {partes['nombre_proveedor']},",
                f"<b>{partes['nombre_mayorista']}</b> solicitó una reserva para "
                f"<b>{servicio}</b>. Un administrador la revisará; te avisaremos "
                "cuando haya una decisión.",
                reserva,
            ),
        )

        enviar_correo(
            [partes["mayorista"]],
            f"Recibimos tu solicitud: {servicio}",
            _plantilla(
                "Recibimos tu solicitud",
                f"Hola {partes['nombre_mayorista']},",
                f"Registramos tu solicitud de reserva para <b>{servicio}</b>. "
                "Queda pendiente de aprobación y te avisaremos apenas haya "
                "respuesta.",
                reserva,
            ),
        )

    elif evento == "reserva_aprobada":
        enviar_correo(
            [partes["proveedor"]],
            f"Reserva aprobada: {servicio}",
            _plantilla(
                "Reserva aprobada",
                f"Hola {partes['nombre_proveedor']},",
                f"La reserva de <b>{partes['nombre_mayorista']}</b> para "
                f"<b>{servicio}</b> fue aprobada. Puedes prepararla para las "
                "fechas indicadas.",
                reserva,
            ),
        )

        # El botón sólo aparece si el cobro se pudo generar; si no, se dice
        # la verdad en vez de mostrar un enlace roto.
        if reserva.pago_link_url:
            extra_pago = _boton(
                reserva.pago_link_url,
                f"Pagar {formatear_moneda(calcular_total(reserva))}",
            )
        else:
            extra_pago = _aviso(
                "Te enviaremos el enlace de pago en un correo aparte.",
                "#eff6ff",
                "#1d4ed8",
            )

        enviar_correo(
            [partes["mayorista"]],
            f"Tu reserva fue aprobada: {servicio}",
            _plantilla(
                "Tu reserva fue aprobada",
                f"Hola {partes['nombre_mayorista']},",
                f"Tu reserva para <b>{servicio}</b> fue aprobada. "
                "Para confirmarla, completa el pago.",
                reserva,
                extra_pago,
            ),
        )

    elif evento == "reserva_rechazada":
        motivo = reserva.motivo_rechazo or "No se indicó un motivo."
        aviso_motivo = _aviso(
            f"<b>Motivo:</b> {motivo}", "#fef2f2", "#b91c1c"
        )

        enviar_correo(
            [partes["mayorista"]],
            f"Tu reserva no pudo confirmarse: {servicio}",
            _plantilla(
                "Tu reserva fue rechazada",
                f"Hola {partes['nombre_mayorista']},",
                f"No pudimos confirmar tu reserva para <b>{servicio}</b>.",
                reserva,
                aviso_motivo,
            ),
        )

        enviar_correo(
            [partes["proveedor"]],
            f"Reserva rechazada: {servicio}",
            _plantilla(
                "Reserva rechazada",
                f"Hola {partes['nombre_proveedor']},",
                f"La reserva de <b>{partes['nombre_mayorista']}</b> para "
                f"<b>{servicio}</b> fue rechazada por un administrador.",
                reserva,
                aviso_motivo,
            ),
        )

    else:
        logger.warning("Evento de correo desconocido: %s", evento)
