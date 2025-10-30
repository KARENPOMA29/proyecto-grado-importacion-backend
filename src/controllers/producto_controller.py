# src/controllers/producto_controller.py
from sqlalchemy.orm import Session
from fastapi import HTTPException

from src.models.producto import Producto
from src.schemas.producto import ProductoCreate, ProductoUpdate


def crear_producto(db: Session, producto: ProductoCreate):
    # validar numeroSerie único (solo activos)
    if producto.numeroSerie:
      existente = (
          db.query(Producto)
          .filter(
              Producto.numeroSerie == producto.numeroSerie,
              Producto.estado == 1,
          )
          .first()
      )
      if existente:
          raise HTTPException(
              status_code=400,
              detail="Ya existe un producto activo con ese número de serie.",
          )

    nuevo = Producto(**producto.dict())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


def listar_productos(db: Session):
    # solo activos
    return db.query(Producto).filter(Producto.estado == 1).all()


def obtener_producto(db: Session, producto_id: int):
    producto = (
        db.query(Producto)
        .filter(Producto.id == producto_id, Producto.estado == 1)
        .first()
    )
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado o inactivo")
    return producto


def actualizar_producto(db: Session, producto_id: int, datos: ProductoUpdate):
    producto = (
        db.query(Producto)
        .filter(Producto.id == producto_id, Producto.estado == 1)
        .first()
    )
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado o inactivo")

    # si actualiza numeroSerie, validamos que no choque
    if datos.numeroSerie is not None:
        existe = (
            db.query(Producto)
            .filter(
                Producto.numeroSerie == datos.numeroSerie,
                Producto.estado == 1,
                Producto.id != producto_id,
            )
            .first()
        )
        if existe:
            raise HTTPException(
                status_code=400,
                detail="Ya existe otro producto activo con ese número de serie.",
            )

    for key, value in datos.dict(exclude_unset=True).items():
        setattr(producto, key, value)

    db.commit()
    db.refresh(producto)
    return producto


def eliminar_producto(db: Session, producto_id: int):
    producto = (
        db.query(Producto)
        .filter(Producto.id == producto_id, Producto.estado == 1)
        .first()
    )
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado o ya eliminado")

    producto.estado = 0  # borrado lógico
    db.commit()
    return {"mensaje": "Producto eliminado correctamente (lógico)"}
