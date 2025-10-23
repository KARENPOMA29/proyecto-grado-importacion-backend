from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from src.config.db import SessionLocal
from src.controllers import empleado_controller
from src.schemas.empleado import EmpleadoCreate, EmpleadoResponse, EmpleadoUpdate

router = APIRouter(prefix="/empleados", tags=["Empleados"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 📍 Crear un nuevo empleado
@router.post("/", response_model=EmpleadoResponse)
def crear_empleado(empleado: EmpleadoCreate, db: Session = Depends(get_db)):
    return empleado_controller.crear_empleado(db, empleado)

# 📍 Listar empleados
@router.get("/", response_model=List[EmpleadoResponse])
def listar_empleados(db: Session = Depends(get_db)):
    return empleado_controller.listar_empleados(db)

# 📍 Obtener empleado por ID
@router.get("/{empleado_id}", response_model=EmpleadoResponse)
def obtener_empleado(empleado_id: int, db: Session = Depends(get_db)):
    empleado = empleado_controller.obtener_empleado_por_id(db, empleado_id)
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return empleado

# 📍 Eliminar empleado
@router.delete("/{empleado_id}")
def eliminar_empleado(empleado_id: int, db: Session = Depends(get_db)):
    ok = empleado_controller.eliminar_empleado(db, empleado_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return {"mensaje": "Empleado marcado como inactivo ✅"}

@router.put("/{empleado_id}", response_model=EmpleadoResponse)
def actualizar_empleado(empleado_id: int, datos: EmpleadoUpdate, db: Session = Depends(get_db)):
    return empleado_controller.actualizar_empleado(db, empleado_id, datos)