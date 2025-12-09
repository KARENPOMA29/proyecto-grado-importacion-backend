from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.config.db import SessionLocal
from src.schemas.reportes import (
    ResumenVentasResponse,
    ResumenImportacionesResponse,
    StockResponse,
)
from src.controllers import reportes_controller


router = APIRouter(prefix="/reportes", tags=["Reportes"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============ VENTAS ============

@router.get("/ventas", response_model=ResumenVentasResponse)
def get_reporte_ventas(
    fecha_desde: Optional[date] = Query(None),
    fecha_hasta: Optional[date] = Query(None),
    sucursal_id: Optional[int] = Query(None),
    empleado_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Reporte de ventas con:
    - total general
    - ventas por día
    - ventas por sucursal
    Filtrable por rango de fechas, sucursal y empleado.
    """
    return reportes_controller.obtener_resumen_ventas(
        db=db,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        sucursal_id=sucursal_id,
        empleado_id=empleado_id,
    )


# ============ IMPORTACIONES ============

@router.get("/importaciones", response_model=ResumenImportacionesResponse)
def get_reporte_importaciones(
    fecha_desde: Optional[date] = Query(None),
    fecha_hasta: Optional[date] = Query(None),
    proveedor_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Reporte de importaciones:
    - cantidad total de importaciones
    - resumen por proveedor
    """
    return reportes_controller.obtener_resumen_importaciones(
        db=db,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        proveedor_id=proveedor_id,
    )


# ============ CONTROL DE STOCK ============

@router.get("/stock", response_model=StockResponse)
def get_reporte_stock(
    solo_en_alerta: bool = Query(False),
    db: Session = Depends(get_db),
):
    """
    Reporte de stock:
    - Lista de modelos con stockActual y stockMinimo
    - Marca cuáles están en alerta (stockActual <= stockMinimo)
    - Puedes filtrar solo los que están en alerta.
    """
    return reportes_controller.obtener_reporte_stock(
        db=db,
        solo_en_alerta=solo_en_alerta,
    )
