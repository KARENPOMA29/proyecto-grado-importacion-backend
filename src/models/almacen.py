from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from src.config.db import Base

class Almacen(Base):
    __tablename__ = "Almacen"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)
    sucursalId = Column(Integer, ForeignKey("Sucursal.id"), nullable=True)
    fechaRegistro = Column(DateTime, default=datetime.utcnow)
    estado = Column(Integer, default=1)  # 1 = activo, 0 = eliminado
