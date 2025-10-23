from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.models.empleado import Empleado
from src.schemas.empleado import EmpleadoCreate, EmpleadoUpdate

def crear_empleado(db: Session, empleado: EmpleadoCreate):
    # 🔎 Validar si ya existe un empleado con mismo correo y nombre
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

    # ✅ Si no existe, crear el nuevo empleado
    nuevo_empleado = Empleado(**empleado.dict())
    db.add(nuevo_empleado)
    db.commit()
    db.refresh(nuevo_empleado)
    return nuevo_empleado

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

    # 🔎 Validar que no haya otro con el mismo nombre y correo
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

    # ✅ Actualizar solo los campos enviados
    for key, value in datos.dict(exclude_unset=True).items():
        setattr(empleado, key, value)

    db.commit()
    db.refresh(empleado)
    return empleado