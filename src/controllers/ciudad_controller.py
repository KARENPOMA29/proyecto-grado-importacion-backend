from sqlalchemy.orm import Session
from fastapi import HTTPException

from src.models.ciudad import Ciudad
from src.models.sucursal import Sucursal
from src.schemas.ciudad import CiudadCreate, CiudadUpdate


def crear_ciudad(db: Session, ciudad: CiudadCreate):
    existente = db.query(Ciudad).filter(Ciudad.nombre == ciudad.nombre).first()
    if existente:
        raise HTTPException(
            status_code=400,
            detail="Ya existe una ciudad con ese nombre."
        )

    nueva = Ciudad(**ciudad.model_dump())
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva


def listar_ciudades(db: Session):
    return db.query(Ciudad).all()


def obtener_ciudad(db: Session, ciudad_id: int):
    ciudad = db.query(Ciudad).filter(Ciudad.id == ciudad_id).first()
    if not ciudad:
        raise HTTPException(status_code=404, detail="Ciudad no encontrada")
    return ciudad


def actualizar_ciudad(db: Session, ciudad_id: int, datos: CiudadUpdate):
    ciudad = db.query(Ciudad).filter(Ciudad.id == ciudad_id).first()
    if not ciudad:
        raise HTTPException(status_code=404, detail="Ciudad no encontrada")

    datos_dict = datos.model_dump(exclude_unset=True)

    if "nombre" in datos_dict and datos_dict["nombre"]:
        duplicado = db.query(Ciudad).filter(
            Ciudad.nombre == datos_dict["nombre"],
            Ciudad.id != ciudad_id
        ).first()
        if duplicado:
            raise HTTPException(
                status_code=400,
                detail="Ya existe otra ciudad con ese nombre."
            )

    for key, value in datos_dict.items():
        setattr(ciudad, key, value)

    db.commit()
    db.refresh(ciudad)
    return ciudad


def eliminar_ciudad(db: Session, ciudad_id: int):
    ciudad = db.query(Ciudad).filter(Ciudad.id == ciudad_id).first()
    if not ciudad:
        raise HTTPException(status_code=404, detail="Ciudad no encontrada")

    # validar sucursales asociadas
    sucursales_count = db.query(Sucursal).filter(
        Sucursal.idCiudad == ciudad_id,
        Sucursal.estado == 1
    ).count()

    if sucursales_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"No se puede eliminar la ciudad porque tiene "
                   f"{sucursales_count} sucursal(es) activas asociadas."
        )

    db.delete(ciudad)
    db.commit()
    return {"mensaje": "Ciudad eliminada correctamente"}
