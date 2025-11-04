from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.models.sucursal import Sucursal
from src.schemas.sucursal import SucursalCreate, SucursalUpdate
from src.models.almacen import Almacen     
from src.models.venta import Venta 
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
    sucursal = db.query(Sucursal).filter(
        Sucursal.id == sucursal_id,
        Sucursal.estado == 1
    ).first()
    if not sucursal:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada o ya eliminada")

    # 🔎 1) validar almacenes activos en esta sucursal
    almacenes_activos = db.query(Almacen).filter(
        Almacen.sucursalId == sucursal_id,   # cambia al nombre real de tu FK
        Almacen.estado == 1                  # o .activo == 1
    ).count()

    if almacenes_activos > 0:
        raise HTTPException(
            status_code=400,
            detail=f"No se puede eliminar la sucursal porque tiene {almacenes_activos} almacén(es) activos."
        )

    # 🔎 2) validar ventas activas en esta sucursal
    ventas_activas = db.query(Venta).filter(
        Venta.sucursalId == sucursal_id,     # cambia al nombre real de tu FK
        Venta.estado == 1                    # o .activo == 1
    ).count()

    if ventas_activas > 0:
        raise HTTPException(
            status_code=400,
            detail=f"No se puede eliminar la sucursal porque tiene {ventas_activas} venta(s) activas."
        )

    # ✅ si no tiene dependencias, eliminación lógica
    sucursal.estado = 0
    db.commit()
    return {"mensaje": "Sucursal eliminada correctamente (lógicamente)"}
