from sqlalchemy import (
    Column,
    Integer,
    SmallInteger,
    String,
    DateTime,
    ForeignKey,
    text,
)
from sqlalchemy.orm import relationship
from src.config.db import Base


class ModeloProducto(Base):
    __tablename__ = "ModeloProducto"

    id = Column(Integer, primary_key=True, index=True)

    nombreModelo = Column(String(50), nullable=False)

    capacidadOTamano = Column(Integer, nullable=False)

    unidadMedida = Column(String(50), nullable=False)

    stockMinimo = Column(Integer, nullable=False)

    stockActual = Column(
        Integer,
        nullable=False,
        default=0,
        server_default=text("0")
    )

    color = Column(String(50), nullable=False)

    duracionGarantia = Column(
        SmallInteger,
        nullable=False
    )

    tipoGarantia = Column(String(5), nullable=False)

    fechaRegistro = Column(
        DateTime,
        server_default=text("GETDATE()"),
        nullable=False
    )

    estado = Column(
        SmallInteger,
        default=1,
        nullable=False
    )

    urlImagen = Column(String, nullable=True)

    idMarca = Column(
        Integer,
        ForeignKey("Marca.id"),
        nullable=True
    )

    marca = relationship(
        "Marca",
        back_populates="modelos"
    )