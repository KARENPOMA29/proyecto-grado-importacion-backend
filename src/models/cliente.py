from sqlalchemy import Column, Integer, String, DateTime, func
from datetime import datetime
from src.config.db import Base

class Cliente(Base):
    __tablename__ = "Cliente"

    id = Column(Integer, primary_key=True, index=True)
    razonSocial = Column(String(250), nullable=False)
    nit = Column(String(20), nullable=False)
    correo = Column(String(60), nullable=False)
    telefono = Column(String(10), nullable=False)
    fechaRegistro = Column(DateTime, nullable=False, server_default=func.getdate())
    estado = Column(Integer, nullable=False, server_default="1")