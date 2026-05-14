from typing import Optional, List
from pydantic import BaseModel


# =========================
# DASHBOARD
# =========================

class ReporteEntradasDashboard(BaseModel):
    productosIngresados: int
    movimientosEntrada: int
    importacionesRelacionadas: int
    proveedoresRelacionados: int
    sucursalesConEntrada: int
    almacenesConEntrada: int

    costoTotalOrigen: float
    valorVentaEstimado: float
    utilidadEstimadaTotal: float

    productosObservados: int

    costoPromedioUnitario: float
    margenEstimadoPromedio: float


# =========================
# DETALLE
# =========================

class ReporteEntradaDetalle(BaseModel):
    movimientoId: int

    fechaEntrada: Optional[str]
    fechaEntradaSolo: Optional[str]

    productoId: int
    numeroSerie: Optional[str]
    productoDescripcion: Optional[str]

    observado: Optional[int]
    observadoTexto: Optional[str]
    obsDescripcion: Optional[str]

    precioOrigen: Optional[float]
    precioVenta: Optional[float]

    utilidadEstimada: Optional[float]
    margenEstimadoPorcentaje: Optional[float]

    categoriaId: Optional[int]
    categoriaNombre: Optional[str]

    modeloId: Optional[int]
    nombreModelo: Optional[str]

    color: Optional[str]
    capacidadOTamano: Optional[str]
    unidadMedida: Optional[str]
    capacidadTexto: Optional[str]

    stockMinimo: Optional[int]
    stockActual: Optional[int]

    almacenId: Optional[int]
    almacenNombre: Optional[str]

    sucursalId: Optional[int]
    sucursalNombre: Optional[str]

    ciudadId: Optional[int]
    ciudadNombre: Optional[str]

    importacionId: Optional[int]
    importacionCodigo: Optional[str]

    proveedorId: Optional[int]
    proveedorNombre: Optional[str]

    empleadoRegistroId: Optional[int]
    empleadoRegistroNombre: Optional[str]

    class Config:
        from_attributes = True


# =========================
# PAGINADO
# =========================

class ReporteEntradaDetalleResponse(BaseModel):
    items: List[ReporteEntradaDetalle]
    total: int
    page: int
    pageSize: int


# =========================
# POR DIA
# =========================

class ReporteEntradasPorDia(BaseModel):
    fecha: Optional[str]

    productosIngresados: int
    movimientosEntrada: int
    importacionesRelacionadas: int

    costoTotalOrigen: float
    valorVentaEstimado: float
    utilidadEstimadaTotal: float

    productosObservados: int


# =========================
# POR SUCURSAL
# =========================

class ReporteEntradasSucursalAlmacen(BaseModel):
    ciudadNombre: Optional[str]
    sucursalNombre: Optional[str]
    almacenNombre: Optional[str]

    productosIngresados: int
    importacionesRelacionadas: int
    proveedoresRelacionados: int

    costoTotalOrigen: float
    valorVentaEstimado: float
    utilidadEstimadaTotal: float

    productosObservados: int


# =========================
# POR PRODUCTO
# =========================

class ReporteEntradasProducto(BaseModel):
    categoriaNombre: Optional[str]

    nombreModelo: Optional[str]
    color: Optional[str]
    capacidadTexto: Optional[str]

    productosIngresados: int
    importacionesRelacionadas: int

    costoTotalOrigen: float
    valorVentaEstimado: float
    utilidadEstimadaTotal: float

    costoPromedioOrigen: float
    precioVentaPromedio: float

    productosObservados: int


# =========================
# POR IMPORTACION
# =========================

class ReporteEntradasImportacion(BaseModel):
    importacionId: Optional[int]
    importacionCodigo: Optional[str]

    proveedorNombre: Optional[str]

    fechaLlegada: Optional[str]

    productosIngresados: int
    categoriasIngresadas: int
    modelosIngresados: int

    costoTotalOrigen: float
    valorVentaEstimado: float
    utilidadEstimadaTotal: float

    productosObservados: int


# =========================
# POR PROVEEDOR
# =========================

class ReporteEntradasProveedor(BaseModel):
    proveedorId: Optional[int]
    proveedorNombre: Optional[str]

    proveedorEncargado: Optional[str]
    proveedorTelefono: Optional[str]

    productosIngresados: int
    importacionesRelacionadas: int

    costoTotalOrigen: float
    valorVentaEstimado: float
    utilidadEstimadaTotal: float

    productosObservados: int


# =========================
# STOCK ACTUAL
# =========================

class ReporteStockActual(BaseModel):
    sucursalId: Optional[int]
    sucursal: Optional[str]

    almacenId: Optional[int]
    almacen: Optional[str]

    seccionId: Optional[int]
    seccion: Optional[str]

    modeloId: Optional[int]
    nombreModelo: Optional[str]

    categoriaNombre: Optional[str]

    color: Optional[str]
    capacidadTexto: Optional[str]

    cantidad: int

    stockMinimo: Optional[int]
    estadoStock: Optional[str]

    precioOrigenPromedio: Optional[float]
    precioVentaPromedio: Optional[float]

    costoTotalStock: Optional[float]
    valorTotalStock: Optional[float]

    productosObservados: Optional[int]


# =========================
# OBSERVADOS
# =========================

class ReporteEntradasObservadas(ReporteEntradaDetalle):
    pass