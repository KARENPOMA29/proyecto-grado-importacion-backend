from pydantic import BaseModel
from datetime import datetime
from typing import Optional

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
