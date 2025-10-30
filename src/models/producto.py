# src/models/producto.py
from sqlalchemy import Column, Integer, String, DateTime, Numeric, SmallInteger, ForeignKey, Text
from sqlalchemy.sql import func
from src.config.db import Base

class Producto(Base):
    __tablename__ = "Producto"

    id = Column(Integer, primary_key=True, index=True)
    numeroSerie = Column(String(50), nullable=False)
    descripcion = Column(Text, nullable=False)
    precio = Column(Numeric(8, 2), nullable=False)
    color = Column(String(50), nullable=False)
    duracionGarantia = Column(SmallInteger, nullable=False)  # tinyint
    tipoGarantia = Column(String(5), nullable=False)
    categoriaId = Column(Integer, ForeignKey("Categoria.id"), nullable=False)
    modeloId = Column(Integer, ForeignKey("ModeloProducto.id"), nullable=False)
    importacionId = Column(Integer, ForeignKey("Importacion.id"), nullable=True)

    fechaRegistro = Column(DateTime, nullable=False, server_default=func.getdate())
    estado = Column(SmallInteger, nullable=False, server_default="1")
