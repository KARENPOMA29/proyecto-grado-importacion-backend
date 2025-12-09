from sqlalchemy.orm import Session
from fastapi import HTTPException

from src.models.marca import Marca
from src.schemas.marca import MarcaCreate, MarcaUpdate


def crear_marca(db: Session, datos: MarcaCreate):
    existente = (
        db.query(Marca)
        .filter(Marca.nombre == datos.nombre)
        .first()
    )
    if existente:
        raise HTTPException(
            status_code=400,
            detail="Ya existe una marca con ese nombre.",
        )

    marca = Marca(nombre=datos.nombre)
    db.add(marca)
    db.commit()
    db.refresh(marca)
    return marca


def listar_marcas(db: Session):
    return db.query(Marca).all()


def obtener_marca(db: Session, marca_id: int):
    marca = db.query(Marca).filter(Marca.id == marca_id).first()
    if not marca:
        raise HTTPException(status_code=404, detail="Marca no encontrada")
    return marca


def actualizar_marca(db: Session, marca_id: int, datos: MarcaUpdate):
    marca = db.query(Marca).filter(Marca.id == marca_id).first()
    if not marca:
        raise HTTPException(status_code=404, detail="Marca no encontrada")

    update_data = datos.model_dump(exclude_unset=True)

    if "nombre" in update_data:
        duplicado = (
            db.query(Marca)
            .filter(Marca.nombre == update_data["nombre"], Marca.id != marca_id)
            .first()
        )
        if duplicado:
            raise HTTPException(
                status_code=400,
                detail="Ya existe otra marca con ese nombre.",
            )

    for k, v in update_data.items():
        setattr(marca, k, v)

    db.commit()
    db.refresh(marca)
    return marca


def eliminar_marca(db: Session, marca_id: int):
    marca = db.query(Marca).filter(Marca.id == marca_id).first()
    if not marca:
        raise HTTPException(status_code=404, detail="Marca no encontrada")

    # Eliminación física (tu tabla Marca no tiene campo estado)
    db.delete(marca)
    db.commit()
    return {"mensaje": "Marca eliminada correctamente"}
