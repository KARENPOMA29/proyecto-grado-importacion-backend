from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from src.config.db import Base


class Ciudad(Base):
    __tablename__ = "Ciudad"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)

    # sucursales asociadas
    sucursales = relationship("Sucursal", back_populates="ciudad")
    @property
    def totalSucursales(self):
        return len([s for s in self.sucursales if s.estado == 1])