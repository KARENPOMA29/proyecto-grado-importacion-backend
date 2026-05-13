# src/routers/venta_router.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.config.db import get_db
from src.controllers.venta_controller import (
    listar_ventas,
    crear_venta,
    obtener_venta_por_id,
    cancelar_venta,
)
from src.schemas.venta import VentaCreate

router = APIRouter(prefix="/ventas", tags=["ventas"])


@router.get("/")
def get_ventas(
    empleadoId: int | None = Query(default=None),
    sucursalId: int | None = Query(default=None),
    search: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return listar_ventas(
        db=db,
        empleado_id=empleadoId,
        sucursal_id=sucursalId,
        search=search,
        page=page,
        page_size=pageSize,
    )


@router.get("/{venta_id}")
def get_venta(venta_id: int, db: Session = Depends(get_db)):
    return obtener_venta_por_id(db, venta_id)


@router.post("/")
def post_venta(venta: VentaCreate, db: Session = Depends(get_db)):
    return crear_venta(db, venta)


@router.put("/{venta_id}/cancelar")
def cancelar(venta_id: int, db: Session = Depends(get_db)):
    return cancelar_venta(db, venta_id)