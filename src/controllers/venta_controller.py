# src/controllers/venta_controller.py
from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy import desc

from src.models.venta import Venta
from src.models.detalle_venta import DetalleVenta
from src.models.producto import Producto
from src.schemas.venta import VentaCreate


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
    # Generar el código automáticamente si no viene desde el frontend
    codigo = venta_in.codigoVenta or _generar_siguiente_codigo(db)

    # Calcular total
    total = sum(det.subtotal for det in venta_in.detalles)

    venta_db = Venta(
        empleadoId=venta_in.empleadoId,
        clienteId=venta_in.clienteId,
        sucursalId=venta_in.sucursalId,
        codigoVenta=codigo,
        total=total,
        fechaRegistro=datetime.utcnow(),
        estado=1,  # activo
    )
    db.add(venta_db)
    db.flush()  # ya tengo venta_db.id

    # Procesar los detalles de venta
    for det in venta_in.detalles:
      # solo productos disponibles
      prod = (
          db.query(Producto)
          .filter(Producto.id == det.productoId, Producto.estado == 1)
          .first()
      )
      if not prod:
          raise HTTPException(
              status_code=400,
              detail=f"Producto {det.productoId} no existe o ya está vendido",
          )

      detalle_db = DetalleVenta(
          ventaId=venta_db.id,
          productoId=det.productoId,
          subtotal=det.subtotal,
      )
      db.add(detalle_db)

      # Marcar producto como vendido
      prod.estado = 2  # 1 = disponible, 2 = vendido
      db.add(prod)

    db.commit()
    db.refresh(venta_db)
    return venta_db


def listar_ventas(db: Session):
    return (
        db.query(Venta)
        .filter(Venta.estado == 1)
        .order_by(Venta.fechaRegistro.desc())
        .all()
    )


def obtener_venta_por_id(db: Session, venta_id: int):
    # 1. obtener la venta
    venta = (
        db.query(Venta)
        .filter(Venta.id == venta_id, Venta.estado == 1)
        .first()
    )
    if not venta:
      raise HTTPException(status_code=404, detail="Venta no encontrada o inactiva")

    # 2. obtener detalles
    detalles = (
        db.query(DetalleVenta)
        .filter(DetalleVenta.ventaId == venta_id)
        .all()
    )

    # 3. armar respuesta manual (dict) para que el front la tenga clara
    return {
        "id": venta.id,
        "empleadoId": venta.empleadoId,
        "clienteId": venta.clienteId,
        "sucursalId": venta.sucursalId,
        "codigoVenta": venta.codigoVenta,
        "total": venta.total,
        "fechaRegistro": venta.fechaRegistro,
        "estado": venta.estado,
        # 👇 devolvemos los detalles en un array
        "detalles": [
            {
                "id": det.id,
                "productoId": det.productoId,
                "subtotal": det.subtotal,
            }
            for det in detalles
        ],
    }

# 👇 NUEVO
def cancelar_venta(db: Session, venta_id: int):
    """
    Cancela/anula una venta:
    - marca la venta como inactiva/anulada
    - vuelve a poner en disponible (estado = 1) todos los productos de esa venta
    """
    # 1. obtener la venta
    venta = db.query(Venta).filter(Venta.id == venta_id, Venta.estado == 1).first()
    if not venta:
        raise HTTPException(status_code=404, detail="La venta no existe o ya está cancelada")

    # 2. obtener sus detalles
    detalles = db.query(DetalleVenta).filter(DetalleVenta.ventaId == venta_id).all()

    # 3. recorrer productos y devolverlos a disponible
    for det in detalles:
        prod = db.query(Producto).filter(Producto.id == det.productoId).first()
        if prod:
            prod.estado = 1  # disponible
            db.add(prod)

    # 4. marcar la venta como cancelada
    venta.estado = 0  # o 2 = anulada, según tu convención
    # si quieres guardar fecha de cancelación, aquí:
    # venta.fechaActualizacion = datetime.utcnow()

    db.add(venta)
    db.commit()
    db.refresh(venta)

    return {"message": "Venta cancelada correctamente", "ventaId": venta_id}
