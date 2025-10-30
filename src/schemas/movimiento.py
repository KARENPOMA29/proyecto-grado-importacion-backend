# src/schemas/movimiento.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from src.schemas.producto import ProductoOut
from src.schemas.almacen import AlmacenOut
from src.schemas.modelo_producto import ModeloProductoOut
from src.schemas.categoria import CategoriaOut
from src.schemas.importacion import ImportOut


class MovimientoBase(BaseModel):
    productoId: int
    almacenId: int
    tipoMovimiento: str


class MovimientoCreate(MovimientoBase):
    pass


class MovimientoUpdate(BaseModel):
    productoId: Optional[int] = None
    almacenId: Optional[int] = None
    tipoMovimiento: Optional[str] = None


class MovimientoOut(MovimientoBase):
    id: int
    usuarioId: Optional[int] = None
    fecha: Optional[datetime] = None

    # objetos embebidos
    producto: Optional[ProductoOut] = None
    almacen: Optional[AlmacenOut] = None
    modeloProducto: Optional[ModeloProductoOut] = None
    categoria: Optional[CategoriaOut] = None
    importacion: Optional[ImportOut] = None

    # campos planos para el details
    productoSerie: Optional[str] = None
    productoDescripcion: Optional[str] = None
    almacenNombre: Optional[str] = None

    class Config:
        orm_mode = True
