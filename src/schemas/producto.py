# src/schemas/producto.py
from pydantic import BaseModel, Field, condecimal
from typing import Optional
from datetime import datetime

class ProductoBase(BaseModel):
    numeroSerie: str = Field(..., max_length=50)
    descripcion: str
    precio: condecimal(max_digits=8, decimal_places=2)
    color: str = Field(..., max_length=50)
    duracionGarantia: int = Field(..., ge=0, le=255)
    tipoGarantia: str = Field(..., max_length=5)
    categoriaId: int
    modeloId: int
    importacionId: Optional[int] = None

class ProductoCreate(ProductoBase):
    # POST requiere todo lo anterior
    pass

class ProductoUpdate(BaseModel):
    numeroSerie: Optional[str] = Field(None, max_length=50)
    descripcion: Optional[str] = None
    precio: Optional[condecimal(max_digits=8, decimal_places=2)] = None
    color: Optional[str] = Field(None, max_length=50)
    duracionGarantia: Optional[int] = Field(None, ge=0, le=255)
    tipoGarantia: Optional[str] = Field(None, max_length=5)
    categoriaId: Optional[int] = None
    modeloId: Optional[int] = None
    importacionId: Optional[int] = None
    # estado lo dejamos editable por si quieres reactivar
    estado: Optional[int] = None

class ProductoOut(ProductoBase):
    id: int
    fechaRegistro: datetime
    estado: int

    class Config:
        orm_mode = True
