from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class EmpleadoBase(BaseModel):
    nombre: str
    apellido: str
    segundoApellido: Optional[str]
    ci: str
    telefono: str
    rol: str
    usuario: str
    correo: Optional[EmailStr]
    urlImagen: Optional[str]

class EmpleadoCreate(EmpleadoBase):
    contrasena: str

class EmpleadoUpdate(BaseModel):
    nombre: Optional[str]
    apellido: Optional[str]
    segundoApellido: Optional[str]
    ci: Optional[str]
    telefono: Optional[str]
    rol: Optional[str]
    usuario: Optional[str]
    correo: Optional[EmailStr]
    urlImagen: Optional[str]

class EmpleadoResponse(EmpleadoBase):
    id: int
    fechaRegistro: datetime
    estado: int
    urlImagen: Optional[str]

    class Config:
        from_attributes = True
