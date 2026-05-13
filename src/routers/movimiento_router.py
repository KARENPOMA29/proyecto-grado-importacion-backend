# src/routers/movimiento_router.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from src.config.db import SessionLocal
from src.controllers import movimiento_controller
from src.schemas.movimiento import MovimientoCreate, MovimientoOut, MovimientoUpdate

router = APIRouter(prefix="/movimientos", tags=["Movimientos"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 📦 Crear movimiento
@router.post("/", response_model=MovimientoOut)
def crear_movimiento(
    payload: MovimientoCreate,
    db: Session = Depends(get_db),
):
    # si el schema MovimientoCreate tiene usuarioId opcional:
    usuario_id = getattr(payload, "usuarioId", None)
    return movimiento_controller.crear_movimiento(db, payload, usuario_id)

# 📋 Listar movimientos (filtros opcionales: usuarioId, almacenId)
@router.get("/")
def listar_movimientos(
    usuarioId: Optional[int] = Query(default=None),
    almacenId: Optional[int] = Query(default=None),
    search: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    estadoProducto: Optional[int] = Query(default=None),
    fecha: Optional[str] = Query(default=None),
):
    return movimiento_controller.listar_movimientos(
        db,
        usuario_id=usuarioId,
        almacen_id=almacenId,
        search=search,
        page=page,
        page_size=pageSize,
        estado_producto=estadoProducto,
        fecha=fecha,
    )
# 🔍 Obtener movimiento por ID
@router.get("/{movimiento_id}", response_model=MovimientoOut)
def obtener_movimiento(
    movimiento_id: int,
    db: Session = Depends(get_db),
):
    return movimiento_controller.obtener_movimiento(db, movimiento_id)

# ✏️ Actualizar movimiento
@router.put("/{movimiento_id}", response_model=MovimientoOut)
def actualizar_movimiento(
    movimiento_id: int,
    payload: MovimientoUpdate,
    db: Session = Depends(get_db),
):
    usuario_id = getattr(payload, "usuarioId", None)
    return movimiento_controller.actualizar_movimiento(
        db,
        movimiento_id,
        payload,
        usuario_id,
    )

# 🗑️ Eliminar movimiento
@router.delete("/{movimiento_id}")
def eliminar_movimiento(
    movimiento_id: int,
    db: Session = Depends(get_db),
):
    return movimiento_controller.eliminar_movimiento(db, movimiento_id)
