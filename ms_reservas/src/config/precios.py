"""Cálculo del total de una reserva.

La regla ya vivía repetida en la landing y en los dos dashboards. Aquí es
donde debe estar: el correo, el dashboard y el mayorista tienen que ver el
mismo importe, y el único que puede garantizarlo es quien guarda el dato.
"""

from datetime import date

# Tipos que se cobran por noche; el resto se cobra por persona.
TIPOS_POR_RANGO = ("alojamiento", "hoteles", "hotel")


def es_por_rango(tipo_servicio) -> bool:
    return str(tipo_servicio or "").lower() in TIPOS_POR_RANGO


def calcular_noches(fecha_inicio, fecha_fin) -> int:
    """Noches entre dos fechas. Mínimo 1, para no dejar un total en cero."""
    if not isinstance(fecha_inicio, date) or not isinstance(fecha_fin, date):
        return 1

    noches = (fecha_fin - fecha_inicio).days
    return noches if noches > 0 else 1


def calcular_total(reserva) -> float:
    """Total de la reserva.

    Alojamiento: precio por noche (las personas sólo validan capacidad).
    Resto: precio por persona.
    """
    try:
        precio = float(reserva.precio)
    except (TypeError, ValueError):
        return 0.0

    if es_por_rango(reserva.tipo_servicio):
        return precio * calcular_noches(reserva.fecha_inicio, reserva.fecha_fin)

    return precio * (reserva.cantidad or 1)


def formatear_moneda(valor: float) -> str:
    """Importe en pesos con separador de miles, para mostrar a una persona."""
    return "$" + f"{valor:,.0f}".replace(",", ".")
