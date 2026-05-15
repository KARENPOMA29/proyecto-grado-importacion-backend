# src/models/alerta.py

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    SmallInteger,
    text,
)

from src.config.db import Base


class Alerta(Base):
    __tablename__ = "Alerta"

    id = Column(Integer, primary_key=True, index=True)

    tipo = Column(String(50), nullable=False)

    # 🔥 NUEVO
    referencia = Column(String(200), nullable=True)

    mensaje = Column(String(200), nullable=False)

    empleadoId = Column(Integer, nullable=True)

    fecha = Column(
        DateTime,
        server_default=text("GETDATE()"),
        nullable=False
    )

    estado = Column(
        SmallInteger,
        nullable=False,
        server_default="1"
    )