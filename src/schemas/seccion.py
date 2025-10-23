from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SeccionBase(BaseModel):
    almacenId: int
    modeloId: int
    descripcion: str

class SeccionCreate(SeccionBase):
    pass

class SeccionUpdate(BaseModel):
    almacenId: Optional[int]
    modeloId: Optional[int]
    descripcion: Optional[str]

class SeccionResponse(SeccionBase):
    id: int
    fechaRegistro: datetime
    estado: int

    class Config:
        from_attributes = True
