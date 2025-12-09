from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.config.db import SessionLocal
from src.schemas.marca import MarcaCreate, MarcaUpdate, MarcaResponse
from src.controllers import marca_controller

router = APIRouter(prefix="/marcas", tags=["Marcas"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=MarcaResponse)
def crear_marca(datos: MarcaCreate, db: Session = Depends(get_db)):
    return marca_controller.crear_marca(db, datos)


@router.get("/", response_model=List[MarcaResponse])
def listar_marcas(db: Session = Depends(get_db)):
    return marca_controller.listar_marcas(db)


@router.get("/{marca_id}", response_model=MarcaResponse)
def obtener_marca(marca_id: int, db: Session = Depends(get_db)):
    return marca_controller.obtener_marca(db, marca_id)


@router.put("/{marca_id}", response_model=MarcaResponse)
def actualizar_marca(
    marca_id: int,
    datos: MarcaUpdate,
    db: Session = Depends(get_db),
):
    return marca_controller.actualizar_marca(db, marca_id, datos)


@router.delete("/{marca_id}")
def eliminar_marca(marca_id: int, db: Session = Depends(get_db)):
    return marca_controller.eliminar_marca(db, marca_id)
