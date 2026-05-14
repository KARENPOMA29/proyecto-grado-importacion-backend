from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import text

def _paginate_query(
    db: Session,
    base_sql: str,
    params: dict,
    order_by: str,
    page: int = 1,
    pageSize: int = 20,
):
    """
    Paginación consistente para todos los reportes.
    
    Retorna: {
        "items": [],
        "total": 0,
        "page": 1,  # Basado en 1 (para el frontend)
        "pageSize": 20
    }
    """
    page = max(int(page or 1), 1)
    pageSize = max(min(int(pageSize or 20), 100), 1)

    offset = (page - 1) * pageSize

    total_sql = text(f"""
        SELECT COUNT(*) AS total
        FROM (
            {base_sql}
        ) AS T
    """)

    data_sql = text(f"""
        SELECT *
        FROM (
            {base_sql}
        ) AS T
        ORDER BY {order_by}
        OFFSET :offset ROWS
        FETCH NEXT :pageSize ROWS ONLY
    """)

    total = db.execute(total_sql, params).scalar() or 0

    rows = db.execute(
        data_sql,
        {
            **params,
            "offset": offset,
            "pageSize": pageSize,
        },
    ).mappings().all()

    return {
        "items": [dict(row) for row in rows],
        "total": total,
        "page": page,
        "pageSize": pageSize,
    }


# ============================================================
# FILTROS PARA ENTRADAS - HISTÓRICO
# Usa vw_reporte_entradas_detalle
# ============================================================

def _build_filters_entradas(
    fechaDesde: Optional[str] = None,
    fechaHasta: Optional[str] = None,
    ciudadId: Optional[int] = None,
    sucursalId: Optional[int] = None,
    almacenId: Optional[int] = None,
    categoriaId: Optional[int] = None,
    modeloId: Optional[int] = None,
    proveedorId: Optional[int] = None,
    importacionId: Optional[int] = None,
    empleadoId: Optional[int] = None,
    observado: Optional[int] = None,
    search: Optional[str] = None,
):
    where = ["1 = 1"]
    params = {}

    if fechaDesde:
        where.append("fechaEntradaSolo >= :fechaDesde")
        params["fechaDesde"] = fechaDesde

    if fechaHasta:
        where.append("fechaEntradaSolo <= :fechaHasta")
        params["fechaHasta"] = fechaHasta

    if ciudadId is not None:
        where.append("ciudadId = :ciudadId")
        params["ciudadId"] = ciudadId

    if sucursalId is not None:
        where.append("sucursalId = :sucursalId")
        params["sucursalId"] = sucursalId

    if almacenId is not None:
        where.append("almacenId = :almacenId")
        params["almacenId"] = almacenId

    if categoriaId is not None:
        where.append("categoriaId = :categoriaId")
        params["categoriaId"] = categoriaId

    if modeloId is not None:
        where.append("modeloId = :modeloId")
        params["modeloId"] = modeloId

    if proveedorId is not None:
        where.append("proveedorId = :proveedorId")
        params["proveedorId"] = proveedorId

    if importacionId is not None:
        where.append("importacionId = :importacionId")
        params["importacionId"] = importacionId

    if empleadoId is not None:
        where.append("empleadoRegistroId = :empleadoId")
        params["empleadoId"] = empleadoId

    if observado is not None:
        where.append("observado = :observado")
        params["observado"] = observado

    if search and search.strip():
        where.append("""
            (
                numeroSerie LIKE :search OR
                productoDescripcion LIKE :search OR
                nombreModelo LIKE :search OR
                categoriaNombre LIKE :search OR
                sucursalNombre LIKE :search OR
                almacenNombre LIKE :search OR
                ciudadNombre LIKE :search OR
                importacionCodigo LIKE :search OR
                proveedorNombre LIKE :search OR
                empleadoRegistroNombre LIKE :search
            )
        """)
        params["search"] = f"%{search.strip()}%"

    return " AND ".join(where), params


# ============================================================
# FILTROS PARA STOCK ACTUAL
# Usa vw_reporte_stock_actual y vw_reporte_stock_actual_detalle
# ============================================================

