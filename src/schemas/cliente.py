from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional

# Base
class ClienteBase(BaseModel):
    razonSocial: str
    nit: str
    correo: EmailStr
    telefono: str

# Crear
class ClienteCreate(ClienteBase):
    pass

# Actualizar
class ClienteUpdate(BaseModel):
    razonSocial: Optional[str] = None
    nit: Optional[str] = None
    correo: Optional[EmailStr] = None
    telefono: Optional[str] = None

# Respuesta
class ClienteResponse(ClienteBase):
    id: int
    fechaRegistro: datetime
    estado: int

    # Pydantic v2
    model_config = ConfigDict(from_attributes=True)
