# src/models/importacion.py
from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, SmallInteger
from sqlalchemy.orm import relationship
from datetime import datetime
from src.config.db import Base 

class Importacion(Base):
    __tablename__ = "Importacion"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), nullable=False)
    proveedorId = Column(Integer, ForeignKey("Proveedor.id"), nullable=False)
    fechaRegistro = Column(DateTime, nullable=False, default=datetime.utcnow)
    estado = Column(SmallInteger, nullable=False, server_default="1")
    descripcion = Column(String(200), nullable=True)
    empleadoId = Column(Integer, nullable=False)
    fechaLlegada = Column(Date, nullable=False)
    idEmpleadoAsignado = Column(Integer, ForeignKey("Empleado.id"), nullable=False)

    proveedor = relationship("Proveedor", back_populates="importaciones")
    empleadoAsignado = relationship(
        "Empleado",
        foreign_keys=[idEmpleadoAsignado],
        back_populates="importaciones_asignadas",
    )