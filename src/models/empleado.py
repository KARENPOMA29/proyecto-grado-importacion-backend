from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from src.config.db import Base

class Empleado(Base):
    __tablename__ = "Empleado"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)
    apellido = Column(String(50), nullable=False)
    segundoApellido = Column(String(50))
    ci = Column(String(20), nullable=False)
    telefono = Column(String(10), nullable=False)
    rol = Column(String(15), nullable=False)
    usuario = Column(String(50), nullable=False)
    contrasena = Column(Text, nullable=False)
    fechaRegistro = Column(DateTime, default=datetime.utcnow)
    urlImagen = Column(String(500))
    estado = Column(Integer, default=1)
    correo = Column(String(100))
