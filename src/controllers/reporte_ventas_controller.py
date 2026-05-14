from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import text


def _build_filters(
    fechaDesde: Optional[str] = None,
    fechaHasta: Optional[str] = None,
    ciudadId: Optional[int] = None,
    sucursalId: Optional[int] = None,
    categoriaId: Optional[int] = None,
    modeloId: Optional[int] = None,
    empleadoId: Optional[int] = None,
    clienteId: Optional[int] = None,
    estado: Optional[int] = 1,
    search: Optional[str] = None,
):
    where = ["1 = 1"]
    params = {}

    if fechaDesde:
        where.append("fechaVentaSolo >= :fechaDesde")
        params["fechaDesde"] = fechaDesde

    if fechaHasta:
        where.append("fechaVentaSolo <= :fechaHasta")
        params["fechaHasta"] = fechaHasta

    if ciudadId is not None:
        where.append("ciudadId = :ciudadId")
        params["ciudadId"] = ciudadId

    if sucursalId is not None:
        where.append("sucursalId = :sucursalId")
        params["sucursalId"] = sucursalId

    if categoriaId is not None:
        where.append("categoriaId = :categoriaId")
        params["categoriaId"] = categoriaId

    if modeloId is not None:
        where.append("modeloId = :modeloId")
        params["modeloId"] = modeloId

    if empleadoId is not None:
        where.append("empleadoId = :empleadoId")
        params["empleadoId"] = empleadoId

    if clienteId is not None:
        where.append("clienteId = :clienteId")
        params["clienteId"] = clienteId

    if estado is not None:
        where.append("estadoVenta = :estado")
        params["estado"] = estado

    if search and search.strip():
        where.append("""
            (
                codigoVenta LIKE :search OR
                clienteNombre LIKE :search OR
                empleadoNombre LIKE :search OR
                numeroSerie LIKE :search OR
                nombreModelo LIKE :search OR
                categoriaNombre LIKE :search OR
                sucursalNombre LIKE :search OR
                ciudadNombre LIKE :search
            )
        """)
        params["search"] = f"%{search.strip()}%"

    return " AND ".join(where), params

