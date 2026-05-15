# src/routes/importacion_routes.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional


from src.config.db import get_db
from src.schemas.importacion import (
    ImportacionCreate,
    ImportacionOut,
    ImportacionUpdate,
)
from src.controllers import importacion_controller

router = APIRouter(prefix="/importaciones", tags=["Importaciones"])

@router.get("/empleado/{empleado_id}")
def listar_por_empleado(
    empleado_id: int,
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1),
    db: Session = Depends(get_db),
):
    return importacion_controller.listar_importaciones_por_empleado(
        db=db,
        empleado_id=empleado_id,
        search=search,
        page=page,
        pageSize=pageSize,
    )

@router.get("/control")
def listar_control_importaciones(
    search: str | None = None,
    situacion: str | None = None,
    page: int = 1,
    pageSize: int = 10,
    db: Session = Depends(get_db),
):
    return importacion_controller.listar_control_importaciones(
        db,
        search,
        situacion,
        page,
        pageSize,
    )

@router.get("/")
def listar_importaciones(
    search: str | None = None,
    page: int = 1,
    pageSize: int = 10,
    db: Session = Depends(get_db),
):
    return importacion_controller.listar_importaciones(db, search, page, pageSize)


@router.post("/", response_model=ImportacionOut)
def crear_importacion(
    payload: ImportacionCreate,
    db: Session = Depends(get_db),
):
    return importacion_controller.crear_importacion(db, payload)

@router.get("/concluidas")
def listar_importaciones_concluidas(
    search: Optional[str] = Query(default=None),
    page: int = Query(default=1),
    pageSize: int = Query(default=1000),
    db: Session = Depends(get_db),
):
    return importacion_controller.listar_importaciones_concluidas(
        db=db,
        search=search,
        page=page,
        pageSize=pageSize,
    )

@router.get("/{importacion_id}", response_model=ImportacionOut)
def obtener_importacion(
    importacion_id: int,
    db: Session = Depends(get_db),
):
    return importacion_controller.obtener_importacion(db, importacion_id)


@router.put("/{importacion_id}", response_model=ImportacionOut)
def actualizar_importacion(
    importacion_id: int,
    payload: ImportacionUpdate,
    db: Session = Depends(get_db),
):
    return importacion_controller.actualizar_importacion(db, importacion_id, payload)


@router.delete("/{importacion_id}")
def eliminar_importacion(
    importacion_id: int,
    db: Session = Depends(get_db),
):
    return importacion_controller.eliminar_importacion(db, importacion_id)
