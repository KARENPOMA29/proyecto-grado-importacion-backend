# src/controllers/importacion_controller.py
from typing import Dict, Any, List
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.models.producto import Producto
from src.models.importacion import Importacion
from src.schemas.importacion import (
    ImportacionCreate,
    ImportacionUpdate,
    ImportacionOut,
)

def listar_importaciones_por_empleado(
    db: Session,
    empleado_id: int,
) -> List[Importacion]:
    """
    Lista las importaciones ACTIVAS (estado = 1) asignadas a un empleado específico.

    Se toma como referencia el campo idEmpleadoAsignado, que representa
    al empleado encargado de la importación.
    """
    return (
        db.query(Importacion)
        .filter(
            Importacion.idEmpleadoAsignado == empleado_id,
            Importacion.estado == 1,  # solo activas
        )
        .all()
    )
def crear_importacion(db: Session, payload: ImportacionCreate) -> Importacion:
    """
    Crea una nueva importación. 
    Se valida que no haya duplicado de código y se asigna estado = 1 (activo) por defecto.
    """
    # Evitar duplicados por código activos
    dup = (
        db.query(Importacion)
        .filter(Importacion.codigo == payload.codigo, Importacion.estado == 1)
        .first()
    )
    if dup:
        raise HTTPException(
            status_code=400,
            detail="Ya existe una importación activa con ese código."
        )

    obj = Importacion(
        codigo=payload.codigo,
        proveedorId=payload.proveedorId,
        fechaLlegada=payload.fechaLlegada,
        estado=1,  # activa al crear
        descripcion=payload.descripcion,
        empleadoId=payload.empleadoId,
        idEmpleadoAsignado=payload.idEmpleadoAsignado,
        fechaRegistro=datetime.utcnow(),
    )

    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def listar_importaciones(db: Session) -> list[Importacion]:
    """
    Lista todas las importaciones activas (estado = 1).
    """
    return db.query(Importacion).filter(Importacion.estado == 1).all()


def obtener_importacion(db: Session, importacion_id: int) -> Importacion:
    """
    Obtiene una importación activa por su ID.
    """
    obj = (
        db.query(Importacion)
        .filter(Importacion.id == importacion_id, Importacion.estado == 1)
        .first()
    )
    if not obj:
        raise HTTPException(status_code=404, detail="Importación no encontrada o inactiva")
    return obj


def actualizar_importacion(
    db: Session, importacion_id: int, payload: ImportacionUpdate
) -> Importacion:
    """
    Actualiza los datos de una importación activa.
    """
    obj = obtener_importacion(db, importacion_id)

    # Actualizar solo los campos enviados
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)

    db.commit()
    db.refresh(obj)
    return obj


def eliminar_importacion(db: Session, importacion_id: int) -> Dict[str, Any]:
    """
    Marca como inactiva (estado = 0) una importación, 
    si no tiene productos activos vinculados.
    """
    obj = obtener_importacion(db, importacion_id)

    # Verificar si existen productos activos vinculados
    productos_activos = (
        db.query(Producto)
        .filter(
            Producto.importacionId == importacion_id,
            Producto.estado == 1  # activo
        )
        .count()
    )

    if productos_activos > 0:
        raise HTTPException(
            status_code=400,
            detail=f"No se puede eliminar la importación porque tiene {productos_activos} productos activos."
        )

    # Marcar como inactiva (soft delete)
    obj.estado = 0
    db.commit()

    return {"ok": True, "mensaje": "Importación desactivada correctamente"}
