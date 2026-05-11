from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from typing import Optional, List
from sqlalchemy.orm import Session
from src.config.db import SessionLocal
from src.controllers import empleado_controller
from uuid import uuid4
import os
from pathlib import Path
from src.schemas.empleado import EmpleadoCreate, EmpleadoResponse, EmpleadoUpdate, ImagenEmpleadoResponse
from src.config.paths import EMPLEADOS_DIR
    
router = APIRouter(prefix="/empleados", tags=["Empleados"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/upload-imagen", response_model=ImagenEmpleadoResponse)
async def upload_imagen_empleado(file: UploadFile = File(...)):
    ext_permitidas = {"jpg", "jpeg", "png", "webp"}
    nombre_original = file.filename or ""
    ext = nombre_original.rsplit(".", 1)[-1].lower()

    if ext not in ext_permitidas:
        raise HTTPException(status_code=400, detail="Formato de imagen no permitido.")

    EMPLEADOS_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid4().hex}.{ext}"
    file_path = EMPLEADOS_DIR / filename

    contenido = await file.read()
    with open(file_path, "wb") as f:
        f.write(contenido)

    url = f"/archivos/empleados/{filename}"
    return ImagenEmpleadoResponse(urlImagen=url)

# 📍 Crear un nuevo empleado
@router.post("/", response_model=EmpleadoResponse)
def crear_empleado(empleado: EmpleadoCreate, db: Session = Depends(get_db)):
    return empleado_controller.crear_empleado(db, empleado)

# 📍 Listar empleados
#@router.get("/", response_model=List[EmpleadoResponse])
#def listar_empleados(db: Session = Depends(get_db)):
#    return empleado_controller.listar_empleados(db)

@router.get("/")
def listar_empleados(
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1),
    db: Session = Depends(get_db)
):
    return empleado_controller.listar_empleados(db, search, page, pageSize)

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