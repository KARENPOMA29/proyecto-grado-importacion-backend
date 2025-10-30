from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from src.config.db import get_db
from src.schemas.importacion import ImportacionCreate, ImportacionOut, ImportacionUpdate
from src.controllers import importacion_controller

router = APIRouter(prefix="/importaciones", tags=["Importaciones"])

@router.get("/", response_model=list[ImportacionOut])
def listar_importaciones(db: Session = Depends(get_db)):
    return importacion_controller.listar_importaciones(db)

@router.post("/", response_model=ImportacionOut)
def crear_importacion(payload: ImportacionCreate, db: Session = Depends(get_db)):
    return importacion_controller.crear_importacion(db, payload)

@router.get("/{importacion_id}", response_model=ImportacionOut)
def obtener_importacion(importacion_id: int, db: Session = Depends(get_db)):
    return importacion_controller.obtener_importacion(db, importacion_id)

@router.put("/{importacion_id}", response_model=ImportacionOut)
def actualizar_importacion(importacion_id: int, payload: ImportacionUpdate, db: Session = Depends(get_db)):
    return importacion_controller.actualizar_importacion(db, importacion_id, payload)

@router.delete("/{importacion_id}")
def eliminar_importacion(importacion_id: int, db: Session = Depends(get_db)):
    return importacion_controller.eliminar_importacion(db, importacion_id)
