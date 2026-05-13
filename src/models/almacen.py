# src/models/almacen.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, text
from sqlalchemy.orm import relationship
from src.config.db import Base


class Almacen(Base):
    __tablename__ = "Almacen"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)
    direccion = Column(String(200), nullable=False)
    sucursalId = Column(Integer, ForeignKey("Sucursal.id"), nullable=False)

    fechaRegistro = Column(
        DateTime,
        server_default=text("GETDATE()"),
        nullable=False
    )

    estado = Column(Integer, default=1)

    sucursal = relationship("Sucursal", back_populates="almacenes")

    @property
    def sucursalNombre(self):
        return self.sucursal.nombre if self.sucursal else None