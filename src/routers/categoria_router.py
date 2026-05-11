from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from src.config.db import SessionLocal
from src.schemas.categoria import CategoriaCreate, CategoriaUpdate, CategoriaResponse
from src.controllers import categoria_controller

router = APIRouter(prefix="/categorias", tags=["Categorías"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=CategoriaResponse)
def crear_categoria(categoria: CategoriaCreate, db: Session = Depends(get_db)):
    return categoria_controller.crear_categoria(db, categoria)

@router.get("/")
def listar_categorias(
    search: Optional[str] = None,
    page: int = 1,
    pageSize: int = 10,
    db: Session = Depends(get_db)
):
    return categoria_controller.listar_categorias(
        db=db,
        search=search,
        page=page,
        pageSize=pageSize
    )

@router.get("/{categoria_id}", response_model=CategoriaResponse)
def obtener_categoria(categoria_id: int, db: Session = Depends(get_db)):
    return categoria_controller.obtener_categoria(db, categoria_id)

@router.put("/{categoria_id}", response_model=CategoriaResponse)
def actualizar_categoria(categoria_id: int, datos: CategoriaUpdate, db: Session = Depends(get_db)):
    return categoria_controller.actualizar_categoria(db, categoria_id, datos)

@router.delete("/{categoria_id}")
def eliminar_categoria(categoria_id: int, db: Session = Depends(get_db)):
    return categoria_controller.eliminar_categoria(db, categoria_id)
