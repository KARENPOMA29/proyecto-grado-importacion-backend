from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.models.almacen import Almacen
from src.models.sucursal import Sucursal
from src.schemas.almacen import AlmacenCreate, AlmacenUpdate
from src.models.seccion import Seccion 
# Crear almacén
def crear_almacen(db: Session, almacen: AlmacenCreate):
    # Validar sucursal activa (si se envía)
    if almacen.sucursalId is not None:
        sucursal = db.query(Sucursal).filter(Sucursal.id == almacen.sucursalId, Sucursal.estado == 1).first()
        if not sucursal:
            raise HTTPException(status_code=400, detail="La sucursal seleccionada no existe o está inactiva.")

    # Validar nombre duplicado activo
    existente = db.query(Almacen).filter(
        Almacen.nombre == almacen.nombre,
        Almacen.estado == 1
    ).first()
    if existente:
        raise HTTPException(status_code=400, detail="Ya existe un almacén activo con ese nombre.")

    nuevo = Almacen(**almacen.dict())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


# Listar almacenes activos
def listar_almacenes(db: Session):
    return db.query(Almacen).filter(Almacen.estado == 1).all()


# Obtener almacén por ID
def obtener_almacen(db: Session, almacen_id: int):
    almacen = db.query(Almacen).filter(Almacen.id == almacen_id, Almacen.estado == 1).first()
    if not almacen:
        raise HTTPException(status_code=404, detail="Almacén no encontrado o inactivo")
    return almacen


# Actualizar almacén
def actualizar_almacen(db: Session, almacen_id: int, datos: AlmacenUpdate):
    almacen = db.query(Almacen).filter(Almacen.id == almacen_id, Almacen.estado == 1).first()
    if not almacen:
        raise HTTPException(status_code=404, detail="Almacén no encontrado o inactivo")

    # Validar sucursal activa si se cambia
    if datos.sucursalId is not None:
        sucursal = db.query(Sucursal).filter(Sucursal.id == datos.sucursalId, Sucursal.estado == 1).first()
        if not sucursal:
            raise HTTPException(status_code=400, detail="La sucursal seleccionada no existe o está inactiva.")

    # Validar nombre duplicado
    if datos.nombre:
        duplicado = db.query(Almacen).filter(
            Almacen.nombre == datos.nombre,
            Almacen.id != almacen_id,
            Almacen.estado == 1
        ).first()
        if duplicado:
            raise HTTPException(status_code=400, detail="Ya existe otro almacén activo con ese nombre.")

    # Actualizar campos
    for key, value in datos.dict(exclude_unset=True).items():
        setattr(almacen, key, value)

    db.commit()
    db.refresh(almacen)
    return almacen


# Eliminación lógica
def eliminar_almacen(db: Session, almacen_id: int):
    almacen = db.query(Almacen).filter(
        Almacen.id == almacen_id,
        Almacen.estado == 1
    ).first()
    if not almacen:
        raise HTTPException(status_code=404, detail="Almacén no encontrado o ya eliminado")

    # 🔎 validar si tiene secciones activas / disponibles
    secciones_activas = db.query(Seccion).filter(
        Seccion.almacenId == almacen_id,   # 👈 FK al almacén
        Seccion.estado == 1                # o .activo == 1
    ).count()

    if secciones_activas > 0:
        raise HTTPException(
            status_code=400,
            detail=f"No se puede eliminar el almacén porque tiene {secciones_activas} sección(es) activas."
        )

    # ✅ si no tiene secciones, eliminación lógica
    almacen.estado = 0
    db.commit()
    return {"mensaje": "Almacén eliminado correctamente (lógicamente)"}