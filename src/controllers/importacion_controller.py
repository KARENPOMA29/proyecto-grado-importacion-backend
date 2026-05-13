# src/controllers/importacion_controller.py

from re import search
from typing import Dict, Any, List
from datetime import datetime
from sqlalchemy import or_, func, String
from src.models.proveedor import Proveedor
from src.models.empleado import Empleado
from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload
from src.models.producto import Producto
from src.models.importacion import Importacion
from src.schemas.importacion import (
    ImportacionCreate,
    ImportacionUpdate,
    ImportacionOut,
)

from sqlalchemy import or_, func
from src.models.vw_control_importaciones import VwControlImportaciones
def listar_control_importaciones(
    db: Session,
    search: str = "",
    situacion: str | None = None,
    page: int = 1,
    pageSize: int = 10,
):
    query = db.query(VwControlImportaciones)

    if search:
        term = f"%{search.lower()}%"

        query = query.filter(
            or_(
                func.lower(VwControlImportaciones.codigo).like(term),
                func.lower(VwControlImportaciones.proveedorNombre).like(term),
                func.lower(VwControlImportaciones.proveedorEncargado).like(term),
                func.lower(VwControlImportaciones.empleadoAsignadoNombre).like(term),
                func.lower(VwControlImportaciones.situacion).like(term),
            )
        )

    if situacion:
        query = query.filter(
            VwControlImportaciones.situacion == situacion
        )

    total = query.count()

    items = (
        query
        .order_by(
            VwControlImportaciones.fechaLlegada.asc()
        )
        .offset((page - 1) * pageSize)
        .limit(pageSize)
        .all()
    )

    return {
        "items": items,
        "total": total,
    }

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
        estado=1,
        descripcion=payload.descripcion,
        empleadoId=payload.empleadoId,
        idEmpleadoAsignado=payload.idEmpleadoAsignado,
    )

    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj



def listar_importaciones(
    db: Session,
    search: str | None = None,
    page: int = 1,
    pageSize: int = 10,
):
    query = (
        db.query(Importacion)
        .options(
            joinedload(Importacion.proveedor),
            joinedload(Importacion.empleadoAsignado),
        )
        .filter(Importacion.estado != 0)
    )

    if search and search.strip():
        term = f"%{search.strip().lower()}%"

        query = (
            query
            .join(Proveedor, Importacion.proveedorId == Proveedor.id)
            .join(Empleado, Importacion.idEmpleadoAsignado == Empleado.id)
            .filter(
                or_(
                    func.lower(Importacion.codigo).like(term),
                    func.lower(Importacion.descripcion).like(term),

                    # proveedor
                    func.lower(Proveedor.razonSocial).like(term),

                    # empleado
                    func.lower(Empleado.nombre).like(term),
                    func.lower(Empleado.apellido).like(term),
                    func.lower(
                        func.concat(Empleado.nombre, " ", Empleado.apellido)
                    ).like(term),

                    # fecha
                    func.cast(Importacion.fechaLlegada, String).like(term),
                )
            )
        )

    total = query.count()

    items = (
        query
        .order_by(Importacion.id.desc())
        .offset((page - 1) * pageSize)
        .limit(pageSize)
        .all()
    )

    return {
        "items": items,
        "total": total,
    }


def obtener_importacion(db: Session, importacion_id: int) -> Importacion:
    obj = (
        db.query(Importacion)
        .options(
            joinedload(Importacion.proveedor),
            joinedload(Importacion.empleadoAsignado),
        )
        .filter(
            Importacion.id == importacion_id,
            Importacion.estado != 0,
        )
        .first()
    )

    if not obj:
        raise HTTPException(
            status_code=404,
            detail="Importación no encontrada o inactiva"
        )

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

def listar_importaciones_concluidas(
    db: Session,
    search: str | None = None,
    page: int = 1,
    pageSize: int = 1000,
):
    query = (
        db.query(Importacion)
        .options(
            joinedload(Importacion.proveedor),
            joinedload(Importacion.empleadoAsignado),
        )
        .filter(Importacion.estado == 2)
    )

    if search and search.strip():
        term = f"%{search.strip().lower()}%"

        query = (
            query
            .join(Proveedor, Importacion.proveedorId == Proveedor.id)
            .join(Empleado, Importacion.idEmpleadoAsignado == Empleado.id)
            .filter(
                or_(
                    func.lower(Importacion.codigo).like(term),
                    func.lower(Importacion.descripcion).like(term),
                    func.lower(Proveedor.razonSocial).like(term),
                    func.lower(Empleado.nombre).like(term),
                    func.lower(Empleado.apellido).like(term),
                    func.lower(
                        func.concat(Empleado.nombre, " ", Empleado.apellido)
                    ).like(term),
                    func.cast(Importacion.fechaLlegada, String).like(term),
                )
            )
        )

    total = query.count()

    items = (
        query
        .order_by(Importacion.id.desc())
        .offset((page - 1) * pageSize)
        .limit(pageSize)
        .all()
    )

    return {
        "items": items,
        "total": total,
    }