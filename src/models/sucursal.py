# src/models/sucursal.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, text
from sqlalchemy.orm import relationship

from src.config.db import Base


class Sucursal(Base):
    __tablename__ = "Sucursal"

    id = Column(Integer, primary_key=True, index=True)

    nombre = Column(String(100), nullable=False)
    telefono = Column(String(20), nullable=True)
    direccion = Column(String(200), nullable=True)

    idCiudad = Column(
        Integer,
        ForeignKey("Ciudad.id"),
        nullable=True
    )

    fechaRegistro = Column(
        DateTime,
        server_default=text("GETDATE()"),
        nullable=False
    )

    estado = Column(
        Integer,
        server_default="1",
        nullable=False
    )

    ciudad = relationship(
        "Ciudad",
        back_populates="sucursales",
        lazy="joined"
    )

    almacenes = relationship(
        "Almacen",
        back_populates="sucursal"
    )

    @property
    def ciudadNombre(self):
        return self.ciudad.nombre if self.ciudad else None
    
    # src/models/sucursal.py
    @property
    def totalAlmacenes(self):
        return len([a for a in self.almacenes if a.estado == 1])