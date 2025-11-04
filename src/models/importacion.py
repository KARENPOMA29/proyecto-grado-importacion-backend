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
    estado = Column(String(30), nullable=False)              # "En tránsito" / "En aduana" / "Entregado"
    fechaActualizacion = Column(DateTime, nullable=True)
    observaciones = Column(String(200), nullable=True)
    empleadoId = Column(Integer, ForeignKey("Empleado.id"), nullable=False)
    fechaLlegada = Column(Date, nullable=False)
    activo = Column(SmallInteger, nullable=False, default=1)  # tinyint en SQL Server