def _build_filters_stock(
    fechaDesde: Optional[str] = None,
    fechaHasta: Optional[str] = None,
    ciudadId: Optional[int] = None,
    sucursalId: Optional[int] = None,
    almacenId: Optional[int] = None,
    categoriaId: Optional[int] = None,
    modeloId: Optional[int] = None,
    proveedorId: Optional[int] = None,
    importacionId: Optional[int] = None,
    empleadoId: Optional[int] = None,
    observado: Optional[int] = None,
    search: Optional[str] = None,
    detalle: bool = False,
):
    where = ["1 = 1"]
    params = {}

    fecha_col = "fechaUltimoMovimiento"

    if fechaDesde:
        where.append(f"CAST({fecha_col} AS DATE) >= :fechaDesde")
        params["fechaDesde"] = fechaDesde

    if fechaHasta:
        where.append(f"CAST({fecha_col} AS DATE) <= :fechaHasta")
        params["fechaHasta"] = fechaHasta

    if ciudadId is not None:
        where.append("ciudadId = :ciudadId")
        params["ciudadId"] = ciudadId

    if sucursalId is not None:
        where.append("sucursalId = :sucursalId")
        params["sucursalId"] = sucursalId

    if almacenId is not None:
        where.append("almacenId = :almacenId")
        params["almacenId"] = almacenId

    if categoriaId is not None:
        where.append("categoriaId = :categoriaId")
        params["categoriaId"] = categoriaId

    if modeloId is not None:
        where.append("modeloId = :modeloId")
        params["modeloId"] = modeloId

    if proveedorId is not None:
        where.append("proveedorId = :proveedorId")
        params["proveedorId"] = proveedorId

    if importacionId is not None:
        where.append("importacionId = :importacionId")
        params["importacionId"] = importacionId

    if empleadoId is not None:
        where.append("empleadoRegistroId = :empleadoId")
        params["empleadoId"] = empleadoId

    if observado is not None:
        where.append("observado = :observado")
        params["observado"] = observado

    if search and search.strip():
        if detalle:
            where.append("""
                (
                    numeroSerie LIKE :search OR
                    productoDescripcion LIKE :search OR
                    nombreModelo LIKE :search OR
                    categoriaNombre LIKE :search OR
                    ciudad LIKE :search OR
                    sucursal LIKE :search OR
                    almacen LIKE :search OR
                    seccion LIKE :search OR
                    importacionCodigo LIKE :search OR
                    proveedorNombre LIKE :search OR
                    empleadoRegistroNombre LIKE :search
                )
            """)
        else:
            where.append("""
                (
                    ciudad LIKE :search OR
                    sucursal LIKE :search OR
                    almacen LIKE :search OR
                    seccion LIKE :search OR
                    categoriaNombre LIKE :search OR
                    nombreModelo LIKE :search OR
                    estadoStock LIKE :search
                )
            """)
        params["search"] = f"%{search.strip()}%"

    return " AND ".join(where), params


# ============================================================
# ENTRADAS - DASHBOARD
# ============================================================

def obtener_dashboard_entradas(
    db: Session,
    fechaDesde=None,
    fechaHasta=None,
    ciudadId=None,
    sucursalId=None,
    almacenId=None,
    categoriaId=None,
    modeloId=None,
    proveedorId=None,
    importacionId=None,
    empleadoId=None,
    observado=None,
    search=None,
):
    where_sql, params = _build_filters_entradas(
        fechaDesde,
        fechaHasta,
        ciudadId,
        sucursalId,
        almacenId,
        categoriaId,
        modeloId,
        proveedorId,
        importacionId,
        empleadoId,
        observado,
        search,
    )

    sql = text(f"""
        SELECT
            COUNT(productoId) AS productosIngresados,
            COUNT(DISTINCT movimientoId) AS movimientosEntrada,
            COUNT(DISTINCT importacionId) AS importacionesRelacionadas,
            COUNT(DISTINCT proveedorId) AS proveedoresRelacionados,
            COUNT(DISTINCT sucursalId) AS sucursalesConEntrada,
            COUNT(DISTINCT almacenId) AS almacenesConEntrada,

            ISNULL(SUM(precioOrigen), 0) AS costoTotalOrigen,
            ISNULL(SUM(precioVenta), 0) AS valorVentaEstimado,
            ISNULL(SUM(utilidadEstimada), 0) AS utilidadEstimadaTotal,

            SUM(CASE WHEN observado = 2 THEN 1 ELSE 0 END) AS productosObservados,
            SUM(CASE WHEN observado = 1 THEN 1 ELSE 0 END) AS productosSinObservacion,

            CASE
                WHEN COUNT(productoId) = 0 THEN 0
                ELSE ISNULL(SUM(precioOrigen), 0) / COUNT(productoId)
            END AS costoPromedioUnitario,

            CASE
                WHEN COUNT(productoId) = 0 THEN 0
                ELSE ISNULL(SUM(precioVenta), 0) / COUNT(productoId)
            END AS precioVentaPromedioUnitario,

            CASE
                WHEN ISNULL(SUM(precioOrigen), 0) = 0 THEN 0
                ELSE (
                    ISNULL(SUM(utilidadEstimada), 0)
                    / ISNULL(SUM(precioOrigen), 0)
                ) * 100
            END AS margenEstimadoPromedio

        FROM vw_reporte_entradas_detalle
        WHERE {where_sql}
    """)

    row = db.execute(sql, params).mappings().first()
    return dict(row or {})


