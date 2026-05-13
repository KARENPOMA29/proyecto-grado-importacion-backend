from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal
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

class MovimientoDetalleUpdate(BaseModel):
    almacenId: Optional[int] = None
    seccionId: Optional[int] = None
    categoriaId: Optional[int] = None
    importacionId: Optional[int] = None
    tipoMovimiento: Optional[str] = None

    productoDescripcion: Optional[str] = None
    productoPrecioOrigen: Optional[Decimal] = None
    productoPrecio: Optional[Decimal] = None
    productoObservado: Optional[int] = None
    productoObsDescripcion: Optional[str] = None

class MovimientoUpdate(BaseModel):
    productoId: Optional[int] = None
    almacenId: Optional[int] = None
    tipoMovimiento: Optional[str] = None
    usuarioId: Optional[int] = None  # también lo agregamos para coherencia


class CategoriaOut(BaseModel):
    id: int
    nombre: Optional[str] = None

    class Config:
        from_attributes = True


class ModeloProductoOut(BaseModel):
    id: int
    nombreModelo: Optional[str] = None

    class Config:
        from_attributes = True


class ImportacionOut(BaseModel):
    id: int
    codigo: Optional[str] = None

    class Config:
        from_attributes = True


class MovimientoOut(BaseModel):
    id: int
    productoId: int
    almacenId: int
    tipoMovimiento: Optional[str] = None
    fecha: Optional[datetime] = None
    estado: int

    productoSerie: Optional[str] = None
    productoDescripcion: Optional[str] = None
    productoEstado: Optional[int] = None
    productoObservado: Optional[int] = None
    productoObsDescripcion: Optional[str] = None

    almacenNombre: Optional[str] = None

    categoria: Optional[CategoriaOut] = None
    modeloProducto: Optional[ModeloProductoOut] = None
    importacion: Optional[ImportacionOut] = None

    class Config:
        from_attributes = True