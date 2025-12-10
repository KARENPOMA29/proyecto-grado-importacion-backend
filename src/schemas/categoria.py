from pydantic import BaseModel
from typing import Optional
class CategoriaOut(BaseModel):
    id: int
    nombre: str | None = None

    class Config:
        from_attributes = True

# Base
class CategoriaBase(BaseModel):
    nombre: str

# Crear
class CategoriaCreate(CategoriaBase):
    pass

# Actualizar
class CategoriaUpdate(BaseModel):
    nombre: Optional[str]

# Respuesta
class CategoriaResponse(CategoriaBase):
    id: int
    estado: int

    class Config:
        from_attributes = True
