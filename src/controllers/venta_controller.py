# src/controllers/venta_controller.py

from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy import String, desc, text, or_, func
from src.models.cliente import Cliente
from src.models.sucursal import Sucursal
from src.models.venta import Venta
from src.models.detalle_venta import DetalleVenta
from src.models.producto import Producto
from src.schemas.venta import VentaCreate
from src.models.modelo_producto import ModeloProducto
from src.models.empleado import Empleado
# =========================================================
# GENERAR CÓDIGO
# =========================================================

def _generar_siguiente_codigo(db: Session) -> str:
    ultima = db.query(Venta).order_by(desc(Venta.id)).first()

    if not ultima or not ultima.codigoVenta:
        return "000001"

    nro = int(ultima.codigoVenta) + 1
    return f"{nro:06d}"


# =========================================================
# VALIDAR PRODUCTO DISPONIBLE EN SUCURSAL
# =========================================================

def validar_producto_en_sucursal(
    db: Session,
    producto_id: int,
    sucursal_id: int,
):
    sql = text("""
        SELECT COUNT(*) AS disponible
        FROM vw_productos_disponibles_por_sucursal
        WHERE productoId = :producto_id
          AND sucursalId = :sucursal_id
    """)

    result = db.execute(
        sql,
        {
            "producto_id": producto_id,
            "sucursal_id": sucursal_id,
        },
    ).scalar()

    if int(result or 0) == 0:
        raise HTTPException(
            status_code=400,
            detail=(
                "El producto seleccionado no está disponible "
                "en la sucursal elegida."
            ),
        )


# =========================================================
# CREAR VENTA
# =========================================================

def crear_venta(db: Session, venta_in: VentaCreate) -> Venta:

    if not venta_in.detalles or len(venta_in.detalles) == 0:
        raise HTTPException(
            status_code=400,
            detail="La venta debe tener al menos un producto.",
        )

    codigo = venta_in.codigoVenta or _generar_siguiente_codigo(db)

    total = sum(float(det.subtotal or 0) for det in venta_in.detalles)

    if total <= 0:
        raise HTTPException(
            status_code=400,
            detail="El total de la venta debe ser mayor a cero.",
        )

    # =====================================================
    # VALIDAR CLIENTE
    # =====================================================

    cliente = (
        db.query(Cliente)
        .filter(
            Cliente.id == venta_in.clienteId,
            Cliente.estado == 1,
        )
        .first()
    )

    if not cliente:
        raise HTTPException(
            status_code=400,
            detail="Cliente no válido.",
        )

    # =====================================================
    # VALIDAR SUCURSAL
    # =====================================================

    sucursal = (
        db.query(Sucursal)
        .filter(Sucursal.id == venta_in.sucursalId)
        .first()
    )

    if not sucursal:
        raise HTTPException(
            status_code=400,
            detail="Sucursal no válida.",
        )

    # =====================================================
    # CREAR VENTA
    # =====================================================

    venta_db = Venta(
        empleadoId=venta_in.empleadoId,
        clienteId=venta_in.clienteId,
        sucursalId=venta_in.sucursalId,
        codigoVenta=codigo,
        total=total,
        estado=1,
    )

    db.add(venta_db)
    db.flush()

    # =====================================================
    # DETALLES
    # =====================================================

    for det in venta_in.detalles:

        # VALIDAR PRODUCTO EN SUCURSAL
        validar_producto_en_sucursal(
            db,
            det.productoId,
            venta_in.sucursalId,
        )

        # BUSCAR PRODUCTO
        prod = (
            db.query(Producto)
            .filter(
                Producto.id == det.productoId,
                Producto.estado == 1,
            )
            .first()
        )

        if not prod:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Producto {det.productoId} "
                    f"no existe o ya fue vendido."
                ),
            )

        # ================================================
        # VALIDAR PRECIO
        # ================================================

        precio_origen = float(
            prod.precioOrigen or prod.precio or 0
        )

        subtotal = float(det.subtotal or 0)

        if subtotal <= 0:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"El subtotal del producto "
                    f"{prod.numeroSerie or prod.descripcion} "
                    f"debe ser mayor a cero."
                ),
            )

        if subtotal < precio_origen:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"El producto "
                    f"{prod.numeroSerie or prod.descripcion} "
                    f"no puede venderse por debajo "
                    f"del precio de origen "
                    f"(Bs {precio_origen:.2f})."
                ),
            )

        # ================================================
        # CREAR DETALLE
        # ================================================

        detalle_db = DetalleVenta(
            ventaId=venta_db.id,
            productoId=det.productoId,
            subtotal=subtotal,
        )
        db.add(detalle_db)

        # ================================================
        # MARCAR PRODUCTO COMO VENDIDO
        # ================================================

        prod.estado = 2
        db.add(prod)

        

    # =====================================================
    # GUARDAR
    # =====================================================

    db.commit()
    db.refresh(venta_db)

    return venta_db


