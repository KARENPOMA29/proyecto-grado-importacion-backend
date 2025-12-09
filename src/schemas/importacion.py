# src/schemas/importacion.py
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ImportacionBase(BaseModel):
    codigo: str = Field(..., max_length=50)
    proveedorId: int
    fechaLlegada: date
    # En el modelo es SmallInteger -> aquí lo manejamos como int
    estado: int = Field(..., description="Estado de la importación (SmallInteger)")
    descripcion: Optional[str] = Field(None, max_length=200)


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

    model_config = ConfigDict(orm_mode=True)


# Útil para combos / selects simples (id, codigo)
class ImportOut(BaseModel):
    id: int
    codigo: str | None = None

    model_config = ConfigDict(orm_mode=True)


class ImportacionOut(ImportacionBase):
    id: int
    empleadoId: int
    idEmpleadoAsignado: int
    fechaRegistro: datetime

    model_config = ConfigDict(orm_mode=True)
