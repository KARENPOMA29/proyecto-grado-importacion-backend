from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from src.config.db import SessionLocal
from src.schemas.modelo_producto import ModeloProductoCreate, ModeloProductoUpdate, ModeloProductoResponse
from src.controllers import modelo_producto_controller

router = APIRouter(prefix="/modelos", tags=["Modelos de Producto"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=ModeloProductoResponse)
def crear_modelo(modelo: ModeloProductoCreate, db: Session = Depends(get_db)):
    return modelo_producto_controller.crear_modelo(db, modelo)

@router.get("/", response_model=List[ModeloProductoResponse])
def listar_modelos(db: Session = Depends(get_db)):
    return modelo_producto_controller.listar_modelos(db)

@router.get("/{modelo_id}", response_model=ModeloProductoResponse)
def obtener_modelo(modelo_id: int, db: Session = Depends(get_db)):
    return modelo_producto_controller.obtener_modelo(db, modelo_id)

@router.put("/{modelo_id}", response_model=ModeloProductoResponse)
def actualizar_modelo(modelo_id: int, datos: ModeloProductoUpdate, db: Session = Depends(get_db)):
    return modelo_producto_controller.actualizar_modelo(db, modelo_id, datos)

@router.delete("/{modelo_id}")
def eliminar_modelo(modelo_id: int, db: Session = Depends(get_db)):
    return modelo_producto_controller.eliminar_modelo(db, modelo_id)
