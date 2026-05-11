# src/schemas/control_importacion.py

from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional

class ControlImportacionOut(BaseModel):
    id: int
    codigo: Optional[str]

    proveedorNombre: Optional[str]
    proveedorEncargado: Optional[str]

    empleadoAsignadoNombre: Optional[str]

    fechaRegistro: Optional[datetime]
    fechaLlegada: Optional[date]

    estado: Optional[int]

    descripcion: Optional[str]

    diasParaLlegada: Optional[int]

    situacion: Optional[str]

    class Config:
        from_attributes = True