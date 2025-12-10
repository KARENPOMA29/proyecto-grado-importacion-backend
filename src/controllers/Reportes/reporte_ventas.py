# src/controllers/Reportes/reporte_ventas.py
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.config.db import SessionLocal
from src.schemas.Reportes.reporte_ventas import VentaReporteItem

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


@router.get("/", response_model=List[VentaReporteItem])
def reporte_ventas(
    # --- filtros principales ---
    fecha_desde: Optional[date] = Query(None),
    fecha_hasta: Optional[date] = Query(None),
    empleado_id: Optional[int] = Query(None),
    ciudad_id: Optional[int] = Query(None),
    sucursal_id: Optional[int] = Query(None),
    cliente_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Reporte de ventas con filtros por:
    - rango de fechas
    - empleado
    - ciudad
    - sucursal
    - cliente

    Devuelve una fila por producto vendido (DetalleVenta).
    """

    # SQL para el reporte
    # OJO: el valor de tipoMovimiento para ventas AJÚSTALO si en tu BD usaste otro texto
    sql = text(
        """
        SELECT
            v.id                 AS ventaId,
            v.codigoVenta        AS codigoVenta,
            v.fechaRegistro      AS fechaVenta,
            v.total              AS totalVenta,

            e.id                 AS empleadoId,
            (e.nombre + ' ' + e.apellido) AS empleadoNombre,

            cli.id               AS clienteId,
            cli.razonSocial      AS clienteNombre,
            cli.nit              AS clienteNit,

            s.id                 AS sucursalId,
            s.nombre             AS sucursalNombre,
            ci.id                AS ciudadId,
            ci.Nombre            AS ciudadNombre,

            dv.id                AS detalleId,
            p.id                 AS productoId,
            p.numeroSerie        AS numeroSerie,
            mp.nombreModelo      AS modeloNombre,
            cat.nombre           AS categoriaNombre,
            m.Nombre             AS marcaNombre,

            al.id                AS almacenId,
            al.nombre            AS almacenNombre,

            p.precioOrigen       AS precioOrigen,
            p.precio             AS precioVenta,
            dv.subtotal          AS subtotal
        FROM Venta v
        INNER JOIN DetalleVenta dv   ON dv.ventaId   = v.id
        INNER JOIN Producto p        ON p.id         = dv.productoId
        INNER JOIN Categoria cat     ON cat.id       = p.categoriaId
        INNER JOIN ModeloProducto mp ON mp.id        = p.modeloId
        LEFT  JOIN Marca m           ON m.id         = mp.idMarca
        INNER JOIN Empleado e        ON e.id         = v.empleadoId
        INNER JOIN Cliente cli       ON cli.id       = v.clienteId
        INNER JOIN Sucursal s        ON s.id         = v.sucursalId
        LEFT  JOIN Ciudad ci         ON ci.id        = s.idCiudad

        -- Para saber desde qué almacén salió el producto
        LEFT JOIN (
            SELECT
                mi.productoId,
                mi.almacenId
            FROM MovimientoInventario mi
            WHERE mi.estado = 1
            AND mi.tipoMovimiento = 'SALIDA_VENTA' -- AJUSTA ESTE TEXTO SI USAS OTRO
        ) AS mi ON mi.productoId = p.id
        LEFT JOIN Almacen al ON al.id = mi.almacenId

        WHERE v.estado = 1
        AND (:fecha_desde IS NULL OR v.fechaRegistro >= :fecha_desde)
        AND (:fecha_hasta IS NULL OR v.fechaRegistro <= :fecha_hasta)
        AND (:empleado_id IS NULL OR v.empleadoId = :empleado_id)
        AND (:cliente_id  IS NULL OR v.clienteId  = :cliente_id)
        AND (:sucursal_id IS NULL OR v.sucursalId = :sucursal_id)
        AND (:ciudad_id   IS NULL OR s.idCiudad   = :ciudad_id)
        ORDER BY v.fechaRegistro DESC, v.id DESC, dv.id ASC
        """
        )

    params = {
        "fecha_desde": fecha_desde,
        "fecha_hasta": fecha_hasta,
        "empleado_id": empleado_id,
        "cliente_id": cliente_id,
        "sucursal_id": sucursal_id,
        "ciudad_id": ciudad_id,
    }

    # En SQL Server con SQLAlchemy, usa .mappings() para obtener dicts
    result = db.execute(sql, params).mappings().all()

    return [VentaReporteItem(**row) for row in result]
