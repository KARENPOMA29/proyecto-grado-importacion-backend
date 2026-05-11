import shutil
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from typing import Optional
from pathlib import Path

from src.config.db import SessionLocal
from src.config.paths import MODELOS_PRODUCTOS_DIR  
from src.schemas.modelo_producto import (
    ModeloProductoCreate,
    ModeloProductoUpdate,
    ModeloProductoResponse,
)
from src.controllers import modelo_producto_controller

router = APIRouter(prefix="/modelos", tags=["Modelos de Producto"])


# 🔧 dependencia de BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 📸 SUBIR IMAGEN de modelo de producto
@router.post("/upload-imagen", include_in_schema=False)
async def subir_imagen_modelo(file: UploadFile = File(...)):
    """
    Guarda la imagen del modelo de producto dentro de /Archivos/modelos_productos
    y devuelve la ruta relativa que se almacena en la BD.
    """
    try:
        filename = file.filename.replace(" ", "_")
        destino = MODELOS_PRODUCTOS_DIR / filename

        with open(destino, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Retornamos la ruta RELATIVA que se guarda en BD
        return {
            "filename": filename,
            "urlImagen": f"/archivos/modelos_productos/{filename}",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir imagen: {str(e)}")


# 📍 Crear modelo
@router.post("/", response_model=ModeloProductoResponse)
def crear_modelo(modelo: ModeloProductoCreate, db: Session = Depends(get_db)):
    return modelo_producto_controller.crear_modelo(db, modelo)


# 📍 Listar modelos activos
#@router.get("/", response_model=List[ModeloProductoResponse])
#def listar_modelos(db: Session = Depends(get_db)):
#    return modelo_producto_controller.listar_modelos(db)
@router.get("/")
def listar_modelos(
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1),
    db: Session = Depends(get_db),
):
    return modelo_producto_controller.listar_modelos(
        db=db,
        search=search,
        page=page,
        pageSize=pageSize,
    )

# 📍 Obtener modelo por ID
@router.get("/{modelo_id}", response_model=ModeloProductoResponse)
def obtener_modelo(modelo_id: int, db: Session = Depends(get_db)):
    return modelo_producto_controller.obtener_modelo(db, modelo_id)


# 📍 Actualizar modelo
@router.put("/{modelo_id}", response_model=ModeloProductoResponse)
def actualizar_modelo(
    modelo_id: int,
    datos: ModeloProductoUpdate,
    db: Session = Depends(get_db),
):
    return modelo_producto_controller.actualizar_modelo(db, modelo_id, datos)


# 📍 Eliminación lógica
@router.delete("/{modelo_id}")
def eliminar_modelo(modelo_id: int, db: Session = Depends(get_db)):
    return modelo_producto_controller.eliminar_modelo(db, modelo_id)
