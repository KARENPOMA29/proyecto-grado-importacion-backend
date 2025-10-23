from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# Base
class ClienteBase(BaseModel):
    nombre: str
    apellido: str
    segundoApellido: Optional[str]
    correo: EmailStr
    ci: str

# Crear
class ClienteCreate(ClienteBase):
    pass

# Actualizar
class ClienteUpdate(BaseModel):
    nombre: Optional[str]
    apellido: Optional[str]
    segundoApellido: Optional[str]
    correo: Optional[EmailStr]
    ci: Optional[str]

# Respuesta
class ClienteResponse(ClienteBase):
    id: int
    fechaRegistro: datetime
    estado: int

    class Config:
        from_attributes = True
