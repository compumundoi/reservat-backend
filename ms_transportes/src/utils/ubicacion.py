"""Resolucion del catalogo de ubicaciones (usr_app.countries/departments/municipalities).

Los formularios mandan unicamente `municipio_id`. Desde ahi se derivan el
departamento, el pais y los tres nombres en texto, que se siguen guardando
porque el buscador del landing, el MCP y los listados leen el nombre y no el id.

Este modulo esta duplicado en cada microservicio que escribe ubicacion: no hay
paquete compartido entre los `ms_*`. Si cambia aca, cambia en todos.
"""

import logging
from typing import Any, Dict, Optional

from fastapi import HTTPException, status
from sqlalchemy import text

logger = logging.getLogger(__name__)

# Colombia. Los formularios lo dejan fijo y el catalogo de departamentos y
# municipios solo esta cargado para este pais.
CODIGO_PAIS_POR_DEFECTO = "CO"

_CONSULTA_MUNICIPIO = text(
    """
    SELECT m.id   AS municipio_id,
           m.name AS municipio,
           d.id   AS departamento_id,
           d.name AS departamento,
           c.id   AS pais_id,
           c.name AS pais
    FROM usr_app.municipalities m
    JOIN usr_app.departments d ON d.id = m.department_id
    JOIN usr_app.countries   c ON c.id = d.country_id
    WHERE m.id = :municipio_id
    """
)

_CONSULTA_PAIS_POR_DEFECTO = text(
    "SELECT id, name FROM usr_app.countries WHERE code = :codigo"
)


def resolver_municipio(db, municipio_id: int) -> Dict[str, Any]:
    """Expande un municipio a su ubicacion completa.

    Lanza 400 si el id no existe en el catalogo: es un dato invalido enviado
    por el cliente, no un error del servidor.
    """
    fila = db.execute(
        _CONSULTA_MUNICIPIO, {"municipio_id": municipio_id}
    ).mappings().first()

    if not fila:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El municipio {municipio_id} no existe en el catalogo de ubicaciones",
        )

    return {
        "municipio_id": fila["municipio_id"],
        "ciudad": fila["municipio"],
        "departamento_id": fila["departamento_id"],
        "departamento": fila["departamento"],
        "pais_id": fila["pais_id"],
        "pais": fila["pais"],
    }


def pais_por_defecto(db) -> Dict[str, Any]:
    """Pais que los formularios traen fijo (Colombia)."""
    fila = db.execute(
        _CONSULTA_PAIS_POR_DEFECTO, {"codigo": CODIGO_PAIS_POR_DEFECTO}
    ).mappings().first()

    if not fila:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="El pais por defecto no esta cargado en el catalogo de ubicaciones",
        )

    return {"pais_id": fila["id"], "pais": fila["name"]}


def campos_ubicacion(
    db,
    municipio_id: Optional[int],
    campo_ciudad: str = "ciudad",
) -> Dict[str, Any]:
    """Devuelve el diccionario de campos de ubicacion listo para asignar.

    `campo_ciudad` existe porque no todas las tablas llaman igual al nombre
    del municipio. Si `municipio_id` viene vacio se devuelve solo el pais por
    defecto, para que un registro sin municipio quede igual anclado a Colombia.
    """
    if municipio_id is None:
        return pais_por_defecto(db)

    resuelto = resolver_municipio(db, municipio_id)
    return {
        "pais_id": resuelto["pais_id"],
        "pais": resuelto["pais"],
        "departamento_id": resuelto["departamento_id"],
        "departamento": resuelto["departamento"],
        "municipio_id": resuelto["municipio_id"],
        campo_ciudad: resuelto["ciudad"],
    }


def aplicar_ubicacion(
    destino: Any,
    db,
    municipio_id: Optional[int],
    campo_ciudad: str = "ciudad",
) -> None:
    """Escribe ids y texto derivado sobre una instancia de modelo."""
    for campo, valor in campos_ubicacion(db, municipio_id, campo_ciudad).items():
        setattr(destino, campo, valor)