# ============================================================
# ENTRADAS - DETALLE
# ============================================================

def obtener_detalle_entradas(
    db: Session,
    fechaDesde=None,
    fechaHasta=None,
    ciudadId=None,
    sucursalId=None,
    almacenId=None,
    categoriaId=None,
    modeloId=None,
    proveedorId=None,
    importacionId=None,
    empleadoId=None,
    observado=None,
    search=None,
    page: int = 1,
    pageSize: int = 20,
):
    where_sql, params = _build_filters_entradas(
        fechaDesde,
        fechaHasta,
        ciudadId,
        sucursalId,
        almacenId,
        categoriaId,
        modeloId,
        proveedorId,
        importacionId,
        empleadoId,
        observado,
        search,
    )

    base_sql = f"""
        SELECT *
        FROM vw_reporte_entradas_detalle
        WHERE {where_sql}
    """

    return _paginate_query(
        db, base_sql, params, "fechaEntrada DESC, movimientoId DESC", page, pageSize
    )


def obtener_por_dia(db: Session, page: int = 1, pageSize: int = 20, **filters):
    where_sql, params = _build_filters_entradas(**filters)

    base_sql = f"""
        SELECT
            fechaEntradaSolo AS fecha,
            COUNT(productoId) AS productosIngresados,
            COUNT(DISTINCT movimientoId) AS movimientosEntrada,
            COUNT(DISTINCT importacionId) AS importacionesRelacionadas,
            ISNULL(SUM(precioOrigen), 0) AS costoTotalOrigen,
            ISNULL(SUM(precioVenta), 0) AS valorVentaEstimado,
            ISNULL(SUM(utilidadEstimada), 0) AS utilidadEstimadaTotal,
            SUM(CASE WHEN observado = 2 THEN 1 ELSE 0 END) AS productosObservados
        FROM vw_reporte_entradas_detalle
        WHERE {where_sql}
        GROUP BY fechaEntradaSolo
    """

    return _paginate_query(db, base_sql, params, "fecha DESC", page, pageSize)


def obtener_por_sucursal_almacen(db: Session, page: int = 1, pageSize: int = 20, **filters):
    where_sql, params = _build_filters_entradas(**filters)

    base_sql = f"""
        SELECT
            ciudadNombre,
            sucursalNombre,
            almacenNombre,
            COUNT(productoId) AS productosIngresados,
            COUNT(DISTINCT importacionId) AS importacionesRelacionadas,
            COUNT(DISTINCT proveedorId) AS proveedoresRelacionados,
            ISNULL(SUM(precioOrigen), 0) AS costoTotalOrigen,
            ISNULL(SUM(precioVenta), 0) AS valorVentaEstimado,
            ISNULL(SUM(utilidadEstimada), 0) AS utilidadEstimadaTotal,
            SUM(CASE WHEN observado = 2 THEN 1 ELSE 0 END) AS productosObservados
        FROM vw_reporte_entradas_detalle
        WHERE {where_sql}
        GROUP BY ciudadNombre, sucursalNombre, almacenNombre
    """

    return _paginate_query(
        db, base_sql, params, "productosIngresados DESC", page, pageSize
    )


