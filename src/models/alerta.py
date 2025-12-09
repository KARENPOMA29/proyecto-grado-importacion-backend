# src/models/alerta.py
from sqlalchemy import Column, Integer, String, DateTime, SmallInteger
from datetime import datetime

from src.config.db import Base


class Alerta(Base):
    __tablename__ = "Alerta"

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(50), nullable=False)
    mensaje = Column(String(200), nullable=False)
    empleadoId = Column(Integer, nullable=True)  # puede ser null
    fecha = Column(DateTime, nullable=False, default=datetime.utcnow)

    # 1 = activa / no leída, 0 = leída
    estado = Column(SmallInteger, nullable=False, default=1)
    # si prefieres que lo maneje SQL Server:
    # estado = Column(SmallInteger, nullable=False, server_default="1")
