from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from src.config.db import SessionLocal
from src.schemas.ciudad import (
    CiudadCreate,
    CiudadUpdate,
    CiudadResponse,
)
from src.controllers import ciudad_controller

router = APIRouter(prefix="/ciudades", tags=["Ciudades"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=CiudadResponse)
def crear_ciudad(ciudad: CiudadCreate, db: Session = Depends(get_db)):
    return ciudad_controller.crear_ciudad(db, ciudad)


@router.get("/", response_model=List[CiudadResponse])
def listar_ciudades(db: Session = Depends(get_db)):
    return ciudad_controller.listar_ciudades(db)


@router.get("/{ciudad_id}", response_model=CiudadResponse)
def obtener_ciudad(ciudad_id: int, db: Session = Depends(get_db)):
    return ciudad_controller.obtener_ciudad(db, ciudad_id)


@router.put("/{ciudad_id}", response_model=CiudadResponse)
def actualizar_ciudad(
    ciudad_id: int,
    datos: CiudadUpdate,
    db: Session = Depends(get_db),
):
    return ciudad_controller.actualizar_ciudad(db, ciudad_id, datos)


@router.delete("/{ciudad_id}")
def eliminar_ciudad(ciudad_id: int, db: Session = Depends(get_db)):
    return ciudad_controller.eliminar_ciudad(db, ciudad_id)
