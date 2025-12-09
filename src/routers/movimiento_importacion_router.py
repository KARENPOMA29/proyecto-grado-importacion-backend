# src/routers/movimiento_importacion_router.py

from typing import List, Optional
from datetime import datetime
from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    status,
    UploadFile,
    File,
    Form,
    HTTPException,
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from src.config.db import SessionLocal
from src.config.paths import MOVIMIENTOS_IMPORTACION_DIR, ARCHIVOS_DIR
from src.controllers import movimientoImportacion_controller
from src.schemas.movimiento_importacion import (
    MovimientoImportacionCreate,
    MovimientoImportacionUpdate,
    MovimientoImportacionOut,
    MovimientoEstadoOut,
)

router = APIRouter(
    prefix="/movimientos-importacion",
    tags=["Movimientos de Importación"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------- CREAR (YA CON ARCHIVO) ----------
@router.post(
    "/",
    response_model=MovimientoImportacionOut,
    status_code=status.HTTP_201_CREATED,
)
async def crear_movimiento_importacion(
    importacionId: int = Form(...),
    tipoMovimiento: str = Form(...),
    descripcion: Optional[str] = Form(None),
    idEmpleadoEncargado: int = Form(...),
    archivo: UploadFile | None = File(None),
    db: Session = Depends(get_db),
):
    ruta_archivo_relativa: Optional[str] = None

    if archivo:
        ext = Path(archivo.filename).suffix or ""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        nombre_archivo = f"mov_{importacionId}_{timestamp}{ext}"
        ruta_fisica = MOVIMIENTOS_IMPORTACION_DIR / nombre_archivo

        contenido = await archivo.read()
        with open(ruta_fisica, "wb") as f:
            f.write(contenido)

        # -> se sirve como /archivos/movimientosimportacion/...
        ruta_archivo_relativa = f"movimientosimportacion/{nombre_archivo}"

    data = MovimientoImportacionCreate(
        importacionId=importacionId,
        tipoMovimiento=tipoMovimiento,
        descripcion=descripcion,
        rutaArchivo=ruta_archivo_relativa,
        idEmpleadoEncargado=idEmpleadoEncargado,
    )

    return movimientoImportacion_controller.crear_movimiento_importacion(db, data)


# ---------- LISTAR / OBTENER (SIN CAMBIOS) ----------
@router.get("/", response_model=List[MovimientoImportacionOut])
def listar_movimientos_importacion(db: Session = Depends(get_db)):
    return movimientoImportacion_controller.listar_movimientos_importacion(db)


@router.get(
    "/importacion/{importacion_id}",
    response_model=List[MovimientoImportacionOut],
)
def listar_movimientos_por_importacion(
    importacion_id: int,
    db: Session = Depends(get_db),
):
    return movimientoImportacion_controller.listar_por_importacion(db, importacion_id)


@router.get(
    "/estado/{importacion_id}",
    response_model=List[MovimientoEstadoOut],
)
def obtener_estado_movimientos(
    importacion_id: int,
    db: Session = Depends(get_db),
):
    return movimientoImportacion_controller.obtener_estado_movimientos(
        db, importacion_id
    )


@router.get("/{movimiento_id}", response_model=MovimientoImportacionOut)
def obtener_movimiento_importacion(
    movimiento_id: int,
    db: Session = Depends(get_db),
):
    return movimientoImportacion_controller.obtener_movimiento_importacion(
        db, movimiento_id
    )


# ---------- ⬆️ ACTUALIZAR CON ARCHIVO ----------
@router.put("/{movimiento_id}", response_model=MovimientoImportacionOut)
async def actualizar_movimiento_importacion(
    movimiento_id: int,
    importacionId: int = Form(...),
    tipoMovimiento: str = Form(...),
    descripcion: Optional[str] = Form(None),
    idEmpleadoEncargado: int = Form(...),
    archivo: UploadFile | None = File(None),
    db: Session = Depends(get_db),
):
    # traemos el movimiento actual para conservar rutaArchivo si no se manda archivo nuevo
    existente = movimientoImportacion_controller.obtener_movimiento_importacion(
        db, movimiento_id
    )
    if not existente:
        raise HTTPException(status_code=404, detail="Movimiento no encontrado")

    ruta_archivo_relativa: Optional[str] = existente.rutaArchivo

    if archivo:
        ext = Path(archivo.filename).suffix or ""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        nombre_archivo = f"mov_{importacionId}_{timestamp}{ext}"
        ruta_fisica = MOVIMIENTOS_IMPORTACION_DIR / nombre_archivo

        contenido = await archivo.read()
        with open(ruta_fisica, "wb") as f:
            f.write(contenido)

        ruta_archivo_relativa = f"movimientosimportacion/{nombre_archivo}"
        # opcional: podrías borrar el archivo anterior si quieres

    data = MovimientoImportacionUpdate(
        importacionId=importacionId,
        tipoMovimiento=tipoMovimiento,
        descripcion=descripcion,
        rutaArchivo=ruta_archivo_relativa,
        idEmpleadoEncargado=idEmpleadoEncargado,
    )

    return movimientoImportacion_controller.actualizar_movimiento_importacion(
        db, movimiento_id, data
    )


# ---------- 📥 OBTENER EL ARCHIVO DEL MOVIMIENTO ----------
@router.get("/{movimiento_id}/archivo")
def descargar_archivo_movimiento(
    movimiento_id: int,
    db: Session = Depends(get_db),
):
    movimiento = movimientoImportacion_controller.obtener_movimiento_importacion(
        db, movimiento_id
    )
    if not movimiento or not movimiento.rutaArchivo:
        raise HTTPException(
            status_code=404, detail="Movimiento sin archivo asociado"
        )

    ruta_relativa = Path(movimiento.rutaArchivo)  # ej: movimientosimportacion/xxx.pdf
    ruta_fisica = ARCHIVOS_DIR / ruta_relativa

    if not ruta_fisica.is_file():
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    return FileResponse(
        path=ruta_fisica,
        filename=ruta_relativa.name,
        media_type="application/octet-stream",
    )


# DELETE igual que antes
@router.delete("/{movimiento_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_movimiento_importacion(
    movimiento_id: int,
    db: Session = Depends(get_db),
):
    movimientoImportacion_controller.eliminar_movimiento_importacion(db, movimiento_id)
    return {"message": "Movimiento eliminado correctamente"}
