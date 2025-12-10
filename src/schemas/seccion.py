# src/schemas/seccion.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SeccionBase(BaseModel):
    nombre: Optional[str] = None
    almacenId: int
    modeloId: int
    descripcion: str

class SeccionCreate(SeccionBase):
    pass

class SeccionUpdate(BaseModel):
    nombre: Optional[str] = None
    almacenId: Optional[int] = None
    modeloId: Optional[int] = None
    descripcion: Optional[str] = None

class SeccionResponse(SeccionBase):
    id: int
    fechaRegistro: datetime
    estado: int
    # solo salida
    almacenNombre: Optional[str] = None
    modeloNombre: Optional[str] = None

    class Config:
        from_attributes = True
