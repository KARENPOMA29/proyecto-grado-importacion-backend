from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Numeric,
    text,
)

from sqlalchemy.orm import relationship
from src.config.db import Base


class Producto(Base):
    __tablename__ = "Producto"

    id = Column(Integer, primary_key=True, index=True)

    numeroSerie = Column(String(50), nullable=False)

    descripcion = Column(String, nullable=True)

    observado = Column(
        Integer,
        server_default="1",
        nullable=False
    )

    obsDescripcion = Column(String, nullable=True)

    precioOrigen = Column(
        Numeric(8, 2),
        nullable=False
    )

    precio = Column(
        Numeric(8, 2),
        nullable=False
    )

    categoriaId = Column(
        Integer,
        ForeignKey("Categoria.id"),
        nullable=False
    )

    modeloId = Column(
        Integer,
        ForeignKey("ModeloProducto.id"),
        nullable=False
    )

    importacionId = Column(
        Integer,
        ForeignKey("Importacion.id"),
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

    categoria = relationship("Categoria")

    modelo = relationship("ModeloProducto")

    importacion = relationship("Importacion")