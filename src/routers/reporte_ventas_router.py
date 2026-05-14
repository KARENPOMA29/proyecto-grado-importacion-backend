from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.config.db import SessionLocal
from src.controllers import reporte_ventas_controller as controller


router = APIRouter(
    prefix="/reportes/ventas",
    tags=["Reportes - Ventas"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/dashboard")
def dashboard_ventas(
    fechaDesde: Optional[str] = Query(None),
    fechaHasta: Optional[str] = Query(None),
    ciudadId: Optional[int] = Query(None),
    sucursalId: Optional[int] = Query(None),
    categoriaId: Optional[int] = Query(None),
    modeloId: Optional[int] = Query(None),
    empleadoId: Optional[int] = Query(None),
    clienteId: Optional[int] = Query(None),
    estado: Optional[int] = Query(1),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    return controller.obtener_dashboard_ventas(
        db,
        fechaDesde,
        fechaHasta,
        ciudadId,
        sucursalId,
        categoriaId,
        modeloId,
        empleadoId,
        clienteId,
        estado,
        search,
    )


@router.get("/detalle")
def detalle_ventas(
    fechaDesde: Optional[str] = Query(None),
    fechaHasta: Optional[str] = Query(None),
    ciudadId: Optional[int] = Query(None),
    sucursalId: Optional[int] = Query(None),
    categoriaId: Optional[int] = Query(None),
    modeloId: Optional[int] = Query(None),
    empleadoId: Optional[int] = Query(None),
    clienteId: Optional[int] = Query(None),
    estado: Optional[int] = Query(1),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return controller.obtener_detalle_ventas(
        db,
        fechaDesde,
        fechaHasta,
        ciudadId,
        sucursalId,
        categoriaId,
        modeloId,
        empleadoId,
        clienteId,
        estado,
        search,
        page,
        pageSize,
    )


@router.get("/por-dia")
def ventas_por_dia(
    fechaDesde: Optional[str] = Query(None),
    fechaHasta: Optional[str] = Query(None),
    ciudadId: Optional[int] = Query(None),
    sucursalId: Optional[int] = Query(None),
    categoriaId: Optional[int] = Query(None),
    modeloId: Optional[int] = Query(None),
    empleadoId: Optional[int] = Query(None),
    clienteId: Optional[int] = Query(None),
    estado: Optional[int] = Query(1),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    return controller.obtener_ventas_por_dia(
        db,
        fechaDesde,
        fechaHasta,
        ciudadId,
        sucursalId,
        categoriaId,
        modeloId,
        empleadoId,
        clienteId,
        estado,
        search,
    )


@router.get("/por-sucursal")
def ventas_por_sucursal(
    fechaDesde: Optional[str] = Query(None),
    fechaHasta: Optional[str] = Query(None),
    ciudadId: Optional[int] = Query(None),
    sucursalId: Optional[int] = Query(None),
    categoriaId: Optional[int] = Query(None),
    modeloId: Optional[int] = Query(None),
    empleadoId: Optional[int] = Query(None),
    clienteId: Optional[int] = Query(None),
    estado: Optional[int] = Query(1),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    return controller.obtener_ventas_por_sucursal(
        db,
        fechaDesde,
        fechaHasta,
        ciudadId,
        sucursalId,
        categoriaId,
        modeloId,
        empleadoId,
        clienteId,
        estado,
        search,
    )


@router.get("/por-producto")
def ventas_por_producto(
    fechaDesde: Optional[str] = Query(None),
    fechaHasta: Optional[str] = Query(None),
    ciudadId: Optional[int] = Query(None),
    sucursalId: Optional[int] = Query(None),
    categoriaId: Optional[int] = Query(None),
    modeloId: Optional[int] = Query(None),
    empleadoId: Optional[int] = Query(None),
    clienteId: Optional[int] = Query(None),
    estado: Optional[int] = Query(1),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    return controller.obtener_ventas_por_producto(
        db,
        fechaDesde,
        fechaHasta,
        ciudadId,
        sucursalId,
        categoriaId,
        modeloId,
        empleadoId,
        clienteId,
        estado,
        search,
    )