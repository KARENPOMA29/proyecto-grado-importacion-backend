from datetime import datetime, date
from typing import Optional, List

from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date

from src.models.venta import Venta
from src.models.detalle_venta import DetalleVenta
from src.models.sucursal import Sucursal
from src.models.importacion import Importacion
from src.models.proveedor import Proveedor
from src.models.modelo_producto import ModeloProducto
from src.models.producto import Producto
from src.models.empleado import Empleado
from src.models.cliente import Cliente

from src.schemas.reportes import (
    ResumenVentasResponse,
    VentaPorDia,
    VentaPorSucursal,
    VentaPorEmpleado,
    VentaPorCliente,
    VentaPorModelo,
    ResumenImportacionesResponse,
    ImportacionPorProveedor,
    StockResponse,
    StockItem,
)


# =====================  VENTAS  =====================

def obtener_resumen_ventas(
    db: Session,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    sucursal_id: Optional[int] = None,
    empleado_id: Optional[int] = None,
    modelo_id: Optional[int] = None,
    cliente_id: Optional[int] = None,
) -> ResumenVentasResponse:
    # Base: ventas activas
    query = db.query(Venta).filter(Venta.estado == 1)

    # Filtros simples
    if fecha_desde:
        query = query.filter(
            Venta.fechaRegistro >= datetime.combine(
                fecha_desde, datetime.min.time()
            )
        )
    if fecha_hasta:
        query = query.filter(
            Venta.fechaRegistro <= datetime.combine(
                fecha_hasta, datetime.max.time()
            )
        )
    if sucursal_id:
        query = query.filter(Venta.sucursalId == sucursal_id)
    if empleado_id:
        query = query.filter(Venta.empleadoId == empleado_id)
    if cliente_id:
        query = query.filter(Venta.clienteId == cliente_id)

    # Filtro por modelo (via DetalleVenta -> Producto -> ModeloProducto)
    if modelo_id:
        venta_ids_subq = (
            db.query(DetalleVenta.ventaId)
            .join(Producto, Producto.id == DetalleVenta.productoId)
            .filter(Producto.modeloId == modelo_id)
            .subquery()
        )
        query = query.filter(Venta.id.in_(venta_ids_subq))

    # Subquery con las ventas filtradas (para reutilizar)
    ventas_subq = query.with_entities(
        Venta.id.label("id"),
        Venta.total.label("total"),
        Venta.fechaRegistro.label("fechaRegistro"),
        Venta.sucursalId.label("sucursalId"),
        Venta.empleadoId.label("empleadoId"),
        Venta.clienteId.label("clienteId"),
    ).subquery()

    # Total general
    total_ventas, cantidad_ventas = db.query(
        func.coalesce(func.sum(ventas_subq.c.total), 0),
        func.count(ventas_subq.c.id),
    ).one()

    # Agrupado por día
    fecha_col = cast(ventas_subq.c.fechaRegistro, Date)
    ventas_por_dia_raw = (
        db.query(
            fecha_col.label("fecha"),
            func.coalesce(func.sum(ventas_subq.c.total), 0).label("total_ventas"),
            func.count(ventas_subq.c.id).label("cantidad_ventas"),
        )
        .group_by(fecha_col)
        .order_by(fecha_col)
        .all()
    )

    ventas_por_dia = [
        VentaPorDia(
            fecha=row.fecha,
            total_ventas=float(row.total_ventas or 0),
            cantidad_ventas=row.cantidad_ventas,
        )
        for row in ventas_por_dia_raw
    ]

    # Agrupado por sucursal
    ventas_por_sucursal_raw = (
        db.query(
            Sucursal.id.label("sucursalId"),
            Sucursal.nombre.label("sucursalNombre"),
            func.coalesce(func.sum(ventas_subq.c.total), 0).label("total_ventas"),
            func.count(ventas_subq.c.id).label("cantidad_ventas"),
        )
        .join(Sucursal, ventas_subq.c.sucursalId == Sucursal.id)
        .group_by(Sucursal.id, Sucursal.nombre)
        .order_by(Sucursal.nombre)
        .all()
    )

    ventas_por_sucursal = [
        VentaPorSucursal(
            sucursalId=row.sucursalId,
            sucursalNombre=row.sucursalNombre,
            total_ventas=float(row.total_ventas or 0),
            cantidad_ventas=row.cantidad_ventas,
        )
        for row in ventas_por_sucursal_raw
    ]

    # Agrupado por empleado
    ventas_por_empleado_raw = (
        db.query(
            Empleado.id.label("empleadoId"),
            Empleado.nombre.label("nombre"),
            Empleado.apellido.label("apellido"),
            func.coalesce(func.sum(ventas_subq.c.total), 0).label("total_ventas"),
            func.count(ventas_subq.c.id).label("cantidad_ventas"),
        )
        .join(Empleado, ventas_subq.c.empleadoId == Empleado.id)
        .group_by(Empleado.id, Empleado.nombre, Empleado.apellido)
        .order_by(Empleado.nombre, Empleado.apellido)
        .all()
    )

    ventas_por_empleado = [
        VentaPorEmpleado(
            empleadoId=row.empleadoId,
            nombre=row.nombre,
            apellido=row.apellido,
            total_ventas=float(row.total_ventas or 0),
            cantidad_ventas=row.cantidad_ventas,
        )
        for row in ventas_por_empleado_raw
    ]

    # Agrupado por cliente
    ventas_por_cliente_raw = (
        db.query(
            Cliente.id.label("clienteId"),
            Cliente.razonSocial.label("clienteNombre"),
            func.coalesce(func.sum(ventas_subq.c.total), 0).label("total_ventas"),
            func.count(ventas_subq.c.id).label("cantidad_ventas"),
        )
        .join(Cliente, ventas_subq.c.clienteId == Cliente.id)
        .group_by(Cliente.id, Cliente.razonSocial)
        .order_by(Cliente.razonSocial)
        .all()
    )

    ventas_por_cliente = [
        VentaPorCliente(
            clienteId=row.clienteId,
            clienteNombre=row.clienteNombre,
            total_ventas=float(row.total_ventas or 0),
            cantidad_ventas=row.cantidad_ventas,
        )
        for row in ventas_por_cliente_raw
    ]

    # Agrupado por modelo (usando DetalleVenta + Producto + ModeloProducto)
    ventas_por_modelo_raw = (
        db.query(
            ModeloProducto.id.label("modeloId"),
            ModeloProducto.nombreModelo.label("nombreModelo"),
            ModeloProducto.marca.label("marca"),
            func.coalesce(func.sum(DetalleVenta.subtotal), 0).label("total_ventas"),
            func.count(DetalleVenta.id).label("cantidad_items"),
        )
        .join(Producto, Producto.modeloId == ModeloProducto.id)
        .join(DetalleVenta, DetalleVenta.productoId == Producto.id)
        .join(ventas_subq, ventas_subq.c.id == DetalleVenta.ventaId)
        .group_by(ModeloProducto.id, ModeloProducto.nombreModelo, ModeloProducto.marca)
        .order_by(ModeloProducto.marca, ModeloProducto.nombreModelo)
        .all()
    )

    ventas_por_modelo = [
        VentaPorModelo(
            modeloId=row.modeloId,
            nombreModelo=row.nombreModelo,
            marca=row.marca,
            total_ventas=float(row.total_ventas or 0),
            cantidad_items=row.cantidad_items,
        )
        for row in ventas_por_modelo_raw
    ]

    return ResumenVentasResponse(
        total_ventas=float(total_ventas or 0),
        cantidad_ventas=cantidad_ventas,
        por_dia=ventas_por_dia,
        por_sucursal=ventas_por_sucursal,
        por_empleado=ventas_por_empleado,
        por_cliente=ventas_por_cliente,
        por_modelo=ventas_por_modelo,
    )


