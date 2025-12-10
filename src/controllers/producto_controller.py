# src/controllers/producto_controller.py
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException

from src.models.producto import Producto
from src.schemas.producto import ProductoCreate, ProductoUpdate


# -------------------------------------------------------------------
# CREAR PRODUCTO
# -------------------------------------------------------------------
def crear_producto(db: Session, producto: ProductoCreate):
    # Validar número de serie único (activos o vendidos)
    if producto.numeroSerie:
        existente = (
            db.query(Producto)
            .filter(
                Producto.numeroSerie == producto.numeroSerie,
                Producto.estado.in_([1, 2]),  # 1 = activo, 2 = vendido
            )
            .first()
        )
        if existente:
            raise HTTPException(
                status_code=400,
                detail="Ya existe un producto con ese número de serie (activo o vendido).",
            )

    data = producto.model_dump()  # 👈 compatibilidad Pydantic v2
    nuevo = Producto(**data)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


# -------------------------------------------------------------------
# OBTENER PRODUCTO POR NÚMERO DE SERIE
# -------------------------------------------------------------------
def obtener_producto_por_serie(db: Session, numero_serie: str):
    producto = (
      db.query(Producto)
      .filter(
          Producto.numeroSerie == numero_serie,
          Producto.estado.in_([1, 2]),  # activos o vendidos
      )
      .first()
    )
    return producto


# -------------------------------------------------------------------
# LISTAR PRODUCTOS (con filtro opcional por estado)
#   estado = 1 -> solo disponibles (por defecto)
#   estado = 2 -> vendidos
#   estado = 0 -> inactivos
#   estado = None -> todos
# -------------------------------------------------------------------
def listar_productos(
    db: Session,
    estado: Optional[int] = 1,
    observado: Optional[int] = None,
    categoriaId: Optional[int] = None,
    modeloId: Optional[int] = None,
    importacionId: Optional[int] = None,
    numeroSerie: Optional[str] = None,
):
    query = db.query(Producto)

    if estado is not None:
        query = query.filter(Producto.estado == estado)

    if observado is not None:
        query = query.filter(Producto.observado == observado)

    if categoriaId is not None:
        query = query.filter(Producto.categoriaId == categoriaId)

    if modeloId is not None:
        query = query.filter(Producto.modeloId == modeloId)

    if importacionId is not None:
        query = query.filter(Producto.importacionId == importacionId)

    if numeroSerie:
        # búsqueda parcial (contiene)
        like_pattern = f"%{numeroSerie}%"
        query = query.filter(Producto.numeroSerie.ilike(like_pattern))

    return query.all()

# -------------------------------------------------------------------
# OBTENER PRODUCTO POR ID (solo activos)
# -------------------------------------------------------------------
def obtener_producto(db: Session, producto_id: int):
    producto = (
        db.query(Producto)
        .filter(Producto.id == producto_id, Producto.estado == 1)
        .first()
    )
    if not producto:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado o inactivo."
        )
    return producto


# -------------------------------------------------------------------
# ACTUALIZAR PRODUCTO
# -------------------------------------------------------------------
def actualizar_producto(db: Session, producto_id: int, datos: ProductoUpdate):
    producto = (
        db.query(Producto)
        .filter(Producto.id == producto_id, Producto.estado == 1)
        .first()
    )
    if not producto:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado o inactivo."
        )

    # Validar duplicado de número de serie si lo está cambiando
    if datos.numeroSerie is not None:
        existe = (
            db.query(Producto)
            .filter(
                Producto.numeroSerie == datos.numeroSerie,
                Producto.estado.in_([1, 2]),
                Producto.id != producto_id,
            )
            .first()
        )
        if existe:
            raise HTTPException(
                status_code=400,
                detail="Ya existe otro producto con ese número de serie (activo o vendido).",
            )

    # Aplicar actualizaciones
    update_data = datos.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(producto, key, value)

    db.commit()
    db.refresh(producto)
    return producto


# -------------------------------------------------------------------
# ELIMINAR PRODUCTO (lógico)
# -------------------------------------------------------------------
def eliminar_producto(db: Session, producto_id: int):
    producto = (
        db.query(Producto)
        .filter(Producto.id == producto_id, Producto.estado == 1)
        .first()
    )
    if not producto:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado o ya eliminado."
        )

    producto.estado = 0  # Borrado lógico
    db.commit()
    return {"mensaje": "Producto eliminado correctamente (lógico)."}
