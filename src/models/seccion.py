from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    text,
)

from src.config.db import Base
from sqlalchemy.orm import relationship

class Seccion(Base):
    __tablename__ = "Seccion"

    id = Column(Integer, primary_key=True, index=True)

    nombre = Column(String(150), nullable=True)

    almacenId = Column(
        Integer,
        ForeignKey("Almacen.id"),
        nullable=False
    )

    modeloId = Column(
        Integer,
        ForeignKey("ModeloProducto.id"),
        nullable=False
    )

    descripcion = Column(
        String(50),
        nullable=False
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

    almacen = relationship("Almacen", back_populates="secciones")