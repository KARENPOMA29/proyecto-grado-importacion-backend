from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Optional

from src.models.almacen import Almacen
from src.models.sucursal import Sucursal
from src.schemas.almacen import AlmacenCreate, AlmacenUpdate
from src.models.seccion import Seccion 


# Crear almacén
def crear_almacen(db: Session, almacen: AlmacenCreate):
    if almacen.sucursalId is not None:
        sucursal = db.query(Sucursal).filter(
            Sucursal.id == almacen.sucursalId,
            Sucursal.estado == 1
        ).first()
        if not sucursal:
            raise HTTPException(
                status_code=400,
                detail="La sucursal seleccionada no existe o está inactiva."
            )

    existente = db.query(Almacen).filter(
        Almacen.nombre == almacen.nombre,
        Almacen.estado == 1
    ).first()
    if existente:
        raise HTTPException(
            status_code=400,
            detail="Ya existe un almacén activo con ese nombre."
        )

    nuevo = Almacen(**almacen.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


# ✅ Listar almacenes (opcionalmente filtrados por sucursal)
def listar_almacenes(
    db: Session,
    sucursal_id: Optional[int] = None,
    search: Optional[str] = None,
    page: int = 1,
    pageSize: int = 10
):
    query = db.query(Almacen).filter(Almacen.estado == 1)

    if sucursal_id is not None:
        query = query.filter(Almacen.sucursalId == sucursal_id)

    if search and search.strip():
        texto = f"%{search.strip()}%"
        query = query.join(Sucursal, Almacen.sucursalId == Sucursal.id).filter(
            (Almacen.nombre.ilike(texto)) |
            (Almacen.direccion.ilike(texto)) |
            (Sucursal.nombre.ilike(texto))
        )

    total = query.count()

    items = (
        query
        .order_by(Almacen.id.desc())
        .offset((page - 1) * pageSize)
        .limit(pageSize)
        .all()
    )

    return {
        "items": items,
        "total": total,
    }

def combo_almacenes(db: Session):
    almacenes = (
        db.query(Almacen)
        .filter(Almacen.estado == 1)
        .order_by(Almacen.nombre.asc())
        .all()
    )

    return [
        {
            "id": a.id,
            "nombre": a.nombre,
        }
        for a in almacenes
    ]

# Obtener almacén por ID
def obtener_almacen(db: Session, almacen_id: int):
    almacen = db.query(Almacen).filter(
        Almacen.id == almacen_id,
        Almacen.estado == 1
    ).first()
    if not almacen:
        raise HTTPException(
            status_code=404,
            detail="Almacén no encontrado o inactivo"
        )
    return almacen


# Actualizar almacén
def actualizar_almacen(db: Session, almacen_id: int, datos: AlmacenUpdate):
    almacen = db.query(Almacen).filter(
        Almacen.id == almacen_id,
        Almacen.estado == 1
    ).first()
    if not almacen:
        raise HTTPException(
            status_code=404,
            detail="Almacén no encontrado o inactivo"
        )

    if datos.sucursalId is not None:
        sucursal = db.query(Sucursal).filter(
            Sucursal.id == datos.sucursalId,
            Sucursal.estado == 1
        ).first()
        if not sucursal:
            raise HTTPException(
                status_code=400,
                detail="La sucursal seleccionada no existe o está inactiva."
            )

    if datos.nombre:
        duplicado = db.query(Almacen).filter(
            Almacen.nombre == datos.nombre,
            Almacen.id != almacen_id,
            Almacen.estado == 1
        ).first()
        if duplicado:
            raise HTTPException(
                status_code=400,
                detail="Ya existe otro almacén activo con ese nombre."
            )

    for key, value in datos.model_dump(exclude_unset=True).items():
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
        raise HTTPException(
            status_code=404,
            detail="Almacén no encontrado o ya eliminado"
        )

    secciones_activas = db.query(Seccion).filter(
        Seccion.almacenId == almacen_id,
        Seccion.estado == 1
    ).count()

    if secciones_activas > 0:
        raise HTTPException(
            status_code=400,
            detail=f"No se puede eliminar el almacén porque tiene {secciones_activas} sección(es) activas."
        )

    almacen.estado = 0
    db.commit()
    return {"mensaje": "Almacén eliminado correctamente (lógicamente)"}
