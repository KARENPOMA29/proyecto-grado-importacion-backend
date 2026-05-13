from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    text,
)
from sqlalchemy.orm import relationship
from src.config.db import Base


class MovimientoImportacion(Base):
    __tablename__ = "MovimientoImportacion"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )

    importacionId = Column(
        Integer,
        ForeignKey("Importacion.id"),
        nullable=False
    )

    tipoMovimiento = Column(
        String(10),
        nullable=False
    )

    descripcion = Column(
        String,
        nullable=True
    )

    rutaArchivo = Column(
        String(200),
        nullable=True
    )

    idEmpleadoEncargado = Column(
        Integer,
        ForeignKey("Empleado.id"),
        nullable=False
    )

    fechaRegistro = Column(
        DateTime,
        server_default=text("GETDATE()"),
        nullable=False
    )

    # relaciones
    importacion = relationship("Importacion")

    empleado_encargado = relationship("Empleado")