from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Base
class SucursalBase(BaseModel):
    nombre: str
    telefono: Optional[str] = None

# Crear
class SucursalCreate(SucursalBase):
    pass

# Actualizar
class SucursalUpdate(BaseModel):
    nombre: Optional[str]
    telefono: Optional[str]

# Respuesta
class SucursalResponse(SucursalBase):
    id: int
    fechaRegistro: datetime
    estado: int

    class Config:
        from_attributes = True
