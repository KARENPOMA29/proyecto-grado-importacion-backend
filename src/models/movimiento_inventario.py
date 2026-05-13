from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    text,
)

from src.config.db import Base


class MovimientoInventario(Base):
    __tablename__ = "MovimientoInventario"

    id = Column(Integer, primary_key=True, index=True)

    productoId = Column(
        Integer,
        ForeignKey("Producto.id"),
        nullable=False
    )

    almacenId = Column(
        Integer,
        ForeignKey("Almacen.id"),
        nullable=False
    )

    tipoMovimiento = Column(
        String(20),
        nullable=False
    )

    fecha = Column(
        DateTime,
        server_default=text("GETDATE()"),
        nullable=False
    )

    usuarioId = Column(
        Integer,
        ForeignKey("Empleado.id"),
        nullable=True
    )

    estado = Column(
        Integer,
        server_default="1",
        nullable=False
    )
    