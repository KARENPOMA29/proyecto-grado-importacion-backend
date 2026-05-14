# src/routers/reporte_importaciones_router.py
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.config.db import SessionLocal
from src.controllers import reporte_importaciones_controller as controller


router = APIRouter(
    prefix="/reportes/importaciones",
    tags=["Reportes - Importaciones"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/dashboard")
def dashboard_importaciones(db: Session = Depends(get_db)):
    return controller.obtener_dashboard(db)


@router.get("/retrasadas")
def importaciones_retrasadas(
    search: Optional[str] = Query(None),
    fechaDesde: Optional[str] = Query(None),
    fechaHasta: Optional[str] = Query(None),
    proveedor: Optional[str] = Query(None),
    empleado: Optional[str] = Query(None),
    nivelRetraso: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    return controller.obtener_importaciones_retrasadas(
        db,
        search,
        fechaDesde,
        fechaHasta,
        proveedor,
        empleado,
        nivelRetraso,
    )


@router.get("/concluidas")
def importaciones_concluidas(
    search: Optional[str] = Query(None),
    fechaDesde: Optional[str] = Query(None),
    fechaHasta: Optional[str] = Query(None),
    proveedor: Optional[str] = Query(None),
    empleado: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    return controller.obtener_importaciones_concluidas(
        db,
        search,
        fechaDesde,
        fechaHasta,
        proveedor,
        empleado,
    )


@router.get("/proveedores")
def rendimiento_proveedores(db: Session = Depends(get_db)):
    return controller.obtener_rendimiento_proveedores(db)


@router.get("/empleados")
def importaciones_por_empleado(db: Session = Depends(get_db)):
    return controller.obtener_importaciones_por_empleado(db)


@router.get("/por-mes")
def importaciones_por_mes(db: Session = Depends(get_db)):
    return controller.obtener_importaciones_por_mes(db)


@router.get("/por-modelo")
def importaciones_por_modelo(db: Session = Depends(get_db)):
    return controller.obtener_importaciones_por_modelo(db)


@router.get("/top-modelos-rentables")
def top_modelos_rentables(db: Session = Depends(get_db)):
    return controller.obtener_top_modelos_rentables(db)


@router.get("/productos-observados")
def productos_observados(
    search: Optional[str] = Query(None),
    fechaDesde: Optional[str] = Query(None),
    fechaHasta: Optional[str] = Query(None),
    proveedor: Optional[str] = Query(None),
    empleado: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    return controller.obtener_productos_observados(
        db,
        search,
        fechaDesde,
        fechaHasta,
        proveedor,
        empleado,
    )


@router.get("/resumen-financiero")
def resumen_financiero(db: Session = Depends(get_db)):
    return controller.obtener_resumen_financiero(db)