from fastapi import APIRouter, Depends, Query
from typing import Optional
from sqlalchemy.orm import Session
from typing import List
from src.config.db import SessionLocal
from src.schemas.proveedor import ProveedorCreate, ProveedorUpdate, ProveedorResponse
from src.controllers import proveedor_controller

router = APIRouter(prefix="/proveedores", tags=["Proveedores"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=ProveedorResponse)
def crear_proveedor(proveedor: ProveedorCreate, db: Session = Depends(get_db)):
    return proveedor_controller.crear_proveedor(db, proveedor)

#@router.get("/", response_model=List[ProveedorResponse])
#def listar_proveedores(db: Session = Depends(get_db)):
#    return proveedor_controller.listar_proveedores(db)

@router.get("/")
def listar_proveedores(
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1),
    db: Session = Depends(get_db)
):
    return proveedor_controller.listar_proveedores(db, search, page, pageSize)

@router.get("/{proveedor_id}", response_model=ProveedorResponse)
def obtener_proveedor(proveedor_id: int, db: Session = Depends(get_db)):
    return proveedor_controller.obtener_proveedor(db, proveedor_id)

@router.put("/{proveedor_id}", response_model=ProveedorResponse)
def actualizar_proveedor(proveedor_id: int, datos: ProveedorUpdate, db: Session = Depends(get_db)):
    return proveedor_controller.actualizar_proveedor(db, proveedor_id, datos)

@router.delete("/{proveedor_id}")
def eliminar_proveedor(proveedor_id: int, db: Session = Depends(get_db)):
    return proveedor_controller.eliminar_proveedor(db, proveedor_id)