def obtener_por_producto(db: Session, page: int = 1, pageSize: int = 20, **filters):
    where_sql, params = _build_filters_entradas(**filters)

    base_sql = f"""
        SELECT
            categoriaNombre,
            nombreModelo,
            color,
            capacidadTexto,
            COUNT(productoId) AS productosIngresados,
            COUNT(DISTINCT importacionId) AS importacionesRelacionadas,
            ISNULL(SUM(precioOrigen), 0) AS costoTotalOrigen,
            ISNULL(SUM(precioVenta), 0) AS valorVentaEstimado,
            ISNULL(SUM(utilidadEstimada), 0) AS utilidadEstimadaTotal,
            AVG(precioOrigen) AS costoPromedioOrigen,
            AVG(precioVenta) AS precioVentaPromedio,
            SUM(CASE WHEN observado = 2 THEN 1 ELSE 0 END) AS productosObservados
        FROM vw_reporte_entradas_detalle
        WHERE {where_sql}
        GROUP BY categoriaNombre, nombreModelo, color, capacidadTexto
    """

    return _paginate_query(
        db, base_sql, params, "productosIngresados DESC", page, pageSize
    )


def obtener_por_importacion(db: Session, page: int = 1, pageSize: int = 20, **filters):
    where_sql, params = _build_filters_entradas(**filters)

    base_sql = f"""
        SELECT
            importacionId,
            importacionCodigo,
            proveedorNombre,
            fechaLlegada,
            COUNT(productoId) AS productosIngresados,
            COUNT(DISTINCT categoriaId) AS categoriasIngresadas,
            COUNT(DISTINCT modeloId) AS modelosIngresados,
            ISNULL(SUM(precioOrigen), 0) AS costoTotalOrigen,
            ISNULL(SUM(precioVenta), 0) AS valorVentaEstimado,
            ISNULL(SUM(utilidadEstimada), 0) AS utilidadEstimadaTotal,
            SUM(CASE WHEN observado = 2 THEN 1 ELSE 0 END) AS productosObservados
        FROM vw_reporte_entradas_detalle
        WHERE {where_sql}
        GROUP BY importacionId, importacionCodigo, proveedorNombre, fechaLlegada
    """

    return _paginate_query(
        db, base_sql, params, "productosIngresados DESC", page, pageSize
    )


def obtener_por_proveedor(db: Session, page: int = 1, pageSize: int = 20, **filters):
    where_sql, params = _build_filters_entradas(**filters)

    base_sql = f"""
        SELECT
            proveedorId,
            proveedorNombre,
            proveedorEncargado,
            proveedorTelefono,
            COUNT(productoId) AS productosIngresados,
            COUNT(DISTINCT importacionId) AS importacionesRelacionadas,
            ISNULL(SUM(precioOrigen), 0) AS costoTotalOrigen,
            ISNULL(SUM(precioVenta), 0) AS valorVentaEstimado,
            ISNULL(SUM(utilidadEstimada), 0) AS utilidadEstimadaTotal,
            SUM(CASE WHEN observado = 2 THEN 1 ELSE 0 END) AS productosObservados
        FROM vw_reporte_entradas_detalle
        WHERE {where_sql}
        GROUP BY proveedorId, proveedorNombre, proveedorEncargado, proveedorTelefono
    """

    return _paginate_query(
        db, base_sql, params, "productosIngresados DESC", page, pageSize
    )


def obtener_observados(db: Session, page: int = 1, pageSize: int = 20, **filters):
    filtros = dict(filters)
    filtros.pop("observado", None)

    where_sql, params = _build_filters_entradas(**filtros)

    base_sql = f"""
        SELECT *
        FROM vw_reporte_entradas_detalle
        WHERE {where_sql}
        AND observado = 2
    """

    return _paginate_query(
        db, base_sql, params, "fechaEntrada DESC, movimientoId DESC", page, pageSize
    )


# ============================================================
# STOCK ACTUAL - DASHBOARD
# Usa vw_reporte_stock_actual_detalle
# ============================================================

