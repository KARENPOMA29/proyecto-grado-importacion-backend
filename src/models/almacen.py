# src/models/almacen.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from src.config.db import Base

class Almacen(Base):
    __tablename__ = "Almacen"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)
    direccion = Column(String(200), nullable=False)  # 👈 OBLIGATORIA
    sucursalId = Column(Integer, ForeignKey("Sucursal.id"), nullable=False)
    fechaRegistro = Column(DateTime, default=datetime.utcnow)
    estado = Column(Integer, default=1)  # 1 = activo, 0 = eliminado

    sucursal = relationship("Sucursal", back_populates="almacenes")

    @property
    def sucursalNombre(self):
        """Nombre de la sucursal asociada (para el schema de salida)."""
        return self.sucursal.nombre if self.sucursal else None
    
   