# =========================================================
# LISTAR VENTAS
# =========================================================

def listar_ventas(
    db: Session,
    empleado_id: int | None = None,
    sucursal_id: int | None = None,
    search: str | None = None,
    page: int = 1,
    page_size: int = 10,
):
    query = (
        db.query(Venta, Cliente, Empleado, Sucursal)
        .outerjoin(Cliente, Cliente.id == Venta.clienteId)
        .outerjoin(Empleado, Empleado.id == Venta.empleadoId)
        .outerjoin(Sucursal, Sucursal.id == Venta.sucursalId)
        .filter(Venta.estado == 1)
    )

    if empleado_id is not None:
        query = query.filter(Venta.empleadoId == empleado_id)

    if sucursal_id is not None:
        query = query.filter(Venta.sucursalId == sucursal_id)

    if search:
        term = f"%{search.strip().lower()}%"

        query = query.filter(
            or_(
                func.lower(func.coalesce(Venta.codigoVenta, "")).like(term),
                func.lower(func.coalesce(Cliente.razonSocial, "")).like(term),
                func.lower(func.coalesce(Cliente.nit, "")).like(term),
                func.lower(func.coalesce(Empleado.nombre, "")).like(term),
                func.lower(func.coalesce(Empleado.apellido, "")).like(term),
                func.lower(func.coalesce(Sucursal.nombre, "")).like(term),
                func.cast(Venta.total, String).like(f"%{search.strip()}%"),
            )
        )

    total = query.count()

    rows = (
        query.order_by(Venta.fechaRegistro.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    items = []

    for venta, cliente, empleado, sucursal in rows:
        empleado_nombre = "—"
        if empleado:
            empleado_nombre = f"{getattr(empleado, 'nombre', '')} {getattr(empleado, 'apellido', '')}".strip()

        items.append({
            "id": venta.id,
            "codigoVenta": venta.codigoVenta,
            "clienteId": venta.clienteId,
            "empleadoId": venta.empleadoId,
            "sucursalId": venta.sucursalId,
            "total": float(venta.total or 0),
            "fechaRegistro": venta.fechaRegistro,
            "estado": venta.estado,

            "clienteNombre": cliente.razonSocial if cliente else "—",
            "clienteNit": cliente.nit if cliente else None,
            "empleadoNombre": empleado_nombre,
            "sucursalNombre": sucursal.nombre if sucursal else "—",
        })

    return {
        "items": items,
        "total": total,
    }

# =========================================================
# OBTENER VENTA POR ID
# =========================================================

def obtener_venta_por_id(db: Session, venta_id: int):

    venta = (
        db.query(Venta)
        .filter(
            Venta.id == venta_id,
            Venta.estado == 1,
        )
        .first()
    )

    if not venta:
        raise HTTPException(
            status_code=404,
            detail="Venta no encontrada o inactiva",
        )

    cliente = (
        db.query(Cliente)
        .filter(Cliente.id == venta.clienteId)
        .first()
    )
    empleado = (
        db.query(Empleado)
        .filter(Empleado.id == venta.empleadoId)
        .first()
    )

    sucursal = (
        db.query(Sucursal)
        .filter(Sucursal.id == venta.sucursalId)
        .first()
    )

    detalles = (
        db.query(DetalleVenta)
        .filter(DetalleVenta.ventaId == venta_id)
        .all()
    )

    detalles_out = []

    for det in detalles:

        prod = (
            db.query(Producto)
            .filter(Producto.id == det.productoId)
            .first()
        )

        modelo = None
        marca = None

        if prod:

            modelo = (
                db.query(ModeloProducto)
                .filter(ModeloProducto.id == prod.modeloId)
                .first()
            )

            if modelo:
                marca = modelo.marca

        detalles_out.append({
            "id": det.id,
            "subtotal": float(det.subtotal),

            "producto": {
                "id": prod.id if prod else None,
                "numeroSerie": getattr(prod, "numeroSerie", None),
                "descripcion": getattr(prod, "descripcion", None),
                "precio": float(prod.precio) if prod else None,

                "modelo": {
                    "id": modelo.id if modelo else None,
                    "nombreModelo": getattr(modelo, "nombreModelo", None),
                    "color": getattr(modelo, "color", None),
                    "capacidadOTamano": getattr(modelo, "capacidadOTamano", None),
                    "stockActual": getattr(modelo, "stockActual", None),
                    "urlImagen": getattr(modelo, "urlImagen", None),

                    "marca": {
                        "id": marca.id if marca else None,
                        "nombre": getattr(marca, "nombre", None),
                    } if marca else None,
                } if modelo else None,
            },
        })

    return {
    "id": venta.id,
    "codigoVenta": venta.codigoVenta,
    "fechaRegistro": venta.fechaRegistro,
    "total": float(venta.total),
    "estado": venta.estado,

    "clienteId": venta.clienteId,
    "empleadoId": venta.empleadoId,
    "sucursalId": venta.sucursalId,

    "cliente": {
        "id": cliente.id,
        "razonSocial": cliente.razonSocial,
        "nit": cliente.nit,
        "telefono": cliente.telefono,
        "correo": cliente.correo,
    } if cliente else None,

    "empleado": {
        "id": empleado.id,
        "nombre": empleado.nombre,
        "apellido": empleado.apellido,
        "ci": empleado.ci,
        "telefono": empleado.telefono,
        "correo": empleado.correo,
    } if empleado else None,

    "sucursal": {
        "id": sucursal.id,
        "nombre": sucursal.nombre,
        "direccion": sucursal.direccion,
        "telefono": sucursal.telefono,
        "ciudad": sucursal.ciudadNombre,
    } if sucursal else None,

    "detalles": detalles_out,
}
    


# =========================================================
# CANCELAR VENTA
# =========================================================

def cancelar_venta(db: Session, venta_id: int):

    venta = (
        db.query(Venta)
        .filter(
            Venta.id == venta_id,
            Venta.estado == 1,
        )
        .first()
    )

    if not venta:
        raise HTTPException(
            status_code=404,
            detail="La venta no existe o ya está cancelada",
        )

    detalles = (
        db.query(DetalleVenta)
        .filter(DetalleVenta.ventaId == venta_id)
        .all()
    )

    for det in detalles:

        prod = (
            db.query(Producto)
            .filter(Producto.id == det.productoId)
            .first()
        )

        if prod:

            prod.estado = 1
            db.add(prod)

            modelo = (
                db.query(ModeloProducto)
                .filter(ModeloProducto.id == prod.modeloId)
                .first()
            )

            if modelo:
                modelo.stockActual += 1
                db.add(modelo)

    venta.estado = 0

    db.add(venta)

    db.commit()
    db.refresh(venta)

    return {
        "message": "Venta cancelada correctamente",
        "ventaId": venta_id,
    }