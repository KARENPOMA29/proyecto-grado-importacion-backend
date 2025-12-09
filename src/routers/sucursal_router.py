from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from src.config.db import SessionLocal
from src.schemas.sucursal import (
    SucursalCreate,
    SucursalUpdate,
    SucursalResponse,
)
from src.controllers import sucursal_controller

router = APIRouter(prefix="/sucursales", tags=["Sucursales"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=SucursalResponse)
def crear_sucursal(sucursal: SucursalCreate, db: Session = Depends(get_db)):
    return sucursal_controller.crear_sucursal(db, sucursal)


@router.get("/", response_model=List[SucursalResponse])
def listar_sucursales(
    ciudadId: int | None = Query(default=None),   # 👈 nuevo filtro opcional
    db: Session = Depends(get_db),
):
    return sucursal_controller.listar_sucursales(db, ciudad_id=ciudadId)

@router.get("/{sucursal_id}", response_model=SucursalResponse)
def obtener_sucursal(sucursal_id: int, db: Session = Depends(get_db)):
    return sucursal_controller.obtener_sucursal(db, sucursal_id)


@router.put("/{sucursal_id}", response_model=SucursalResponse)
def actualizar_sucursal(
    sucursal_id: int,
    datos: SucursalUpdate,
    db: Session = Depends(get_db),
):
    return sucursal_controller.actualizar_sucursal(db, sucursal_id, datos)


@router.delete("/{sucursal_id}")
def eliminar_sucursal(sucursal_id: int, db: Session = Depends(get_db)):
    return sucursal_controller.eliminar_sucursal(db, sucursal_id)
