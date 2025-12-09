# src/controllers/venta_controller.py
from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy import desc

from src.models.cliente import Cliente
from src.models.sucursal import Sucursal
from src.models.venta import Venta
from src.models.detalle_venta import DetalleVenta
from src.models.producto import Producto
from src.schemas.venta import VentaCreate
from src.models.modelo_producto import ModeloProducto


def _generar_siguiente_codigo(db: Session) -> str:
    """
    Genera el siguiente código de venta en formato 000001, 000002, etc.
    Basado en el último registro de la tabla Venta.
    """
    ultima = db.query(Venta).order_by(desc(Venta.id)).first()
    if not ultima or not ultima.codigoVenta:
        return "000001"
    nro = int(ultima.codigoVenta) + 1
    return f"{nro:06d}"

def crear_venta(db: Session, venta_in: VentaCreate) -> Venta:
    codigo = venta_in.codigoVenta or _generar_siguiente_codigo(db)
    total = sum(det.subtotal for det in venta_in.detalles)

    venta_db = Venta(
        empleadoId=venta_in.empleadoId,
        clienteId=venta_in.clienteId,
        sucursalId=venta_in.sucursalId,
        codigoVenta=codigo,
        total=total,
        fechaRegistro=datetime.utcnow(),
        estado=1,
    )
    db.add(venta_db)
    db.flush()  # obtengo id de la venta

    for det in venta_in.detalles:
        prod = (
            db.query(Producto)
            .filter(Producto.id == det.productoId, Producto.estado == 1)
            .first()
        )
        if not prod:
            raise HTTPException(
                status_code=400,
                detail=f"Producto {det.productoId} no existe o ya fue vendido",
            )

        # 🚨 Validar que el subtotal no sea menor al precioOrigen
        # (si por algo precioOrigen es None, usamos precio como fallback)
        precio_origen = float(prod.precioOrigen or prod.precio or 0)
        if float(det.subtotal) < precio_origen:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"El producto {prod.numeroSerie or prod.descripcion} "
                    f"no puede venderse por debajo del precio de origen "
                    f"(Bs {precio_origen:.2f})."
                ),
            )

        detalle_db = DetalleVenta(
            ventaId=venta_db.id,
            productoId=det.productoId,
            subtotal=det.subtotal,
        )
        db.add(detalle_db)

        # marcar producto como vendido
        prod.estado = 2
        db.add(prod)

        # 🔽 descontar 1 del modelo
        modelo = (
            db.query(ModeloProducto)
            .filter(ModeloProducto.id == prod.modeloId)
            .first()
        )
        if modelo and modelo.stockActual > 0:
            modelo.stockActual -= 1
            db.add(modelo)

    db.commit()
    db.refresh(venta_db)
    return venta_db


# src/controllers/venta_controller.py

def listar_ventas(
    db: Session,
    empleado_id: int | None = None,
    sucursal_id: int | None = None,
):
    query = db.query(Venta).filter(Venta.estado == 1)

    if empleado_id is not None:
        query = query.filter(Venta.empleadoId == empleado_id)

    if sucursal_id is not None:
        query = query.filter(Venta.sucursalId == sucursal_id)

    return query.order_by(Venta.fechaRegistro.desc()).all()


def obtener_venta_por_id(db: Session, venta_id: int):
    # 1. obtener la venta
    venta = (
        db.query(Venta)
        .filter(Venta.id == venta_id, Venta.estado == 1)
        .first()
    )
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada o inactiva")

    # 2. obtener cliente
    cliente = db.query(Cliente).filter(Cliente.id == venta.clienteId).first()

    # 3. obtener sucursal + ciudad
    sucursal = (
        db.query(Sucursal)
        .filter(Sucursal.id == venta.sucursalId)
        .first()
    )

    # 4. obtener detalles + producto + modelo + marca
    detalles = (
        db.query(DetalleVenta)
        .filter(DetalleVenta.ventaId == venta_id)
        .all()
    )

    detalles_out = []
    for det in detalles:
        prod = db.query(Producto).filter(Producto.id == det.productoId).first()

        modelo = None
        marca = None

        if prod:
            modelo = db.query(ModeloProducto).filter(
                ModeloProducto.id == prod.modeloId
            ).first()

            if modelo:
                marca = modelo.marca  # relación ya cargada

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
                        "nombre": getattr(marca, "nombre", None)
                    } if marca else None
                } if modelo else None
            }
        })

    # 5. respuesta final detallada
    return {
        "id": venta.id,
        "codigoVenta": venta.codigoVenta,
        "fechaRegistro": venta.fechaRegistro,
        "total": float(venta.total),
        "estado": venta.estado,

        "cliente": {
            "id": cliente.id,
            "razonSocial": cliente.razonSocial,
            "nit": cliente.nit,
            "telefono": cliente.telefono,
            "correo": cliente.correo
        } if cliente else None,

        "sucursal": {
            "id": sucursal.id,
            "nombre": sucursal.nombre,
            "direccion": sucursal.direccion,
            "telefono": sucursal.telefono,
            "ciudad": sucursal.ciudadNombre   # usando la property del modelo
        } if sucursal else None,

        "detalles": detalles_out
    }

# 👇 NUEVO
def cancelar_venta(db: Session, venta_id: int):
    venta = db.query(Venta).filter(Venta.id == venta_id, Venta.estado == 1).first()
    if not venta:
        raise HTTPException(status_code=404, detail="La venta no existe o ya está cancelada")

    detalles = db.query(DetalleVenta).filter(DetalleVenta.ventaId == venta_id).all()

    for det in detalles:
        prod = db.query(Producto).filter(Producto.id == det.productoId).first()
        if prod:
            # volver producto a disponible
            prod.estado = 1
            db.add(prod)

            # 🔼 devolver 1 al stock del modelo
            modelo = (
                db.query(ModeloProducto)
                .filter(ModeloProducto.id == prod.modeloId)
                .first()
            )
            if modelo:
                modelo.stockActual += 1
                db.add(modelo)

    # marcar venta como cancelada
    venta.estado = 0
    db.add(venta)
    db.commit()
    db.refresh(venta)

    return {"message": "Venta cancelada correctamente", "ventaId": venta_id}
