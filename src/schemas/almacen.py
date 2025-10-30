from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AlmacenOut(BaseModel):
    id: int
    nombre: str | None = None

    class Config:
        orm_mode = True

# Base
class AlmacenBase(BaseModel):
    nombre: str
    sucursalId: Optional[int] = None

# Crear
class AlmacenCreate(AlmacenBase):
    pass

# Actualizar
class AlmacenUpdate(BaseModel):
    nombre: Optional[str]
    sucursalId: Optional[int]

# Respuesta
class AlmacenResponse(AlmacenBase):
    id: int
    fechaRegistro: datetime
    estado: int

    class Config:
        from_attributes = True
