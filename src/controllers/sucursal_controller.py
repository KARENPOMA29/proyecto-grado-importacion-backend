# src/controllers/sucursal_controller.py
from sqlalchemy.orm import Session
from fastapi import HTTPException

from src.models.sucursal import Sucursal
from src.models.almacen import Almacen
from src.models.venta import Venta
from src.schemas.sucursal import SucursalCreate, SucursalUpdate

def crear_sucursal(db: Session, sucursal: SucursalCreate):
    existente = db.query(Sucursal).filter(
        Sucursal.nombre == sucursal.nombre,
        Sucursal.estado == 1
    ).first()

    if existente:
        raise HTTPException(status_code=400, detail="Ya existe una sucursal activa con ese nombre.")

    nueva = Sucursal(**sucursal.model_dump())
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva


def listar_sucursales(db: Session, ciudad_id: int | None = None):
    """
    Lista sucursales activas.
    Si se envía ciudad_id, filtra solo las sucursales de esa ciudad.
    """
    query = db.query(Sucursal).filter(Sucursal.estado == 1)

    if ciudad_id is not None:
        query = query.filter(Sucursal.idCiudad == ciudad_id)

    return query.all()


def obtener_sucursal(db: Session, sucursal_id: int):
    sucursal = db.query(Sucursal).filter(
        Sucursal.id == sucursal_id,
        Sucursal.estado == 1
    ).first()

    if not sucursal:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada o inactiva")

    return sucursal


def actualizar_sucursal(db: Session, sucursal_id: int, datos: SucursalUpdate):
    sucursal = db.query(Sucursal).filter(
        Sucursal.id == sucursal_id,
        Sucursal.estado == 1
    ).first()

    if not sucursal:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada o inactiva")

    # Validar duplicado
    if datos.nombre:
        duplicado = db.query(Sucursal).filter(
            Sucursal.nombre == datos.nombre,
            Sucursal.id != sucursal_id,
            Sucursal.estado == 1
        ).first()
        if duplicado:
            raise HTTPException(status_code=400, detail="Ya existe otra sucursal activa con ese nombre.")

    for key, value in datos.model_dump(exclude_unset=True).items():
        setattr(sucursal, key, value)

    db.commit()
    db.refresh(sucursal)
    return sucursal


def eliminar_sucursal(db: Session, sucursal_id: int):
    sucursal = db.query(Sucursal).filter(
        Sucursal.id == sucursal_id,
        Sucursal.estado == 1
    ).first()

    if not sucursal:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada o ya eliminada")

    almacenes_activos = db.query(Almacen).filter(
        Almacen.sucursalId == sucursal_id,
        Almacen.estado == 1
    ).count()

    if almacenes_activos > 0:
        raise HTTPException(
            status_code=400,
            detail=f"No se puede eliminar porque tiene {almacenes_activos} almacén(es) activos."
        )

    ventas_activas = db.query(Venta).filter(
        Venta.sucursalId == sucursal_id,
        Venta.estado == 1
    ).count()

    if ventas_activas > 0:
        raise HTTPException(
            status_code=400,
            detail=f"No se puede eliminar porque tiene {ventas_activas} venta(s) activas."
        )

    sucursal.estado = 0
    db.commit()

    return {"mensaje": "Sucursal eliminada correctamente (lógica)"}
