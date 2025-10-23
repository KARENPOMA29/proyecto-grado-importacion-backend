from sqlalchemy import Column, Integer, String
from src.config.db import Base

class Categoria(Base):
    __tablename__ = "Categoria"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False, unique=True)
    estado = Column(Integer, default=1)  # 1 = activo, 0 = eliminado
