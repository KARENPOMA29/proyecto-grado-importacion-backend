from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.models.seccion import Seccion
from src.models.almacen import Almacen
from src.models.modelo_producto import ModeloProducto
from src.schemas.seccion import SeccionCreate, SeccionUpdate

# Crear sección
def crear_seccion(db: Session, seccion: SeccionCreate):
    # Validar que el almacén esté activo
    almacen = db.query(Almacen).filter(Almacen.id == seccion.almacenId, Almacen.estado == 1).first()
    if not almacen:
        raise HTTPException(status_code=400, detail="El almacén no existe o está inactivo.")

    # Validar que el modelo esté activo
    modelo = db.query(ModeloProducto).filter(ModeloProducto.id == seccion.modeloId, ModeloProducto.estado == 1).first()
    if not modelo:
        raise HTTPException(status_code=400, detail="El modelo no existe o está inactivo.")

    # Evitar duplicados activos (misma descripción dentro del mismo almacén y modelo)
    duplicado = db.query(Seccion).filter(
        Seccion.descripcion == seccion.descripcion,
        Seccion.almacenId == seccion.almacenId,
        Seccion.modeloId == seccion.modeloId,
        Seccion.estado == 1
    ).first()

    if duplicado:
        raise HTTPException(status_code=400, detail="Ya existe una sección activa con esa descripción en este almacén y modelo.")

    nueva = Seccion(**seccion.dict())
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva


# Listar secciones activas
def listar_secciones(db: Session):
    return db.query(Seccion).filter(Seccion.estado == 1).all()


# Obtener por ID
def obtener_seccion(db: Session, seccion_id: int):
    seccion = db.query(Seccion).filter(Seccion.id == seccion_id, Seccion.estado == 1).first()
    if not seccion:
        raise HTTPException(status_code=404, detail="Sección no encontrada o inactiva")
    return seccion


# Actualizar sección
def actualizar_seccion(db: Session, seccion_id: int, datos: SeccionUpdate):
    seccion = db.query(Seccion).filter(Seccion.id == seccion_id, Seccion.estado == 1).first()
    if not seccion:
        raise HTTPException(status_code=404, detail="Sección no encontrada o inactiva")

    # Validar almacén si se cambia
    if datos.almacenId is not None:
        almacen = db.query(Almacen).filter(Almacen.id == datos.almacenId, Almacen.estado == 1).first()
        if not almacen:
            raise HTTPException(status_code=400, detail="El almacén no existe o está inactivo.")

    # Validar modelo si se cambia
    if datos.modeloId is not None:
        modelo = db.query(ModeloProducto).filter(ModeloProducto.id == datos.modeloId, ModeloProducto.estado == 1).first()
        if not modelo:
            raise HTTPException(status_code=400, detail="El modelo no existe o está inactivo.")

    # Validar duplicado (solo si se cambia la descripción o los IDs)
    cambios = datos.dict(exclude_unset=True)
    nueva_desc = cambios.get("descripcion", seccion.descripcion)
    nuevo_almacen = cambios.get("almacenId", seccion.almacenId)
    nuevo_modelo = cambios.get("modeloId", seccion.modeloId)

    duplicado = db.query(Seccion).filter(
        Seccion.descripcion == nueva_desc,
        Seccion.almacenId == nuevo_almacen,
        Seccion.modeloId == nuevo_modelo,
        Seccion.id != seccion_id,
        Seccion.estado == 1
    ).first()

    if duplicado:
        raise HTTPException(status_code=400, detail="Ya existe otra sección activa con esa descripción en este almacén y modelo.")

    # Aplicar cambios
    for key, value in cambios.items():
        setattr(seccion, key, value)

    db.commit()
    db.refresh(seccion)
    return seccion


# Eliminación lógica
def eliminar_seccion(db: Session, seccion_id: int):
    seccion = db.query(Seccion).filter(Seccion.id == seccion_id, Seccion.estado == 1).first()
    if not seccion:
        raise HTTPException(status_code=404, detail="Sección no encontrada o ya eliminada")

    seccion.estado = 0
    db.commit()
    return {"mensaje": "Sección eliminada correctamente (lógicamente)"}
