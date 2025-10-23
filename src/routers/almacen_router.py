from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
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

@router.post("/", response_model=AlmacenResponse)
def crear_almacen(almacen: AlmacenCreate, db: Session = Depends(get_db)):
    return almacen_controller.crear_almacen(db, almacen)

@router.get("/", response_model=List[AlmacenResponse])
def listar_almacenes(db: Session = Depends(get_db)):
    return almacen_controller.listar_almacenes(db)

@router.get("/{almacen_id}", response_model=AlmacenResponse)
def obtener_almacen(almacen_id: int, db: Session = Depends(get_db)):
    return almacen_controller.obtener_almacen(db, almacen_id)

@router.put("/{almacen_id}", response_model=AlmacenResponse)
def actualizar_almacen(almacen_id: int, datos: AlmacenUpdate, db: Session = Depends(get_db)):
    return almacen_controller.actualizar_almacen(db, almacen_id, datos)

@router.delete("/{almacen_id}")
def eliminar_almacen(almacen_id: int, db: Session = Depends(get_db)):
    return almacen_controller.eliminar_almacen(db, almacen_id)
