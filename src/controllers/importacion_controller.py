from typing import Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime
from sqlalchemy import or_

from src.models.importacion import Importacion
from src.schemas.importacion import ImportacionCreate, ImportacionUpdate, ImportacionOut


def crear_importacion(db: Session, payload: ImportacionCreate) -> Importacion:
    # Evitar duplicados por código
    dup = db.query(Importacion).filter(
        Importacion.codigo == payload.codigo,
        Importacion.activo == 1
    ).first()
    if dup:
        raise HTTPException(status_code=400, detail="Ya existe una importación con ese código.")

    obj = Importacion(
        codigo=payload.codigo,
        proveedorId=payload.proveedorId,
        fechaLlegada=payload.fechaLlegada,
        estado=payload.estado,
        observaciones=payload.observaciones,
        empleadoId=payload.empleadoId,
        fechaRegistro=datetime.utcnow(),
        activo=1
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def listar_importaciones(db: Session):
    return db.query(Importacion).filter(Importacion.activo == 1).all()


def obtener_importacion(db: Session, importacion_id: int) -> Importacion:
    obj = db.query(Importacion).filter(
        Importacion.id == importacion_id, 
        Importacion.activo == 1
    ).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Importación no encontrada")
    return obj

def actualizar_importacion(db: Session, importacion_id: int, payload: ImportacionUpdate) -> Importacion:
    obj = obtener_importacion(db, importacion_id)
    
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    
    obj.fechaActualizacion = datetime.utcnow()
    db.commit()
    db.refresh(obj)
    return obj

def eliminar_importacion(db: Session, importacion_id: int):
    obj = obtener_importacion(db, importacion_id)
    obj.activo = 0
    obj.fechaActualizacion = datetime.utcnow()
    db.commit()
    return {"ok": True}
