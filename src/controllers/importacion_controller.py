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
    Lista las importaciones NO ELIMINADAS (estado != 0) asignadas a un empleado específico.

    Se toma como referencia el campo idEmpleadoAsignado, que representa
    al empleado encargado de la importación.
    """
    return (
        db.query(Importacion)
        .filter(
            Importacion.idEmpleadoAsignado == empleado_id,
            Importacion.estado != 0,  # incluye 1 (activa) y 2 (concluida)
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
        .filter(Importacion.codigo == payload.codigo, Importacion.estado != 0)
        .first()
    )
    if dup:
        raise HTTPException(
            status_code=400,
            detail="Ya existe una importación activa o concluida con ese código."
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
    Lista todas las importaciones con estado 1 (activa) o 2 (concluida).
    Excluye solo las eliminadas (estado = 0).
    """
    return (
        db.query(Importacion)
        .filter(Importacion.estado != 0)
        .all()
    )


def obtener_importacion(db: Session, importacion_id: int) -> Importacion:
    """
    Obtiene una importación NO eliminada por su ID (estado != 0).
    """
    obj = (
        db.query(Importacion)
        .filter(
            Importacion.id == importacion_id,
            Importacion.estado != 0,
        )
        .first()
    )
    if not obj:
        raise HTTPException(status_code=404, detail="Importación no encontrada o inactiva")
    return obj


def actualizar_importacion(
    db: Session, importacion_id: int, payload: ImportacionUpdate
) -> Importacion:
    """
    Actualiza los datos de una importación.
    - No permite modificar si la importación está concluida (estado = 2).
    """
    obj = obtener_importacion(db, importacion_id)

    # 🚫 no permitir editar si ya está concluida
    if obj.estado == 2:
        raise HTTPException(
            status_code=400,
            detail="No se puede modificar una importación concluida.",
        )

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
