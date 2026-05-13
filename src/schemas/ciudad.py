# src/schemas/ciudad.py
from pydantic import BaseModel
from typing import Optional

class CiudadBase(BaseModel):
    nombre: str

class CiudadCreate(CiudadBase):
    pass

class CiudadUpdate(BaseModel):
    nombre: Optional[str] = None

class CiudadResponse(CiudadBase):
    id: int
    totalSucursales: int = 0
    class Config:
        from_attributes = True
