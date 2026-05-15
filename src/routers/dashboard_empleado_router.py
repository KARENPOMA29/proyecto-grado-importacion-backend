from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.config.db import SessionLocal
from src.controllers import dashboard_empleado_controller as controller


router = APIRouter(
    prefix="/dashboard-empleado",
    tags=["Dashboard Empleado"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/{empleado_id}")
def obtener_dashboard_empleado(
    empleado_id: int,
    db: Session = Depends(get_db)
):
    return controller.obtener_dashboard_por_empleado(db, empleado_id)