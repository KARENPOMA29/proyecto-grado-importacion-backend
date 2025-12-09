from datetime import date, datetime
from typing import List
from pydantic import BaseModel


# =====================  VENTAS  =====================

class VentaPorDia(BaseModel):
    fecha: date
    total_ventas: float
    cantidad_ventas: int


class VentaPorSucursal(BaseModel):
    sucursalId: int
    sucursalNombre: str
    total_ventas: float
    cantidad_ventas: int


class VentaPorEmpleado(BaseModel):
    empleadoId: int
    nombre: str
    apellido: str
    total_ventas: float
    cantidad_ventas: int


class VentaPorCliente(BaseModel):
    clienteId: int
    clienteNombre: str   # razonSocial
    total_ventas: float
    cantidad_ventas: int


class VentaPorModelo(BaseModel):
    modeloId: int
    nombreModelo: str
    marca: str
    total_ventas: float      # suma de subtotales
    cantidad_items: int      # cantidad de ítems vendidos (detalles)


class ResumenVentasResponse(BaseModel):
    total_ventas: float
    cantidad_ventas: int
    por_dia: List[VentaPorDia]
    por_sucursal: List[VentaPorSucursal]
    por_empleado: List[VentaPorEmpleado]
    por_cliente: List[VentaPorCliente]
    por_modelo: List[VentaPorModelo]
           

class ImportacionPorProveedor(BaseModel):
    proveedorId: int
    proveedorNombre: str
    cantidad_importaciones: int


class ResumenImportacionesResponse(BaseModel):
    total_importaciones: int
    por_proveedor: List[ImportacionPorProveedor]


# =====================  CONTROL DE STOCK  =====================

class StockItem(BaseModel):
    modeloId: int
    nombreModelo: str
    marca: str
    capacidadOTamano: int
    unidadMedida: str
    color: str
    duracionGarantia: int
    tipoGarantia: str
    fechaRegistro: datetime
    stock_actual: int
    stock_minimo: int
    en_alerta: bool


class StockResponse(BaseModel):
    total_modelos: int
    total_en_alerta: int
    items: List[StockItem]
