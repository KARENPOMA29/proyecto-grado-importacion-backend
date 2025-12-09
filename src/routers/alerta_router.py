# src/routers/alerta_router.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.config.db import SessionLocal
from src.models.alerta import Alerta
from src.models.empleado import Empleado
from src.schemas.alerta import AlertaOut, AlertaCreate
from src.controllers.alerta_controller import crear_alerta, marcar_leida

router = APIRouter(
    prefix="/alertas",
    tags=["Alertas"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/dashboard", response_model=List[AlertaOut])
def alertas_dashboard(limite: int = 5, db: Session = Depends(get_db)):
    """
    Devuelve las últimas alertas ACTIVAS (estado = 1) del administrador.
    """
    admin = (
        db.query(Empleado)
        .filter(
            Empleado.rol.in_(["ADMIN", "Administrador"]),
            Empleado.estado == 1,
        )
        .first()
    )
    if not admin:
        return []

    return (
        db.query(Alerta)
        .filter(
            Alerta.empleadoId == admin.id,
            Alerta.estado == 1,  # 👈 solo activas/no leídas
        )
        .order_by(Alerta.fecha.desc())
        .limit(limite)
        .all()
    )


@router.post("", response_model=AlertaOut, status_code=status.HTTP_201_CREATED)
def crear_alerta_endpoint(payload: AlertaCreate, db: Session = Depends(get_db)):
    """
    Endpoint para crear alertas (por si las quieres probar desde /docs).
    """
    return crear_alerta(db, payload)


@router.put("/{id}/leer", status_code=status.HTTP_200_OK)
def marcar_alerta_leida_endpoint(id: int, db: Session = Depends(get_db)):
    """
    Marca una alerta como leída (estado = 0).
    Usado por el botón "Marcar como leída" en el dashboard.
    """
    alerta = marcar_leida(db, id)
    if not alerta:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")

    return {"mensaje": "Alerta marcada como leída"}
