# src/schemas/sucursal.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SucursalBase(BaseModel):
    nombre: str
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    idCiudad: Optional[int] = None

class SucursalCreate(SucursalBase):
    pass

class SucursalUpdate(BaseModel):
    nombre: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    idCiudad: Optional[int] = None

class SucursalResponse(SucursalBase):
    id: int
    fechaRegistro: datetime
    estado: int

    ciudadNombre: Optional[str] = None   # 🔥 Front recibe esto

    class Config:
        from_attributes = True
