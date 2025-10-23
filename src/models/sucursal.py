from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from src.config.db import Base

class Sucursal(Base):
    __tablename__ = "Sucursal"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    telefono = Column(String(20), nullable=True)
    fechaRegistro = Column(DateTime, default=datetime.utcnow)
    estado = Column(Integer, default=1)  # 1 = activa, 0 = eliminada
