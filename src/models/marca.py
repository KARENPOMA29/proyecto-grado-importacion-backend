from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from src.config.db import Base


class Marca(Base):
    __tablename__ = "Marca"

    id = Column(Integer, primary_key=True, index=True)
    # En la BDD el campo es 'Nombre', aquí usamos 'nombre' como atributo Python
    nombre = Column(String(150), nullable=False)

    # Relación inversa
    modelos = relationship("ModeloProducto", back_populates="marca")
