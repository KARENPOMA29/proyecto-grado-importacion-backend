from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from src.config.db import Base

class MovimientoInventario(Base):
    __tablename__ = "MovimientoInventario"
    id = Column(Integer, primary_key=True, index=True)
    productoId = Column(Integer, ForeignKey("Producto.id"), nullable=False)
    almacenId  = Column(Integer, ForeignKey("Almacen.id"),  nullable=False)
    tipoMovimiento = Column(String(20), nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow, nullable=False)
    usuarioId = Column(Integer, ForeignKey("Empleado.id"), nullable=True)
    estado = Column(Integer, default=1)
