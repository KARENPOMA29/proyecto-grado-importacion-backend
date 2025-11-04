# src/schemas/importacion.py
from datetime import date, datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class ImportacionBase(BaseModel):
    codigo: str = Field(..., max_length=50)
    proveedorId: int
    fechaLlegada: date
    estado: str = Field(..., max_length=30)
    observaciones: Optional[str] = Field(None, max_length=200)

class ImportacionCreate(ImportacionBase):
    empleadoId: int

class ImportacionUpdate(BaseModel):
    proveedorId: Optional[int] = None
    fechaLlegada: Optional[date] = None
    estado: Optional[str] = Field(None, max_length=30)
    observaciones: Optional[str] = Field(None, max_length=200)

    model_config = ConfigDict(from_attributes=True)



class ImportOut(BaseModel):
    id: int
    codigo: str | None = None

    class Config:
        from_attributes = True

#
class ImportacionOut(ImportacionBase):
    id: int
    empleadoId: int
    fechaRegistro: datetime
    fechaActualizacion: Optional[datetime] = None
    activo: int

    model_config = ConfigDict(from_attributes=True)