def obtener_dashboard_ventas(
    db: Session,
    fechaDesde: Optional[str] = None,
    fechaHasta: Optional[str] = None,
    ciudadId: Optional[int] = None,
    sucursalId: Optional[int] = None,
    categoriaId: Optional[int] = None,
    modeloId: Optional[int] = None,
    empleadoId: Optional[int] = None,
    clienteId: Optional[int] = None,
    estado: Optional[int] = 1,
    search: Optional[str] = None,
):
    where_sql, params = _build_filters(
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

    sql = text(f"""
        SELECT
            COUNT(DISTINCT ventaId) AS cantidadVentas,
            COUNT(productoId) AS productosVendidos,
            ISNULL(SUM(subtotal), 0) AS totalVendido,
            CASE 
                WHEN COUNT(DISTINCT ventaId) = 0 THEN 0
                ELSE ISNULL(SUM(subtotal), 0) / COUNT(DISTINCT ventaId)
            END AS ticketPromedio
        FROM vw_reporte_ventas_detalle
        WHERE {where_sql}
    """)

    row = db.execute(sql, params).mappings().first()

    return dict(row or {})


def obtener_detalle_ventas(
    db: Session,
    fechaDesde: Optional[str] = None,
    fechaHasta: Optional[str] = None,
    ciudadId: Optional[int] = None,
    sucursalId: Optional[int] = None,
    categoriaId: Optional[int] = None,
    modeloId: Optional[int] = None,
    empleadoId: Optional[int] = None,
    clienteId: Optional[int] = None,
    estado: Optional[int] = 1,
    search: Optional[str] = None,
    page: int = 1,
    pageSize: int = 20,
):
    where_sql, params = _build_filters(
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

    offset = (page - 1) * pageSize
    params["offset"] = offset
    params["pageSize"] = pageSize

    total_sql = text(f"""
        SELECT COUNT(*) AS total
        FROM vw_reporte_ventas_detalle
        WHERE {where_sql}
    """)

    data_sql = text(f"""
        SELECT *
        FROM vw_reporte_ventas_detalle
        WHERE {where_sql}
        ORDER BY fechaVenta DESC, ventaId DESC
        OFFSET :offset ROWS
        FETCH NEXT :pageSize ROWS ONLY
    """)

    total = db.execute(total_sql, params).scalar() or 0
    rows = db.execute(data_sql, params).mappings().all()

    return {
        "items": [dict(row) for row in rows],
        "total": total,
        "page": page,
        "pageSize": pageSize,
    }


def obtener_ventas_por_dia(
    db: Session,
    fechaDesde: Optional[str] = None,
    fechaHasta: Optional[str] = None,
    ciudadId: Optional[int] = None,
    sucursalId: Optional[int] = None,
    categoriaId: Optional[int] = None,
    modeloId: Optional[int] = None,
    empleadoId: Optional[int] = None,
    clienteId: Optional[int] = None,
    estado: Optional[int] = 1,
    search: Optional[str] = None,
):
    where_sql, params = _build_filters(
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

    sql = text(f"""
        SELECT
            fechaVentaSolo AS fecha,
            COUNT(DISTINCT ventaId) AS cantidadVentas,
            COUNT(productoId) AS productosVendidos,
            ISNULL(SUM(subtotal), 0) AS totalVendido,
            CASE 
                WHEN COUNT(DISTINCT ventaId) = 0 THEN 0
                ELSE ISNULL(SUM(subtotal), 0) / COUNT(DISTINCT ventaId)
            END AS ticketPromedio
        FROM vw_reporte_ventas_detalle
        WHERE {where_sql}
        GROUP BY fechaVentaSolo
        ORDER BY fechaVentaSolo ASC
    """)

    rows = db.execute(sql, params).mappings().all()
    return [dict(row) for row in rows]


def obtener_ventas_por_sucursal(
    db: Session,
    fechaDesde: Optional[str] = None,
    fechaHasta: Optional[str] = None,
    ciudadId: Optional[int] = None,
    sucursalId: Optional[int] = None,
    categoriaId: Optional[int] = None,
    modeloId: Optional[int] = None,
    empleadoId: Optional[int] = None,
    clienteId: Optional[int] = None,
    estado: Optional[int] = 1,
    search: Optional[str] = None,
):
    where_sql, params = _build_filters(
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

    sql = text(f"""
        SELECT
            ciudadNombre,
            sucursalNombre,
            COUNT(DISTINCT ventaId) AS cantidadVentas,
            COUNT(productoId) AS productosVendidos,
            ISNULL(SUM(subtotal), 0) AS totalVendido,
            SUM(CASE WHEN estadoVenta = 0 THEN 1 ELSE 0 END) AS ventasAnuladas
        FROM vw_reporte_ventas_detalle
        WHERE {where_sql}
        GROUP BY ciudadNombre, sucursalNombre
        ORDER BY totalVendido DESC
    """)

    rows = db.execute(sql, params).mappings().all()
    return [dict(row) for row in rows]


def obtener_ventas_por_producto(
    db: Session,
    fechaDesde: Optional[str] = None,
    fechaHasta: Optional[str] = None,
    ciudadId: Optional[int] = None,
    sucursalId: Optional[int] = None,
    categoriaId: Optional[int] = None,
    modeloId: Optional[int] = None,
    empleadoId: Optional[int] = None,
    clienteId: Optional[int] = None,
    estado: Optional[int] = 1,
    search: Optional[str] = None,
):
    where_sql, params = _build_filters(
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

    sql = text(f"""
        SELECT
            categoriaNombre,
            nombreModelo,
            color,
            capacidadOTamano,
            COUNT(productoId) AS productosVendidos,
            ISNULL(SUM(subtotal), 0) AS totalVendido,
            CASE 
                WHEN COUNT(productoId) = 0 THEN 0
                ELSE ISNULL(SUM(subtotal), 0) / COUNT(productoId)
            END AS precioPromedioVenta
        FROM vw_reporte_ventas_detalle
        WHERE {where_sql}
        GROUP BY categoriaNombre, nombreModelo, color, capacidadOTamano
        ORDER BY totalVendido DESC
    """)

    rows = db.execute(sql, params).mappings().all()
    return [dict(row) for row in rows]