# src/models/venta.py
from sqlalchemy import Column, Integer, DateTime, DECIMAL, ForeignKey, String, text
from sqlalchemy.orm import relationship

from src.config.db import Base
class Venta(Base):
    __tablename__ = "Venta"

    id = Column(Integer, primary_key=True, index=True)
    empleadoId = Column(Integer, ForeignKey("Empleado.id"), nullable=False)
    clienteId = Column(Integer, ForeignKey("Cliente.id"), nullable=False)
    total = Column(DECIMAL(8, 2), nullable=False)

    fechaRegistro = Column(
        DateTime,
        server_default=text("GETDATE()"),
        nullable=False
    )

    sucursalId = Column(Integer, ForeignKey("Sucursal.id"), nullable=True)
    codigoVenta = Column(String(50), nullable=True)
    estado = Column(Integer, default=1)

    detalles = relationship(
        "DetalleVenta",
        back_populates="venta",
        cascade="all, delete-orphan"
    )
