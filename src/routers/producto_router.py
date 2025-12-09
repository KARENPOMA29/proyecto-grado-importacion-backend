# src/routers/producto_router.py
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from src.config.db import SessionLocal
from src.schemas.producto import ProductoCreate, ProductoUpdate, ProductoOut
from src.controllers import producto_controller as controller

router = APIRouter(
    prefix="/productos",
    tags=["Productos"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------------------------------------------------------------------
# POST /productos/  -> crear
# -------------------------------------------------------------------
@router.post("/", response_model=ProductoOut)
def crear_producto(producto: ProductoCreate, db: Session = Depends(get_db)):
    return controller.crear_producto(db, producto)


# -------------------------------------------------------------------
# GET /productos/  -> listar (con filtro de estado opcional)
#   ?estado=1  -> disponibles (por defecto)
#   ?estado=2  -> vendidos
#   ?estado=0  -> inactivos
#   sin estado -> por defecto 1 (disponibles)
# -------------------------------------------------------------------
@router.get("/", response_model=List[ProductoOut])
def listar_productos(
    estado: Optional[int] = Query(1, description="Estado del producto (0, 1, 2). Por defecto 1 = disponible"),
    db: Session = Depends(get_db),
):
    return controller.listar_productos(db, estado=estado)


# -------------------------------------------------------------------
# GET /productos/{id} -> obtener por ID (solo activos)
# -------------------------------------------------------------------
@router.get("/{producto_id}", response_model=ProductoOut)
def obtener_producto(producto_id: int, db: Session = Depends(get_db)):
    return controller.obtener_producto(db, producto_id)


# -------------------------------------------------------------------
# GET /productos/by-serie/{numero_serie} -> obtener por número de serie
#   Devuelve null si no existe o está inactivo
# -------------------------------------------------------------------
@router.get("/by-serie/{numero_serie}", response_model=Optional[ProductoOut])
def obtener_producto_por_serie(numero_serie: str, db: Session = Depends(get_db)):
    producto = controller.obtener_producto_por_serie(db, numero_serie)
    # No lanzamos 404; dejamos que el frontend reciba null si no hay
    return producto


# -------------------------------------------------------------------
# PUT /productos/{id} -> actualizar
# -------------------------------------------------------------------
@router.put("/{producto_id}", response_model=ProductoOut)
def actualizar_producto(
    producto_id: int,
    datos: ProductoUpdate,
    db: Session = Depends(get_db),
):
    return controller.actualizar_producto(db, producto_id, datos)


# -------------------------------------------------------------------
# DELETE /productos/{id} -> borrado lógico
# -------------------------------------------------------------------
@router.delete("/{producto_id}")
def eliminar_producto(producto_id: int, db: Session = Depends(get_db)):
    return controller.eliminar_producto(db, producto_id)
