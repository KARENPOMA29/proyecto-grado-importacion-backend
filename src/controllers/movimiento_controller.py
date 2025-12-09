# src/controllers/movimiento_controller.py
from typing import Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.models.movimiento_inventario import MovimientoInventario
from src.models.producto import Producto
from src.models.modelo_producto import ModeloProducto
from src.models.almacen import Almacen
from src.models.categoria import Categoria
from src.models.importacion import Importacion

from src.schemas.movimiento import MovimientoCreate, MovimientoUpdate
# src/controllers/movimiento_controller.py

def _adjuntar_extras(db: Session, mov: MovimientoInventario):
    """
    Completa el objeto movimiento con:
    - producto, modeloProducto, categoria, importacion
    - campos planos: productoSerie, productoDescripcion,
      productoObservado, productoObsDescripcion, almacenNombre
    """

    # 🔹 PRODUCTO
    if mov.productoId:
        prod = (
            db.query(Producto)
            .filter(Producto.id == mov.productoId)  # 👈 SIN filtro por estado
            .first()
        )
        mov.producto = prod

        if prod:
            mov.productoSerie = prod.numeroSerie
            mov.productoDescripcion = prod.descripcion
            mov.productoObservado = prod.observado
            mov.productoObsDescripcion = prod.obsDescripcion
        else:
            mov.productoSerie = None
            mov.productoDescripcion = None
            mov.productoObservado = None
            mov.productoObsDescripcion = None

        # 🔹 MODELO
        if prod and prod.modeloId:
            modelo = (
                db.query(ModeloProducto)
                .filter(ModeloProducto.id == prod.modeloId)
                .first()
            )
            mov.modeloProducto = modelo
        else:
            mov.modeloProducto = None

        # 🔹 CATEGORÍA
        if prod and prod.categoriaId:
            categoria = (
                db.query(Categoria)
                .filter(Categoria.id == prod.categoriaId)
                .first()
            )
            mov.categoria = categoria
        else:
            mov.categoria = None

        # 🔹 IMPORTACIÓN
        if prod and prod.importacionId:
            imp = (
                db.query(Importacion)
                .filter(Importacion.id == prod.importacionId)
                .first()
            )
            mov.importacion = imp
        else:
            mov.importacion = None

    else:
        mov.producto = None
        mov.productoSerie = None
        mov.productoDescripcion = None
        mov.productoObservado = None
        mov.productoObsDescripcion = None
        mov.modeloProducto = None
        mov.categoria = None
        mov.importacion = None

    # 🔹 ALMACÉN
    if mov.almacenId:
        a = db.query(Almacen).filter(Almacen.id == mov.almacenId).first()
        mov.almacen = a
        mov.almacenNombre = a.nombre if a else None
    else:
        mov.almacen = None
        mov.almacenNombre = None

    return mov

# ----------------------------------------------------
# 🔸 LISTAR SOLO MOVIMIENTOS ACTIVOS
# ----------------------------------------------------
def listar_movimientos(
    db: Session,
    usuario_id: Optional[int] = None,
    almacen_id: Optional[int] = None,
):
    query = db.query(MovimientoInventario).filter(
        MovimientoInventario.estado == 1  # 👈 solo activos
    )

    # 👇 si viene usuario_id, filtramos por el usuario que realizó el movimiento
    if usuario_id is not None:
        query = query.filter(MovimientoInventario.usuarioId == usuario_id)

    # 👇 si viene almacen_id, filtramos por almacén
    if almacen_id is not None:
        query = query.filter(MovimientoInventario.almacenId == almacen_id)

    movs = query.order_by(MovimientoInventario.fecha.desc()).all()

    for m in movs:
        _adjuntar_extras(db, m)

    return movs
# ----------------------------------------------------
# 🔸 OBTENER MOVIMIENTO (solo si activo)
# ----------------------------------------------------
def obtener_movimiento(db: Session, movimiento_id: int):
    mov = (
        db.query(MovimientoInventario)
        .filter(
            MovimientoInventario.id == movimiento_id,
            MovimientoInventario.estado == 1,  # 👈 solo activos
        )
        .first()
    )
    if not mov:
        raise HTTPException(status_code=404, detail="Movimiento no encontrado")

    _adjuntar_extras(db, mov)
    return mov


# ----------------------------------------------------
# 🔸 CREAR MOVIMIENTO
# ----------------------------------------------------
def crear_movimiento(
    db: Session,
    payload: MovimientoCreate,
    usuario_id: int | None = None,
):
    prod = db.query(Producto).get(payload.productoId)
    if not prod:
        raise HTTPException(status_code=404, detail="Producto no existe")

    mov = MovimientoInventario(
        productoId=payload.productoId,
        almacenId=payload.almacenId,
        tipoMovimiento=payload.tipoMovimiento,
        usuarioId=usuario_id,
        estado=1,  # 👈 activo por defecto
    )
    db.add(mov)

    # Ajuste de stockActual
    if prod.modeloId:
        mp = db.query(ModeloProducto).get(prod.modeloId)
        if mp:
            if payload.tipoMovimiento == "ENTRADA":
                mp.stockActual = (mp.stockActual or 0) + 1
            elif payload.tipoMovimiento == "SALIDA":
                nuevo = (mp.stockActual or 0) - 1
                mp.stockActual = nuevo if nuevo >= 0 else 0

    db.commit()
    db.refresh(mov)

    _adjuntar_extras(db, mov)
    return mov


# ----------------------------------------------------
# 🔸 ACTUALIZAR MOVIMIENTO
# ----------------------------------------------------
def actualizar_movimiento(
    db: Session,
    movimiento_id: int,
    payload: MovimientoUpdate,
    usuario_id: int | None = None,
):
    mov = (
        db.query(MovimientoInventario)
        .filter(
            MovimientoInventario.id == movimiento_id,
            MovimientoInventario.estado == 1,  # 👈 solo activos
        )
        .first()
    )
    if not mov:
        raise HTTPException(status_code=404, detail="Movimiento no encontrado")

    if payload.productoId is not None:
        prod = db.query(Producto).get(payload.productoId)
        if not prod:
            raise HTTPException(status_code=404, detail="Producto no existe")
        mov.productoId = payload.productoId

    if payload.almacenId is not None:
        mov.almacenId = payload.almacenId

    if payload.tipoMovimiento is not None:
        mov.tipoMovimiento = payload.tipoMovimiento

    if usuario_id is not None:
        mov.usuarioId = usuario_id

    db.commit()
    db.refresh(mov)

    _adjuntar_extras(db, mov)
    return mov


# ----------------------------------------------------
# 🔸 "ELIMINAR" MOVIMIENTO = MARCAR INACTIVO
# ----------------------------------------------------
def eliminar_movimiento(db: Session, movimiento_id: int):
    mov = db.query(MovimientoInventario).get(movimiento_id)
    if not mov:
        raise HTTPException(status_code=404, detail="Movimiento no encontrado")

    # en vez de borrar, solo marcamos como inactivo
    mov.estado = 0
    db.commit()
    return {"detail": "Movimiento marcado como inactivo"}
