from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from src.config.db import SessionLocal
from src.schemas.cliente import ClienteCreate, ClienteUpdate, ClienteResponse
from src.controllers import cliente_controller

router = APIRouter(prefix="/clientes", tags=["Clientes"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=ClienteResponse)
def crear_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    return cliente_controller.crear_cliente(db, cliente)


#@router.get("/", response_model=List[ClienteResponse])
#def listar_clientes(db: Session = Depends(get_db)):
#    return cliente_controller.listar_clientes(db)
@router.get("/")
def listar_clientes(
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1),
    db: Session = Depends(get_db)
):
    return cliente_controller.listar_clientes(db, search, page, pageSize)


@router.get("/{cliente_id}", response_model=ClienteResponse)
def obtener_cliente(cliente_id: int, db: Session = Depends(get_db)):
    return cliente_controller.obtener_cliente(db, cliente_id)


@router.put("/{cliente_id}", response_model=ClienteResponse)
def actualizar_cliente(cliente_id: int, datos: ClienteUpdate, db: Session = Depends(get_db)):
    return cliente_controller.actualizar_cliente(db, cliente_id, datos)


@router.delete("/{cliente_id}")
def eliminar_cliente(cliente_id: int, db: Session = Depends(get_db)):
    return cliente_controller.eliminar_cliente(db, cliente_id)
