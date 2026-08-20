from typing import List
from pydantic import BaseModel
from uuid import UUID


class ProveedorBusqueda(BaseModel):
    id_proveedor: UUID
    nombre: str | None = None
    # El autocompletado necesita algo con lo que distinguir dos proveedores
    # de nombre parecido. El UUID no le dice nada a nadie; el correo si.
    email: str | None = None

    class Config:
        from_attributes = True


class ResponseBusqueda(BaseModel):
    proveedores: List[ProveedorBusqueda]
    total: int
    page: int
    size: int