def obtener_dashboard_stock_actual(
    db: Session,
    fechaDesde=None,
    fechaHasta=None,
    ciudadId=None,
    sucursalId=None,
    almacenId=None,
    categoriaId=None,
    modeloId=None,
    proveedorId=None,
    importacionId=None,
    empleadoId=None,
    observado=None,
    search=None,
):
    where_sql, params = _build_filters_stock(
        fechaDesde,
        fechaHasta,
        ciudadId,
        sucursalId,
        almacenId,
        categoriaId,
        modeloId,
        proveedorId,
        importacionId,
        empleadoId,
        observado,
        search,
        detalle=True,
    )

    sql = text(f"""
        SELECT
            COUNT(productoId) AS stockTotal,

            COUNT(DISTINCT modeloId) AS modelosConStock,
            COUNT(DISTINCT categoriaId) AS categoriasConStock,
            COUNT(DISTINCT sucursalId) AS sucursalesConStock,
            COUNT(DISTINCT almacenId) AS almacenesConStock,

            ISNULL(SUM(precioOrigen), 0) AS costoTotalStock,
            ISNULL(SUM(precioVenta), 0) AS valorVentaStock,
            ISNULL(SUM(utilidadEstimada), 0) AS utilidadEstimadaStock,

            SUM(CASE WHEN observado = 2 THEN 1 ELSE 0 END) AS productosObservados,
            SUM(CASE WHEN observado = 1 THEN 1 ELSE 0 END) AS productosSinObservacion

        FROM vw_reporte_stock_actual_detalle
        WHERE {where_sql}
    """)

    row = db.execute(sql, params).mappings().first()
    return dict(row or {})


# ============================================================
# STOCK ACTUAL - AGRUPADO
# Usa vw_reporte_stock_actual
# ============================================================

def obtener_stock_actual(
    db: Session,
    fechaDesde=None,
    fechaHasta=None,
    ciudadId=None,
    sucursalId=None,
    almacenId=None,
    categoriaId=None,
    modeloId=None,
    proveedorId=None,
    importacionId=None,
    empleadoId=None,
    observado=None,
    search=None,
    page: int = 1,
    pageSize: int = 20,
):
    # ✅ CORREGIDO: Solo filtros que existen en vw_reporte_stock_actual
    where_sql, params = _build_filters_stock(
        fechaDesde=None,
        fechaHasta=None,
        ciudadId=ciudadId,
        sucursalId=sucursalId,
        almacenId=almacenId,
        categoriaId=categoriaId,
        modeloId=modeloId,
        proveedorId=None,  # No existe en stock actual
        importacionId=None,  # No existe en stock actual
        empleadoId=None,  # No existe en stock actual
        observado=observado,
        search=search,
        detalle=False,
    )

    base_sql = f"""
        SELECT
            ciudadId,
            ciudad,

            sucursalId,
            sucursal,

            almacenId,
            almacen,

            seccionId,
            seccion,

            categoriaId,
            categoriaNombre,

            modeloId,
            nombreModelo,
            color,
            capacidadTexto,

            cantidad,

            stockMinimo,

            costoTotalStock,
            valorVentaStock,
            utilidadEstimadaStock,

            productosObservados,
            estadoStock
        FROM vw_reporte_stock_actual
        WHERE {where_sql}
    """

    return _paginate_query(
        db,
        base_sql,
        params,
        "ciudad, sucursal, almacen, seccion, nombreModelo",
        page,
        pageSize,
    )


# ============================================================
# STOCK ACTUAL - DETALLE
# Producto por producto disponible actualmente
# Usa vw_reporte_stock_actual_detalle
# ============================================================

def obtener_stock_actual_detalle(
    db: Session,
    fechaDesde=None,
    fechaHasta=None,
    ciudadId=None,
    sucursalId=None,
    almacenId=None,
    categoriaId=None,
    modeloId=None,
    proveedorId=None,
    importacionId=None,
    empleadoId=None,
    observado=None,
    search=None,
    page: int = 1,
    pageSize: int = 20,
):
    where_sql, params = _build_filters_stock(
        fechaDesde,
        fechaHasta,
        ciudadId,
        sucursalId,
        almacenId,
        categoriaId,
        modeloId,
        proveedorId,
        importacionId,
        empleadoId,
        observado,
        search,
        detalle=True,
    )

    base_sql = f"""
        SELECT *
        FROM vw_reporte_stock_actual_detalle
        WHERE {where_sql}
    """

    return _paginate_query(
        db, base_sql, params, "fechaUltimoMovimiento DESC, movimientoId DESC", page, pageSize
    )
