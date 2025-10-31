# src/models/detalle_venta.py
from sqlalchemy import Column, Integer, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship

from src.config.db import Base


class DetalleVenta(Base):
    __tablename__ = "DetalleVenta"

    id = Column(Integer, primary_key=True, index=True)
    ventaId = Column(Integer, ForeignKey("Venta.id"), nullable=False)
    productoId = Column(Integer, ForeignKey("Producto.id"), nullable=False)
    subtotal = Column(DECIMAL(8, 2), nullable=False)

    venta = relationship("Venta", back_populates="detalles")
