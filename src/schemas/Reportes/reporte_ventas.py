# src/schemas/reporte_ventas.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class VentaReporteItem(BaseModel):
    # Datos de la venta
    ventaId: int
    codigoVenta: str
    fechaVenta: datetime
    totalVenta: float

    # Empleado
    empleadoId: int
    empleadoNombre: str

    # Cliente
    clienteId: int
    clienteNombre: str
    clienteNit: str

    # Sucursal / Ciudad
    sucursalId: int
    sucursalNombre: str
    ciudadId: Optional[int] = None
    ciudadNombre: Optional[str] = None

    # Detalle / Producto
    detalleId: int
    productoId: int
    numeroSerie: str
    modeloNombre: str
    categoriaNombre: str
    marcaNombre: Optional[str] = None
    almacenId: Optional[int] = None
    almacenNombre: Optional[str] = None

    precioOrigen: float
    precioVenta: float
    subtotal: float

    class Config:
        from_attributes = True
