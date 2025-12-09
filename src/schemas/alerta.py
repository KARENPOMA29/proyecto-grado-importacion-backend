# src/schemas/alerta.py
from datetime import datetime
from pydantic import BaseModel


class AlertaBase(BaseModel):
    tipo: str
    mensaje: str
    empleadoId: int | None = None


class AlertaCreate(AlertaBase):
    # por si quieres pasar 0 o 1 explícitamente;
    # si no mandas nada, será 1 (activa)
    estado: int = 1


class AlertaOut(AlertaBase):
    id: int
    fecha: datetime
    estado: int

    class Config:
        orm_mode = True
