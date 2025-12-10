from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from src.config.db import Base
from sqlalchemy.orm import relationship

class Proveedor(Base):
    __tablename__ = "Proveedor"

    id = Column(Integer, primary_key=True, index=True)
    razonSocial = Column(String(50), nullable=False)
    telefono = Column(String(20), nullable=False)
    encargado = Column(String(150), nullable=False)
    direccion = Column(String(200), nullable=False)
    ci = Column(String(50), nullable=False)
    fechaRegistro = Column(DateTime, default=datetime.utcnow)
    estado = Column(Integer, default=1)  # 1 = activo, 0 = eliminado

    importaciones = relationship("Importacion", back_populates="proveedor")