# src/routers/reporte_entradas_router.py

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.config.db import SessionLocal
from src.controllers import reporte_entradas_controller as controller

router = APIRouter(
    prefix="/reportes/entradas",
    tags=["Reportes - Entradas"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def filtros_comunes(
    fechaDesde: Optional[str] = Query(None),
    fechaHasta: Optional[str] = Query(None),
    ciudadId: Optional[int] = Query(None),
    sucursalId: Optional[int] = Query(None),
    almacenId: Optional[int] = Query(None),
    categoriaId: Optional[int] = Query(None),
    modeloId: Optional[int] = Query(None),
    proveedorId: Optional[int] = Query(None),
    importacionId: Optional[int] = Query(None),
    empleadoId: Optional[int] = Query(None),
    observado: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
):
    return {
        "fechaDesde": fechaDesde,
        "fechaHasta": fechaHasta,
        "ciudadId": ciudadId,
        "sucursalId": sucursalId,
        "almacenId": almacenId,
        "categoriaId": categoriaId,
        "modeloId": modeloId,
        "proveedorId": proveedorId,
        "importacionId": importacionId,
        "empleadoId": empleadoId,
        "observado": observado,
        "search": search,
    }


# ============================================================
# ENTRADAS - HISTÓRICO
# ============================================================

@router.get("/dashboard")
def dashboard_entradas(
    filtros: dict = Depends(filtros_comunes),
    db: Session = Depends(get_db),
):
    return controller.obtener_dashboard_entradas(db, **filtros)


@router.get("/detalle")
def detalle_entradas(
    filtros: dict = Depends(filtros_comunes),
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return controller.obtener_detalle_entradas(
        db,
        **filtros,
        page=page,
        pageSize=pageSize,
    )


@router.get("/por-dia")
def entradas_por_dia(
    filtros: dict = Depends(filtros_comunes),
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return controller.obtener_por_dia(
        db,
        **filtros,
        page=page,
        pageSize=pageSize,
    )


@router.get("/por-sucursal-almacen")
def entradas_por_sucursal_almacen(
    filtros: dict = Depends(filtros_comunes),
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return controller.obtener_por_sucursal_almacen(
        db,
        **filtros,
        page=page,
        pageSize=pageSize,
    )


@router.get("/por-producto")
def entradas_por_producto(
    filtros: dict = Depends(filtros_comunes),
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return controller.obtener_por_producto(
        db,
        **filtros,
        page=page,
        pageSize=pageSize,
    )


@router.get("/por-importacion")
def entradas_por_importacion(
    filtros: dict = Depends(filtros_comunes),
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return controller.obtener_por_importacion(
        db,
        **filtros,
        page=page,
        pageSize=pageSize,
    )


@router.get("/por-proveedor")
def entradas_por_proveedor(
    filtros: dict = Depends(filtros_comunes),
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return controller.obtener_por_proveedor(
        db,
        **filtros,
        page=page,
        pageSize=pageSize,
    )


@router.get("/observados")
def entradas_observadas(
    filtros: dict = Depends(filtros_comunes),
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return controller.obtener_observados(
        db,
        **filtros,
        page=page,
        pageSize=pageSize,
    )


# ============================================================
# STOCK ACTUAL - ÚLTIMO MOVIMIENTO
# ============================================================

@router.get("/stock/dashboard")
def dashboard_stock_actual(
    filtros: dict = Depends(filtros_comunes),
    db: Session = Depends(get_db),
):
    return controller.obtener_dashboard_stock_actual(db, **filtros)


@router.get("/stock/actual")
def stock_actual(
    filtros: dict = Depends(filtros_comunes),
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return controller.obtener_stock_actual(
        db,
        **filtros,
        page=page,
        pageSize=pageSize,
    )


@router.get("/stock/detalle")
def stock_actual_detalle(
    filtros: dict = Depends(filtros_comunes),
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return controller.obtener_stock_actual_detalle(
        db,
        **filtros,
        page=page,
        pageSize=pageSize,
    )