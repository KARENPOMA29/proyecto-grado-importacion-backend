from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from src.config.db import Base

class ModeloProducto(Base):
    __tablename__ = "ModeloProducto"

    id = Column(Integer, primary_key=True, index=True)
    nombreModelo = Column(String(50), nullable=False)
    marca = Column(String(50), nullable=False)
    capacidadOTamano = Column(Integer, nullable=True)
    unidadMedida = Column(String(50), nullable=True)
    stockMinimo = Column(Integer, nullable=False)
    stockActual = Column(Integer, nullable=False)
    fechaRegistro = Column(DateTime, default=datetime.utcnow)
    estado = Column(Integer, default=1)  # 1 = activo, 0 = eliminado
