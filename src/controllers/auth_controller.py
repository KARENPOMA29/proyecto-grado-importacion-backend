from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.models.empleado import Empleado
from src.schemas.auth import LoginRequest

def login_empleado(db: Session, credentials: LoginRequest):
    # Buscar el empleado por usuario
    empleado = db.query(Empleado).filter(
        Empleado.usuario == credentials.usuario,
        Empleado.estado == 1
    ).first()

    if not empleado:
        raise HTTPException(
            status_code=401,
            detail=" Usuario o contraseña incorrectos"
        )
    
    # Verificar la contraseña
    if empleado.contrasena != credentials.contrasena:  # Nota: En producción, usar hash para contraseñas
        raise HTTPException(
            status_code=401,
            detail=" Usuario o contraseña incorrectos"
        )
    
    # Retornar información del empleado (excluir datos sensibles)
    return {
        "id": empleado.id,
        "nombre": empleado.nombre,
        "apellido": empleado.apellido,
        "rol": empleado.rol,
        "correo": empleado.correo,
        "usuario": empleado.usuario
    }