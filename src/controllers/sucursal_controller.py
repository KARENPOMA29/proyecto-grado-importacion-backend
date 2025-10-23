from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.models.sucursal import Sucursal
from src.schemas.sucursal import SucursalCreate, SucursalUpdate

# Crear sucursal
def crear_sucursal(db: Session, sucursal: SucursalCreate):
    existente = db.query(Sucursal).filter(
        Sucursal.nombre == sucursal.nombre,
        Sucursal.estado == 1
    ).first()

    if existente:
        raise HTTPException(status_code=400, detail="Ya existe una sucursal activa con ese nombre.")

    nueva = Sucursal(**sucursal.dict())
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

# Listar activas
def listar_sucursales(db: Session):
    return db.query(Sucursal).filter(Sucursal.estado == 1).all()

# Obtener por ID
def obtener_sucursal(db: Session, sucursal_id: int):
    sucursal = db.query(Sucursal).filter(Sucursal.id == sucursal_id, Sucursal.estado == 1).first()
    if not sucursal:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada o inactiva")
    return sucursal

# Actualizar
def actualizar_sucursal(db: Session, sucursal_id: int, datos: SucursalUpdate):
    sucursal = db.query(Sucursal).filter(Sucursal.id == sucursal_id, Sucursal.estado == 1).first()
    if not sucursal:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada o inactiva")

    if datos.nombre:
        duplicado = db.query(Sucursal).filter(
            Sucursal.nombre == datos.nombre,
            Sucursal.id != sucursal_id,
            Sucursal.estado == 1
        ).first()
        if duplicado:
            raise HTTPException(status_code=400, detail="Ya existe otra sucursal activa con ese nombre.")

    for key, value in datos.dict(exclude_unset=True).items():
        setattr(sucursal, key, value)

    db.commit()
    db.refresh(sucursal)
    return sucursal

# Eliminación lógica
def eliminar_sucursal(db: Session, sucursal_id: int):
    sucursal = db.query(Sucursal).filter(Sucursal.id == sucursal_id, Sucursal.estado == 1).first()
    if not sucursal:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada o ya eliminada")

    sucursal.estado = 0
    db.commit()
    return {"mensaje": "Sucursal eliminada correctamente (lógicamente)"}
