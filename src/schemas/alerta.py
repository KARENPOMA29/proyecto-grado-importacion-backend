# src/schemas/alerta.py
from datetime import datetime
from pydantic import BaseModel


class AlertaBase(BaseModel):
    tipo: str

    # 🔥 NUEVO
    referencia: str | None = None

    mensaje: str
    empleadoId: int | None = None


class AlertaCreate(AlertaBase):
    estado: int = 1


class AlertaOut(AlertaBase):
    id: int
    fecha: datetime
    estado: int

    class Config:
        from_attributes = True