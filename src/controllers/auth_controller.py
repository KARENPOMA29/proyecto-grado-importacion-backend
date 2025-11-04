# src/controllers/auth_controller.py
from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.models.empleado import Empleado
from src.schemas.auth import LoginRequest
from src.utils.security import md5_hash
from src.utils.mailer import enviar_credenciales


def login_empleado(db: Session, credentials: LoginRequest):
    # Buscar el empleado por usuario
    empleado = db.query(Empleado).filter(
        Empleado.usuario == credentials.usuario,
        Empleado.estado == 1
    ).first()

    if not empleado:
        raise HTTPException(status_code=401, detail=" Usuario o contraseña incorrectos")

    # hashear lo que llega del frontend
    pwd_hash = md5_hash(credentials.contrasena)

    if empleado.contrasena != pwd_hash:
        raise HTTPException(status_code=401, detail=" Usuario o contraseña incorrectos")

    # devolver datos limpios
    return {
        "id": empleado.id,
        "nombre": empleado.nombre,
        "apellido": empleado.apellido,
        "rol": empleado.rol,
        "correo": empleado.correo,
        "usuario": empleado.usuario,
    }


def recuperar_contrasena_empleado(db: Session, correo: str, ci: str):
    """
    Busca empleado por correo + ci.
    Si existe:
      - genera nueva pass con regla: <ci><inicialNombre><apellido>
      - guarda en MD5
      - envía por correo usuario + pass
    """
    empleado = db.query(Empleado).filter(
        Empleado.correo == correo,
        Empleado.ci == ci,
        Empleado.estado == 1
    ).first()

    if not empleado:
        raise HTTPException(status_code=404, detail="No se encontró un empleado con esos datos")

    nombre = (empleado.nombre or "").strip()
    apellido = (empleado.apellido or "").strip()

    inicial_nombre = nombre[0].lower() if nombre else ""
    nueva_pass_plana = f"{empleado.ci}{inicial_nombre}{apellido.lower()}"

    # guardar en BD en MD5
    empleado.contrasena = md5_hash(nueva_pass_plana)
    db.commit()
    db.refresh(empleado)

    # enviar correo con usuario + pass
    try:
        enviar_credenciales(empleado.correo, empleado.usuario, nueva_pass_plana)
    except Exception as e:
        # no rompemos la respuesta por el correo
        print("Error enviando correo de recuperación:", e)

    return {"message": "Se envió su usuario y contraseña al correo registrado."}
