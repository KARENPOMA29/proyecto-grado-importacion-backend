from typing import Optional
from pydantic import BaseModel


class MarcaBase(BaseModel):
    nombre: str


class MarcaCreate(MarcaBase):
    pass


class MarcaUpdate(BaseModel):
    nombre: Optional[str] = None


class MarcaResponse(MarcaBase):
    id: int

    class Config:
        one_mode = True


# Para combos si quieres algo corto
class MarcaOut(BaseModel):
    id: int
    nombre: str

    class Config:
        from_attributes = True
