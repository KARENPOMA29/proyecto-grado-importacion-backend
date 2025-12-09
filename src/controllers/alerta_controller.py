# src/controllers/alerta_controller.py
from datetime import datetime
from sqlalchemy.orm import Session

from src.models.alerta import Alerta
from src.schemas.alerta import AlertaCreate


def crear_alerta(db: Session, data: AlertaCreate) -> Alerta:
    """
    Crea una nueva alerta.
    La fecha se setea automáticamente con la hora actual del servidor.
    """
    nueva = Alerta(
        tipo=data.tipo,
        mensaje=data.mensaje,
        empleadoId=data.empleadoId,
        fecha=datetime.utcnow(),
        estado=data.estado if data.estado is not None else 1,
    )

    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva


def marcar_leida(db: Session, alerta_id: int) -> Alerta | None:
    """
    Marca una alerta como leída (estado = 0).
    Devuelve la alerta actualizada o None si no existe.
    """
    alerta = db.query(Alerta).filter(Alerta.id == alerta_id).first()
    if not alerta:
        return None

    alerta.estado = 0
    db.commit()
    db.refresh(alerta)
    return alerta
