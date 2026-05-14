# src/controllers/reporte_importaciones_controller.py
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import text


def _build_where(
    search: Optional[str] = None,
    fechaDesde: Optional[str] = None,
    fechaHasta: Optional[str] = None,
    proveedor: Optional[str] = None,
    empleado: Optional[str] = None,
):
    where = []
    params = {}

    if search:
        where.append("""
            (
                codigo LIKE :search OR
                proveedorNombre LIKE :search OR
                empleadoEncargado LIKE :search OR
                descripcion LIKE :search
            )
        """)
        params["search"] = f"%{search}%"

    if fechaDesde:
        where.append("CAST(fechaRegistro AS DATE) >= :fechaDesde")
        params["fechaDesde"] = fechaDesde

    if fechaHasta:
        where.append("CAST(fechaRegistro AS DATE) <= :fechaHasta")
        params["fechaHasta"] = fechaHasta

    if proveedor:
        where.append("proveedorNombre = :proveedor")
        params["proveedor"] = proveedor

    if empleado:
        where.append("empleadoEncargado = :empleado")
        params["empleado"] = empleado

    where_sql = ""
    if where:
        where_sql = " WHERE " + " AND ".join(where)

    return where_sql, params


def _fetch_view(db: Session, view_name: str):
    result = db.execute(text(f"SELECT * FROM {view_name}"))
    return [dict(row._mapping) for row in result]


def _fetch_filtered_importaciones(
    db: Session,
    view_name: str,
    search=None,
    fechaDesde=None,
    fechaHasta=None,
    proveedor=None,
    empleado=None,
):
    where_sql, params = _build_where(
        search=search,
        fechaDesde=fechaDesde,
        fechaHasta=fechaHasta,
        proveedor=proveedor,
        empleado=empleado,
    )

    sql = text(f"""
        SELECT *
        FROM {view_name}
        {where_sql}
        ORDER BY fechaRegistro DESC
    """)

    result = db.execute(sql, params)
    return [dict(row._mapping) for row in result]


def obtener_dashboard(db: Session):
    result = db.execute(text("SELECT * FROM vw_dashboard_importaciones")).first()
    return dict(result._mapping) if result else {}


def obtener_importaciones_retrasadas(
    db: Session,
    search=None,
    fechaDesde=None,
    fechaHasta=None,
    proveedor=None,
    empleado=None,
    nivelRetraso=None,
):
    where_sql, params = _build_where(
        search=search,
        fechaDesde=fechaDesde,
        fechaHasta=fechaHasta,
        proveedor=proveedor,
        empleado=empleado,
    )

    extra = ""

    if nivelRetraso:
        extra = " AND nivelRetraso = :nivelRetraso" if where_sql else " WHERE nivelRetraso = :nivelRetraso"
        params["nivelRetraso"] = nivelRetraso

    sql = text(f"""
        SELECT *
        FROM vw_importaciones_retrasadas
        {where_sql}
        {extra}
        ORDER BY diasRetraso DESC
    """)

    result = db.execute(sql, params)
    return [dict(row._mapping) for row in result]


def obtener_importaciones_concluidas(
    db: Session,
    search=None,
    fechaDesde=None,
    fechaHasta=None,
    proveedor=None,
    empleado=None,
):
    return _fetch_filtered_importaciones(
        db,
        "vw_importaciones_concluidas",
        search,
        fechaDesde,
        fechaHasta,
        proveedor,
        empleado,
    )


def obtener_rendimiento_proveedores(db: Session):
    return _fetch_view(db, "vw_rendimiento_proveedores")


def obtener_importaciones_por_empleado(db: Session):
    return _fetch_view(db, "vw_importaciones_por_empleado")


def obtener_importaciones_por_mes(db: Session):
    return _fetch_view(db, "vw_importaciones_por_mes")


def obtener_importaciones_por_modelo(db: Session):
    return _fetch_view(db, "vw_importaciones_por_modelo")


def obtener_top_modelos_rentables(db: Session):
    return _fetch_view(db, "vw_top_modelos_rentables")


def obtener_productos_observados(
    db: Session,
    search=None,
    fechaDesde=None,
    fechaHasta=None,
    proveedor=None,
    empleado=None,
):
    where = []
    params = {}

    if search:
        where.append("""
            (
                numeroSerie LIKE :search OR
                nombreModelo LIKE :search OR
                codigoImportacion LIKE :search OR
                proveedorNombre LIKE :search OR
                empleadoEncargado LIKE :search OR
                obsDescripcion LIKE :search
            )
        """)
        params["search"] = f"%{search}%"

    if fechaDesde:
        where.append("CAST(fechaRegistro AS DATE) >= :fechaDesde")
        params["fechaDesde"] = fechaDesde

    if fechaHasta:
        where.append("CAST(fechaRegistro AS DATE) <= :fechaHasta")
        params["fechaHasta"] = fechaHasta

    if proveedor:
        where.append("proveedorNombre = :proveedor")
        params["proveedor"] = proveedor

    if empleado:
        where.append("empleadoEncargado = :empleado")
        params["empleado"] = empleado

    where_sql = ""
    if where:
        where_sql = " WHERE " + " AND ".join(where)

    sql = text(f"""
        SELECT *
        FROM vw_productos_observados_importacion
        {where_sql}
        ORDER BY fechaRegistro DESC
    """)

    result = db.execute(sql, params)
    return [dict(row._mapping) for row in result]


def obtener_resumen_financiero(db: Session):
    result = db.execute(text("SELECT * FROM vw_resumen_financiero_importaciones")).first()
    return dict(result._mapping) if result else {}