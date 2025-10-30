# src/crud/movimiento.py
from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.models.movimiento_inventario import MovimientoInventario
from src.models.producto import Producto
from src.models.modelo_producto import ModeloProducto
from src.models.almacen import Almacen
from src.models.categoria import Categoria
from src.models.importacion import Importacion

from src.schemas.movimiento import MovimientoCreate, MovimientoUpdate


def _adjuntar_extras(db: Session, mov: MovimientoInventario):
  
    # 🔹 PRODUCTO
    if mov.productoId:
        prod = db.query(Producto).filter(
            Producto.id == mov.productoId,
            Producto.estado == 1
        ).first()
        mov.producto = prod

        # planos
        mov.productoSerie = prod.numeroSerie if prod else None
        mov.productoDescripcion = (prod.descripcion or prod.nombre) if prod else None

        # 🔹 MODELO (derivado del producto)
        if prod and prod.modeloId:
            modelo = db.query(ModeloProducto).filter(
                ModeloProducto.id == prod.modeloId
            ).first()
            mov.modeloProducto = modelo
        else:
            mov.modeloProducto = None

        # 🔹 CATEGORÍA (derivado del producto)
        if prod and prod.categoriaId:
            categoria = db.query(Categoria).filter(
                Categoria.id == prod.categoriaId
            ).first()
            mov.categoria = categoria
        else:
            mov.categoria = None

        # 🔹 IMPORTACIÓN (derivado del producto)
        if prod and prod.importacionId:
            imp = db.query(Importacion).filter(
                Importacion.id == prod.importacionId
            ).first()
            mov.importacion = imp
        else:
            mov.importacion = None

    else:
        mov.producto = None
        mov.productoSerie = None
        mov.productoDescripcion = None
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


def listar_movimientos(db: Session):
    movs = (
        db.query(MovimientoInventario)
        .order_by(MovimientoInventario.fecha.desc())
        .all()
    )
    for m in movs:
        _adjuntar_extras(db, m)
    return movs


def obtener_movimiento(db: Session, movimiento_id: int):
    mov = db.query(MovimientoInventario).get(movimiento_id)
    if not mov:
        raise HTTPException(status_code=404, detail="Movimiento no encontrado")

    _adjuntar_extras(db, mov)
    return mov


def crear_movimiento(db: Session, payload: MovimientoCreate, usuario_id: int | None = None):
    # validar producto
    prod = db.query(Producto).get(payload.productoId)
    if not prod:
        raise HTTPException(status_code=404, detail="Producto no existe")

    mov = MovimientoInventario(
        productoId=payload.productoId,
        almacenId=payload.almacenId,
        tipoMovimiento=payload.tipoMovimiento,
        usuarioId=usuario_id,
    )
    db.add(mov)

    # Ajuste de stockActual a nivel de ModeloProducto
    mp = db.query(ModeloProducto).get(prod.modeloId)
    if mp:
        if payload.tipoMovimiento == "ENTRADA":
            mp.stockActual = (mp.stockActual or 0) + 1
        elif payload.tipoMovimiento == "SALIDA":
            nuevo = (mp.stockActual or 0) - 1
            if nuevo < 0:
                nuevo = 0
            mp.stockActual = nuevo

    db.commit()
    db.refresh(mov)

    _adjuntar_extras(db, mov)
    return mov


def actualizar_movimiento(db: Session, movimiento_id: int, payload: MovimientoUpdate, usuario_id: int | None = None):
    mov = db.query(MovimientoInventario).get(movimiento_id)
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


def eliminar_movimiento(db: Session, movimiento_id: int):
    mov = db.query(MovimientoInventario).get(movimiento_id)
    if not mov:
        raise HTTPException(status_code=404, detail="Movimiento no encontrado")

    db.delete(mov)
    db.commit()
    return {"detail": "Movimiento eliminado"}
