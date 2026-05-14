from typing import Optional
from pydantic import BaseModel
from decimal import Decimal
from datetime import date, datetime


class ReporteVentasDashboardOut(BaseModel):
    cantidadVentas: int = 0
    productosVendidos: int = 0
    totalVendido: Decimal = 0
    ticketPromedio: Decimal = 0