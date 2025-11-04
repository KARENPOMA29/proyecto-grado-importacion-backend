from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.models.empleado import Empleado
from src.schemas.empleado import EmpleadoCreate, EmpleadoUpdate
from src.utils.security import md5_hash
from src.utils.mailer import enviar_credenciales

def crear_empleado(db: Session, empleado: EmpleadoCreate):
    # validación de duplicados
    existente = db.query(Empleado).filter(
        Empleado.nombre == empleado.nombre,
        Empleado.correo == empleado.correo,
        Empleado.ci == empleado.ci,
        Empleado.estado == 1
    ).first()

    if existente:
        raise HTTPException(
            status_code=400,
            detail="⚠️ Ya existe un empleado registrado con el mismo nombre, ci y correo."
        )

    # acá guardamos la contraseña encriptada
    password_plano = empleado.contrasena  # lo que vino del front
    empleado_dict = empleado.dict()

    if password_plano:
        empleado_dict["contrasena"] = md5_hash(password_plano)
    else:
        empleado_dict["contrasena"] = None

    nuevo = Empleado(**empleado_dict)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    # si hay correo, le mandamos
    if nuevo.correo and password_plano:
        try:
            enviar_credenciales(nuevo.correo, nuevo.usuario, password_plano)
        except Exception as e:
            # no rompemos la creación solo por el correo
            print("Error enviando correo:", e)

    return nuevo

def listar_empleados(db: Session):
    return db.query(Empleado).filter(Empleado.estado == 1).all()


def obtener_empleado_por_id(db: Session, empleado_id: int):
    return db.query(Empleado).filter(Empleado.id == empleado_id, Empleado.estado == 1).first()

def eliminar_empleado(db: Session, empleado_id: int):
    empleado = db.query(Empleado).filter(Empleado.id == empleado_id).first()
    if empleado:
        empleado.estado = 0  # 🔁 Marcamos como eliminado
        db.commit()
        db.refresh(empleado)
        return True
    return False

def actualizar_empleado(db: Session, empleado_id: int, datos: EmpleadoUpdate):
    empleado = db.query(Empleado).filter(Empleado.id == empleado_id, Empleado.estado == 1).first()

    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    # validar duplicado
    if datos.nombre and datos.correo:
        duplicado = db.query(Empleado).filter(
            Empleado.nombre == datos.nombre,
            Empleado.correo == datos.correo,
            Empleado.id != empleado_id,
            Empleado.estado == 1
        ).first()
        if duplicado:
            raise HTTPException(
                status_code=400,
                detail="⚠️ Otro empleado con el mismo nombre y correo ya existe."
            )

    update_data = datos.dict(exclude_unset=True)

    # si viene contrasena → encriptar
    if "contrasena" in update_data and update_data["contrasena"]:
        update_data["contrasena"] = md5_hash(update_data["contrasena"])

    for key, value in update_data.items():
        setattr(empleado, key, value)

    db.commit()
    db.refresh(empleado)
    return empleado
