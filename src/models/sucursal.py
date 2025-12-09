# src/models/sucursal.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from src.config.db import Base
from src.models.ciudad import Ciudad

class Sucursal(Base):
    __tablename__ = "Sucursal"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    telefono = Column(String(20), nullable=True)
    direccion = Column(String(200), nullable=True)

    idCiudad = Column(Integer, ForeignKey("Ciudad.id"), nullable=True)

    fechaRegistro = Column(DateTime, default=datetime.utcnow)
    estado = Column(Integer, default=1)

    # 🔥 RELACIÓN
    ciudad = relationship("Ciudad", lazy="joined")

    # 🔥 PROPIEDAD LISTA PARA EL FRONT
    @property
    def ciudadNombre(self):
        return self.ciudad.nombre if self.ciudad else None
    

    
    ciudad = relationship("Ciudad", back_populates="sucursales")
    almacenes = relationship("Almacen", back_populates="sucursal")