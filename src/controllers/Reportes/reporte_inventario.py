# src/controllers/Reportes/reporte_inventario.py

from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import date


from src.config.db import SessionLocal

router = APIRouter(
    prefix="/reportes",
    tags=["Reportes"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/inventario")
def reporte_inventario(
    fecha_desde: Optional[date] = Query(None),
    fecha_hasta: Optional[date] = Query(None),
    ciudad_id: Optional[int] = Query(None),
    sucursal_id: Optional[int] = Query(None),
    almacen_id: Optional[int] = Query(None),
    seccion_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):

    """
    🔎 Reporte de inventario por MODELO y ubicación:
    - Filtra por rango de fechas (fechaRegistro de la SECCION)
    - Filtra por ciudad, sucursal, almacén y sección
    - Stock es el stockActual del ModeloProducto (stock por modelo)
    """

    sql = text(
        """
        SELECT
            -- MODELO / MARCA
            mp.id              AS modeloId,
            mp.nombreModelo    AS modeloNombre,
            mp.stockActual     AS stockActual,
            mp.stockMinimo     AS stockMinimo,
            mp.color           AS modeloColor,
            mp.capacidadOTamano AS capacidadOTamano,
            mp.unidadMedida    AS unidadMedida,

            m.id               AS marcaId,
            m.Nombre           AS marcaNombre,

            -- SECCION
            sec.id             AS seccionId,
            sec.nombre         AS seccionNombre,
            sec.descripcion    AS seccionDescripcion,
            sec.fechaRegistro  AS fechaAsignacion,

            -- ALMACEN
            al.id              AS almacenId,
            al.nombre          AS almacenNombre,
            al.direccion       AS almacenDireccion,

            -- SUCURSAL
            s.id               AS sucursalId,
            s.nombre           AS sucursalNombre,
            s.direccion        AS sucursalDireccion,

            -- CIUDAD
            ci.id              AS ciudadId,
            ci.Nombre          AS ciudadNombre

        FROM Seccion sec
        INNER JOIN Almacen al          ON al.id = sec.almacenId
        INNER JOIN Sucursal s          ON s.id = al.sucursalId
        LEFT  JOIN Ciudad ci           ON ci.id = s.idCiudad
        INNER JOIN ModeloProducto mp   ON mp.id = sec.modeloId
        LEFT  JOIN Marca m             ON m.id = mp.idMarca

        WHERE sec.estado = 1
          AND mp.estado  = 1
          AND al.estado  = 1
          AND s.estado   = 1

          AND (:fecha_desde IS NULL OR sec.fechaRegistro >= :fecha_desde)
          AND (:fecha_hasta IS NULL OR sec.fechaRegistro <= :fecha_hasta)
          AND (:ciudad_id   IS NULL OR s.idCiudad   = :ciudad_id)
          AND (:sucursal_id IS NULL OR s.id         = :sucursal_id)
          AND (:almacen_id  IS NULL OR al.id        = :almacen_id)
          AND (:seccion_id  IS NULL OR sec.id       = :seccion_id)

        ORDER BY
            ci.Nombre,
            s.nombre,
            al.nombre,
            sec.nombre,
            mp.nombreModelo
        """
    )

    params = {
        "fecha_desde": fecha_desde,
        "fecha_hasta": fecha_hasta,
        "ciudad_id": ciudad_id,
        "sucursal_id": sucursal_id,
        "almacen_id": almacen_id,
        "seccion_id": seccion_id,
    }

    result = db.execute(sql, params).mappings().all()

    # Devolvemos lista de dicts para que el frontend lo consuma fácil
    return [dict(row) for row in result]
