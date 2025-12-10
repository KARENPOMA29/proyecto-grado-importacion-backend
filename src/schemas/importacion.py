# src/schemas/importacion.py
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class ImportacionBase(BaseModel):
    codigo: str = Field(..., max_length=50)
    proveedorId: int
    fechaLlegada: date
    estado: int = Field(..., description="Estado de la importación (SmallInteger)")
    descripcion: Optional[str] = Field(None, max_length=200)

# 👇 minis para usar en respuestas
class ProveedorMini(BaseModel):
    id: int
    razonSocial: str

    model_config = ConfigDict(from_attributes=True)

class EmpleadoMini(BaseModel):
    id: int
    nombre: str
    apellido: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class ImportacionCreate(ImportacionBase):
    empleadoId: int
    idEmpleadoAsignado: int

class ImportacionUpdate(BaseModel):
    proveedorId: Optional[int] = None
    fechaLlegada: Optional[date] = None
    estado: Optional[int] = Field(None, description="Estado de la importación (SmallInteger)")
    descripcion: Optional[str] = Field(None, max_length=200)
    empleadoId: Optional[int] = None
    idEmpleadoAsignado: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

class ImportOut(BaseModel):
    id: int
    codigo: str | None = None

    model_config = ConfigDict(from_attributes=True)

class ImportacionOut(ImportacionBase):
    id: int
    empleadoId: int
    idEmpleadoAsignado: int
    fechaRegistro: datetime

    # 👇 nuevos campos anidados
    proveedor: Optional[ProveedorMini] = None
    empleadoAsignado: Optional[EmpleadoMini] = None

    model_config = ConfigDict(from_attributes=True)
