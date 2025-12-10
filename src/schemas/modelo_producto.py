from datetime import datetime
from typing import Optional
from pydantic import BaseModel


# 👉 Esquema de marca para respuesta
class MarcaOut(BaseModel):
    id: int
    nombre: str   # 👈 en minúscula, igual que el modelo SQLAlchemy

    class Config:
        from_attributes = True


# Para combos / selects cortos
class ModeloProductoOut(BaseModel):
    id: int
    nombreModelo: Optional[str] = None

    class Config:
        from_attributes = True


# -------- BASE --------
class ModeloProductoBase(BaseModel):
    nombreModelo: str
    capacidadOTamano: int
    unidadMedida: str
    stockMinimo: int
    stockActual: int = 0
    color: str
    duracionGarantia: int
    tipoGarantia: str
    urlImagen: Optional[str] = None
    idMarca: Optional[int] = None  # FK


# -------- CREATE --------
class ModeloProductoCreate(ModeloProductoBase):
    pass


# -------- UPDATE --------
class ModeloProductoUpdate(BaseModel):
    nombreModelo: Optional[str] = None
    capacidadOTamano: Optional[int] = None
    unidadMedida: Optional[str] = None
    stockMinimo: Optional[int] = None
    stockActual: Optional[int] = None
    color: Optional[str] = None
    duracionGarantia: Optional[int] = None
    tipoGarantia: Optional[str] = None
    urlImagen: Optional[str] = None
    idMarca: Optional[int] = None


# -------- RESPONSE --------
class ModeloProductoResponse(ModeloProductoBase):
    id: int
    fechaRegistro: datetime
    estado: int

    # 👉 aquí incluimos el objeto marca
    marca: Optional[MarcaOut] = None

    class Config:
        from_attributes = True
