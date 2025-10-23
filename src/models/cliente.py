from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from src.config.db import Base

class Cliente(Base):
    __tablename__ = "Cliente"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)
    apellido = Column(String(50), nullable=False)
    segundoApellido = Column(String(50))
    correo = Column(String(60), nullable=False)
    ci = Column(String(50), nullable=False)
    fechaRegistro = Column(DateTime, default=datetime.utcnow)
    estado = Column(Integer, default=1)
