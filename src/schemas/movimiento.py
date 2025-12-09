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


# ✅ AQUI AGREGAMOS usuarioId OPCIONAL
class MovimientoCreate(MovimientoBase):
    usuarioId: Optional[int] = None


class MovimientoUpdate(BaseModel):
    productoId: Optional[int] = None
    almacenId: Optional[int] = None
    tipoMovimiento: Optional[str] = None
    usuarioId: Optional[int] = None  # también lo agregamos para coherencia


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

    # nuevos: info de observación del producto
    productoObservado: Optional[int] = None
    productoObsDescripcion: Optional[str] = None

    class Config:
        orm_mode = True
