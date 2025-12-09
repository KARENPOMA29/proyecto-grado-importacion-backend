from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from pydantic import constr

class MovimientoImportacionBase(BaseModel):
    importacionId: int
    tipoMovimiento: constr(max_length=10)
    descripcion: Optional[str] = None
    rutaArchivo: Optional[str] = None
    idEmpleadoEncargado: int


class MovimientoImportacionCreate(MovimientoImportacionBase):
    pass


class MovimientoImportacionUpdate(BaseModel):
    importacionId: Optional[int] = None
    tipoMovimiento: Optional[constr(max_length=10)] = None
    descripcion: Optional[str] = None
    rutaArchivo: Optional[str] = None
    idEmpleadoEncargado: Optional[int] = None


class MovimientoImportacionResponse(MovimientoImportacionBase):
    id: int
    fechaRegistro: datetime

    class Config:
        orm_mode = True


class PasoMovimientoOut(BaseModel):
    code: str
    label: str
    completado: bool
    movimiento: Optional[MovimientoImportacionResponse] = None  # reutilizamos el response

    class Config:
        orm_mode = True


class MovimientoImportacionOut(BaseModel):
    id: int
    importacionId: int
    tipoMovimiento: str
    descripcion: Optional[str] = None
    rutaArchivo: Optional[str] = None
    idEmpleadoEncargado: int
    fechaRegistro: datetime

    class Config:
        orm_mode = True

# src/schemas/movimiento_importacion.py
class MovimientoImportacionOut(BaseModel):
    id: int
    importacionId: int
    tipoMovimiento: str
    descripcion: Optional[str] = None
    rutaArchivo: Optional[str] = None
    idEmpleadoEncargado: int
    fechaRegistro: datetime

    # 👇 NUEVO
    empleadoNombre: Optional[str] = None

    class Config:
        orm_mode = True


class MovimientoEstadoOut(BaseModel):
    code: str
    label: str
    completado: bool
    movimiento: Optional[MovimientoImportacionOut] = None