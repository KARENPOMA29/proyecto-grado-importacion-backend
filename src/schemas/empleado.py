from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class EmpleadoBase(BaseModel):
    nombre: str
    apellido: str
    segundoApellido: Optional[str] = None
    ci: str
    telefono: str
    rol: str
    usuario: str
    correo: Optional[EmailStr] = None
    urlImagen: Optional[str] = None
    # 👇 IMPORTANTE: la sucursal en el schema
    idSucursal: Optional[int] = None


class EmpleadoCreate(EmpleadoBase):
    # 👇 la contraseña ES requerida al crear
    contrasena: str


class EmpleadoUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    segundoApellido: Optional[str] = None
    ci: Optional[str] = None
    telefono: Optional[str] = None
    rol: Optional[str] = None
    usuario: Optional[str] = None
    correo: Optional[EmailStr] = None
    urlImagen: Optional[str] = None
    idSucursal: Optional[int] = None
    contrasena: Optional[str] = None
    
class ImagenEmpleadoResponse(BaseModel):
    urlImagen: str

class EmpleadoResponse(EmpleadoBase):
    id: int
    fechaRegistro: datetime
    estado: int

    class Config:
        orm_mode = True  # FastAPI puede convertir desde SQLAlchemy
