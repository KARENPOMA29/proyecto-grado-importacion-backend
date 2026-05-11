from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from src.config.db import SessionLocal
from src.schemas.almacen import AlmacenCreate, AlmacenUpdate, AlmacenResponse
from src.controllers import almacen_controller

router = APIRouter(prefix="/almacenes", tags=["Almacenes"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ✅ único GET para listar (filtra por sucursal si llega ?sucursalId=)
@router.get("/")
def listar_almacenes(
    sucursal_id: Optional[int] = Query(default=None, alias="sucursalId"),
    search: Optional[str] = Query(default=None),
    page: int = Query(default=1),
    pageSize: int = Query(default=10),
    db: Session = Depends(get_db),
):
    return almacen_controller.listar_almacenes(
        db=db,
        sucursal_id=sucursal_id,
        search=search,
        page=page,
        pageSize=pageSize,
    )
@router.get("/combo")
def combo_almacenes(
    db: Session = Depends(get_db),
):
    return almacen_controller.combo_almacenes(db)
@router.post("/", response_model=AlmacenResponse)
def crear_almacen(almacen: AlmacenCreate, db: Session = Depends(get_db)):
    return almacen_controller.crear_almacen(db, almacen)


@router.get("/{almacen_id}", response_model=AlmacenResponse)
def obtener_almacen(almacen_id: int, db: Session = Depends(get_db)):
    return almacen_controller.obtener_almacen(db, almacen_id)


@router.put("/{almacen_id}", response_model=AlmacenResponse)
def actualizar_almacen(
    almacen_id: int,
    datos: AlmacenUpdate,
    db: Session = Depends(get_db),
):
    return almacen_controller.actualizar_almacen(db, almacen_id, datos)


@router.delete("/{almacen_id}")
def eliminar_almacen(almacen_id: int, db: Session = Depends(get_db)):
    return almacen_controller.eliminar_almacen(db, almacen_id)