# =====================  IMPORTACIONES  =====================

def obtener_resumen_importaciones(
    db: Session,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    proveedor_id: Optional[int] = None,
) -> ResumenImportacionesResponse:
    query = db.query(Importacion).filter(Importacion.estado == 1)

    if fecha_desde:
        query = query.filter(
            Importacion.fechaRegistro >= datetime.combine(
                fecha_desde, datetime.min.time()
            )
        )
    if fecha_hasta:
        query = query.filter(
            Importacion.fechaRegistro <= datetime.combine(
                fecha_hasta, datetime.max.time()
            )
        )
    if proveedor_id:
        query = query.filter(Importacion.proveedorId == proveedor_id)

    total_importaciones = query.count()

    por_proveedor_raw = (
        db.query(
            Proveedor.id.label("proveedorId"),
            Proveedor.razonSocial.label("proveedorNombre"),
            func.count(Importacion.id).label("cantidad_importaciones"),
        )
        .join(Proveedor, Importacion.proveedorId == Proveedor.id)
        .filter(Importacion.id.in_(q.id for q in query.all()))
        .group_by(Proveedor.id, Proveedor.razonSocial)
        .order_by(Proveedor.razonSocial)
        .all()
    )

    por_proveedor = [
        ImportacionPorProveedor(
            proveedorId=row.proveedorId,
            proveedorNombre=row.proveedorNombre,
            cantidad_importaciones=row.cantidad_importaciones,
        )
        for row in por_proveedor_raw
    ]

    return ResumenImportacionesResponse(
        total_importaciones=total_importaciones,
        por_proveedor=por_proveedor,
    )


# =====================  CONTROL DE STOCK  =====================

def obtener_reporte_stock(
    db: Session,
    solo_en_alerta: bool = False,
) -> StockResponse:
    """
    Se usa ModeloProducto.stockActual / stockMinimo y se completa la ficha
    con todos los datos del modelo (capacidad, unidad, color, garantía, etc.).
    """
    modelos = (
        db.query(ModeloProducto)
        .filter(ModeloProducto.estado == 1)
        .order_by(ModeloProducto.marca, ModeloProducto.nombreModelo)
        .all()
    )

    items: List[StockItem] = []
    total_en_alerta = 0

    for m in modelos:
        en_alerta = m.stockActual <= m.stockMinimo
        if solo_en_alerta and not en_alerta:
            continue

        if en_alerta:
            total_en_alerta += 1

        items.append(
            StockItem(
                modeloId=m.id,
                nombreModelo=m.nombreModelo,
                marca=m.marca,
                capacidadOTamano=m.capacidadOTamano,
                unidadMedida=m.unidadMedida,
                color=m.color,
                duracionGarantia=m.duracionGarantia,
                tipoGarantia=m.tipoGarantia,
                fechaRegistro=m.fechaRegistro,
                stock_actual=m.stockActual,
                stock_minimo=m.stockMinimo,
                en_alerta=bool(en_alerta),
            )
        )

    return StockResponse(
        total_modelos=len(items),
        total_en_alerta=total_en_alerta,
        items=items,
    )
