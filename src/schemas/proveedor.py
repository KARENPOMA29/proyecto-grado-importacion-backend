from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Base
class ProveedorBase(BaseModel):
    razonSocial: str
    telefono: str
    encargado: str
    direccion: str
    ci: str

# Crear
class ProveedorCreate(ProveedorBase):
    pass

# Actualizar
class ProveedorUpdate(BaseModel):
    razonSocial: Optional[str]
    telefono: Optional[str]
    encargado: Optional[str]
    direccion: Optional[str]
    ci: Optional[str]

# Respuesta
class ProveedorResponse(ProveedorBase):
    id: int
    fechaRegistro: datetime
    estado: int

    class Config:
        from_attributes = True
