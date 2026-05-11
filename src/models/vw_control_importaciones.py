# src/models/vw_control_importaciones.py

from sqlalchemy import Column, Integer, String, Date, DateTime
from src.config.db import Base

class VwControlImportaciones(Base):
    __tablename__ = "vw_control_importaciones"

    id = Column(Integer, primary_key=True)

    codigo = Column(String)

    proveedorNombre = Column(String)
    proveedorEncargado = Column(String)

    empleadoAsignadoNombre = Column(String)

    fechaRegistro = Column(DateTime)
    fechaLlegada = Column(Date)

    estado = Column(Integer)

    descripcion = Column(String)

    diasParaLlegada = Column(Integer)

    situacion = Column(String)