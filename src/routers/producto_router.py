# src/routes/producto_route.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.config.db import get_db
from src.schemas.producto import ProductoCreate, ProductoUpdate, ProductoOut
from src.controllers import producto_controller as controller

router = APIRouter(prefix="/productos", tags=["Productos"])

# Listar todos los productos activos
@router.get("/", response_model=list[ProductoOut])
def list_products(db: Session = Depends(get_db)):
    return controller.listar_productos(db)

@router.get("/by-serie/{numero_serie}")
def get_by_serie(numero_serie: str, db: Session = Depends(get_db)):
    prod = controller.obtener_producto_por_serie(db, numero_serie)
    # si no hay, devolvemos null para que el front sepa que está libre
    if not prod:
        return None
    return prod

# Obtener uno
@router.get("/{producto_id}", response_model=ProductoOut)
def get_product(producto_id: int, db: Session = Depends(get_db)):
    return controller.obtener_producto(db, producto_id)

# Crear
@router.post("/", response_model=ProductoOut, status_code=201)
def create_product(payload: ProductoCreate, db: Session = Depends(get_db)):
    return controller.crear_producto(db, payload)

# Actualizar
@router.put("/{producto_id}", response_model=ProductoOut)
def update_product(producto_id: int, payload: ProductoUpdate, db: Session = Depends(get_db)):
    return controller.actualizar_producto(db, producto_id, payload)

# Eliminar (lógico)
@router.delete("/{producto_id}")
def delete_product(producto_id: int, db: Session = Depends(get_db)):
    return controller.eliminar_producto(db, producto_id)
