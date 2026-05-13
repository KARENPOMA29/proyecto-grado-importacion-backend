# src/schemas/almacen.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AlmacenOut(BaseModel):
    id: int
    nombre: Optional[str] = None

    class Config:
        from_attributes = True

# Base
class AlmacenBase(BaseModel):
    nombre: str
    direccion: str               # 👈 OBLIGATORIA
    sucursalId: int              # 👈 OBLIGATORIO

# Crear
class AlmacenCreate(AlmacenBase):
    pass

# Actualizar
class AlmacenUpdate(BaseModel):
    nombre: Optional[str] = None
    direccion: Optional[str] = None
    sucursalId: Optional[int] = None

# Respuesta
class AlmacenResponse(AlmacenBase):
    id: int
    fechaRegistro: datetime
    estado: int
    sucursalNombre: Optional[str] = None  # 👈 viene del @property del modelo
    totalSecciones: int = 0
    
    class Config:
        from_attributes = True
