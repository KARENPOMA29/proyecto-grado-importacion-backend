from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric
from datetime import datetime
from sqlalchemy.orm import relationship
from src.config.db import Base

class Producto(Base):
    __tablename__ = "Producto"

    id = Column(Integer, primary_key=True, index=True)
    numeroSerie = Column(String(50), nullable=False)
    descripcion = Column(String, nullable=True)
    observado = Column(Integer, default=1)
    obsDescripcion = Column(String, nullable=True)
    precioOrigen = Column(Numeric(8, 2), nullable=False)
    precio = Column(Numeric(8, 2), nullable=False)

    categoriaId = Column(Integer, ForeignKey("Categoria.id"), nullable=False)
    modeloId = Column(Integer, ForeignKey("ModeloProducto.id"), nullable=False)
    importacionId = Column(Integer, ForeignKey("Importacion.id"), nullable=True)

    fechaRegistro = Column(DateTime, default=datetime.utcnow)
    estado = Column(Integer, default=1)

    categoria = relationship("Categoria")
    modelo = relationship("ModeloProducto")
    importacion = relationship("Importacion")