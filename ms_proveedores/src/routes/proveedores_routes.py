from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import text
from datetime import datetime
import logging
from fastapi.responses import JSONResponse
from config.db2 import DB
from models.proveedores_model import ProveedorModel
from schemas.proveedores_schema import ProveedorBusqueda, ResponseBusqueda
from typing import List

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

db = DB.create()
SessionLocal = sessionmaker(bind=db.engine)


def get_db():
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()


proveedores = APIRouter()


@proveedores.get("/proveedores/buscar/", response_model=ResponseBusqueda)
async def buscar_proveedores(
    search: str = "",
    pagina: int = 0,
    limite: int = 10,
    db: Session = Depends(get_db),
):
    """Busca proveedores por nombre con paginación (máximo 10 resultados)"""
    try:
        # Limitar a máximo 10 resultados por búsqueda
        limite = min(limite, 10)
        skip = pagina * limite

        query = db.query(ProveedorModel).filter(ProveedorModel.activo == True)

        if search.strip():
            query = query.filter(ProveedorModel.nombre.ilike(f"%{search}%"))

        total = query.count()
        proveedores_result = query.order_by(ProveedorModel.nombre).offset(skip).limit(limite).all()

        return ResponseBusqueda(
            proveedores=[
                ProveedorBusqueda(
                    id_proveedor=p.id_proveedor,
                    nombre=p.nombre,
                )
                for p in proveedores_result
            ],
            total=total,
            page=pagina,
            size=limite,
        )

    except Exception as e:
        logger.error(f"Error en búsqueda de proveedores: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al buscar proveedores",
        )


# Health Check
@proveedores.get("/proveedores/healthchecker")
def get_live():
    return {"message": "Proveedores service is LIVE!!"}


# Readiness
@proveedores.get("/proveedores/readiness")
def check_readiness(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT 1")).fetchone()
        if result and result[0] == 1:
            return {"status": "Ready"}
        return {"status": "Not Ready"}
    except Exception as e:
        logger.error(f"Error en readiness check: {str(e)}")
        return {"status": "Not Ready"}
