from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from src.config.db import Base

class Seccion(Base):
    __tablename__ = "Seccion"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=True)
    almacenId = Column(Integer, ForeignKey("Almacen.id"), nullable=False)
    modeloId = Column(Integer, ForeignKey("ModeloProducto.id"), nullable=False)
    descripcion = Column(String(50), nullable=False)
    fechaRegistro = Column(DateTime, default=datetime.utcnow)
    estado = Column(Integer, default=1)
