from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ModeloProductoOut(BaseModel):
    id: int
    nombreModelo: str | None = None

    class Config:
        orm_mode = True

# Base
class ModeloProductoBase(BaseModel):
    nombreModelo: str
    marca: str
    capacidadOTamano: Optional[int]
    unidadMedida: Optional[str]
    stockMinimo: int
    stockActual: int

# Crear
class ModeloProductoCreate(ModeloProductoBase):
    pass

# Actualizar
class ModeloProductoUpdate(BaseModel):
    nombreModelo: Optional[str]
    marca: Optional[str]
    capacidadOTamano: Optional[int]
    unidadMedida: Optional[str]
    stockMinimo: Optional[int]
    stockActual: Optional[int]

# Respuesta
class ModeloProductoResponse(ModeloProductoBase):
    id: int
    fechaRegistro: datetime
    estado: int

    class Config:
        from_attributes = True
