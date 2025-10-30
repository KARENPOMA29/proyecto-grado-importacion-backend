# src/routes/movimiento_route.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.config.db import get_db
from src.schemas.movimiento import MovimientoCreate, MovimientoOut, MovimientoUpdate
from src.controllers import movimiento_controller as ctl

router = APIRouter(prefix="/movimientos", tags=["Movimientos"])

@router.post("/", response_model=MovimientoOut)
def crear(payload: MovimientoCreate, db: Session = Depends(get_db)):
    return ctl.crear_movimiento(db, payload, usuario_id=None)

@router.get("/", response_model=list[MovimientoOut])
def listar(db: Session = Depends(get_db)):
    return ctl.listar_movimientos(db)

@router.get("/{movimiento_id}", response_model=MovimientoOut)
def obtener(movimiento_id: int, db: Session = Depends(get_db)):
    return ctl.obtener_movimiento(db, movimiento_id)

@router.put("/{movimiento_id}", response_model=MovimientoOut)
def actualizar(movimiento_id: int, payload: MovimientoUpdate, db: Session = Depends(get_db)):
    return ctl.actualizar_movimiento(db, movimiento_id, payload, usuario_id=None)

@router.delete("/{movimiento_id}")
def eliminar(movimiento_id: int, db: Session = Depends(get_db)):
    return ctl.eliminar_movimiento(db, movimiento_id)
