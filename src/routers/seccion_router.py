# src/routers/seccion_router.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from src.config.db import SessionLocal
from src.schemas.seccion import SeccionCreate, SeccionUpdate, SeccionResponse
from src.controllers import seccion_controller

router = APIRouter(prefix="/secciones", tags=["Secciones"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=SeccionResponse)
def crear_seccion(seccion: SeccionCreate, db: Session = Depends(get_db)):
    return seccion_controller.crear_seccion(db, seccion)

@router.get("/", response_model=List[SeccionResponse])
def listar_secciones(
    almacen_id: Optional[int] = Query(default=None, alias="almacenId"),
    db: Session = Depends(get_db),
):
    return seccion_controller.listar_secciones(db, almacen_id)

@router.get("/{seccion_id}", response_model=SeccionResponse)
def obtener_seccion(seccion_id: int, db: Session = Depends(get_db)):
    return seccion_controller.obtener_seccion(db, seccion_id)

@router.put("/{seccion_id}", response_model=SeccionResponse)
def actualizar_seccion(seccion_id: int, datos: SeccionUpdate, db: Session = Depends(get_db)):
    return seccion_controller.actualizar_seccion(db, seccion_id, datos)

@router.delete("/{seccion_id}")
def eliminar_seccion(seccion_id: int, db: Session = Depends(get_db)):
    return seccion_controller.eliminar_seccion(db, seccion_id)
