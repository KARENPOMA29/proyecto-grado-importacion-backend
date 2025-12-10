# src/schemas/venta.py
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional


class DetalleVentaBase(BaseModel):
    productoId: int
    subtotal: float  # podrías calcularlo del precio del producto, pero lo dejo así


class DetalleVentaCreate(DetalleVentaBase):
    pass


class DetalleVentaOut(DetalleVentaBase):
    id: int

    class Config:
        from_attributes = True


class VentaBase(BaseModel):
    empleadoId: int
    clienteId: int
    sucursalId: Optional[int] = None
    codigoVenta: Optional[str] = None


class VentaCreate(VentaBase):
    detalles: List[DetalleVentaCreate]


class VentaOut(VentaBase):
    id: int
    total: float
    fechaRegistro: datetime
    estado: int 
    detalles: List[DetalleVentaOut]

    class Config:
        from_attributes = True

