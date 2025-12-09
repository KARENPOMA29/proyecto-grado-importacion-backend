# src/schemas/producto.py
from pydantic import BaseModel, Field, condecimal
from typing import Optional
from datetime import datetime


class ProductoBase(BaseModel):
    numeroSerie: str = Field(..., max_length=50)
    descripcion: str

    # Por si quieres manejar observaciones desde el front
    observado: int = Field(1, ge=0, le=255)
    obsDescripcion: Optional[str] = None
    precioOrigen: condecimal(max_digits=8, decimal_places=2)
    precio: condecimal(max_digits=8, decimal_places=2)

    categoriaId: int
    modeloId: int
    importacionId: Optional[int] = None


class ProductoCreate(ProductoBase):
    # POST requiere todo lo anterior
    pass


class ProductoUpdate(BaseModel):
    numeroSerie: Optional[str] = Field(None, max_length=50)
    descripcion: Optional[str] = None

    observado: Optional[int] = Field(None, ge=0, le=255)
    obsDescripcion: Optional[str] = None
    precioOrigen: Optional[condecimal(max_digits=8, decimal_places=2)] = None
    precio: Optional[condecimal(max_digits=8, decimal_places=2)] = None

    categoriaId: Optional[int] = None
    modeloId: Optional[int] = None
    importacionId: Optional[int] = None

    # estado editable por si quieres reactivar o marcar como vendido (2)
    estado: Optional[int] = None


class ProductoOut(ProductoBase):
    id: int
    fechaRegistro: datetime
    estado: int

    class Config:
        orm_mode = True             