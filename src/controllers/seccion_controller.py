# src/controllers/seccion_controller.py
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.models.seccion import Seccion
from src.models.almacen import Almacen
from src.models.modelo_producto import ModeloProducto
from src.schemas.seccion import SeccionCreate, SeccionUpdate
from src.models.movimiento_inventario import MovimientoInventario
from src.models.producto import Producto
from sqlalchemy import text
# Crear sección
def crear_seccion(db: Session, seccion: SeccionCreate):
    # Validar que el almacén esté activo
    almacen = db.query(Almacen).filter(
        Almacen.id == seccion.almacenId,
        Almacen.estado == 1
    ).first()
    if not almacen:
        raise HTTPException(status_code=400, detail="El almacén no existe o está inactivo.")

    # Validar que el modelo esté activo
    modelo = db.query(ModeloProducto).filter(
        ModeloProducto.id == seccion.modeloId,
        ModeloProducto.estado == 1
    ).first()
    if not modelo:
        raise HTTPException(status_code=400, detail="El modelo no existe o está inactivo.")

    # ❗ No permitir mismo NOMBRE en el mismo almacén (independiente del modelo)
    if seccion.nombre:
        duplicado = db.query(Seccion).filter(
            Seccion.nombre == seccion.nombre,
            Seccion.almacenId == seccion.almacenId,
            Seccion.estado == 1
        ).first()
        if duplicado:
            raise HTTPException(
                status_code=400,
                detail="Ya existe una sección activa con ese nombre en este almacén."
            )

    nueva = Seccion(**seccion.dict())
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva


# Obtener por ID
def obtener_seccion(db: Session, seccion_id: int):
    seccion = db.query(Seccion).filter(
        Seccion.id == seccion_id,
        Seccion.estado == 1
    ).first()
    if not seccion:
        raise HTTPException(status_code=404, detail="Sección no encontrada o inactiva")
    return seccion


# Actualizar sección
def actualizar_seccion(db: Session, seccion_id: int, datos: SeccionUpdate):
    seccion = db.query(Seccion).filter(
        Seccion.id == seccion_id,
        Seccion.estado == 1
    ).first()
    if not seccion:
        raise HTTPException(status_code=404, detail="Sección no encontrada o inactiva")

    cambios = datos.dict(exclude_unset=True)

    # Validar almacén si se cambia
    if "almacenId" in cambios:
        almacen = db.query(Almacen).filter(
            Almacen.id == cambios["almacenId"],
            Almacen.estado == 1
        ).first()
        if not almacen:
            raise HTTPException(status_code=400, detail="El almacén no existe o está inactivo.")

    # Validar modelo si se cambia
    if "modeloId" in cambios:
        modelo = db.query(ModeloProducto).filter(
            ModeloProducto.id == cambios["modeloId"],
            ModeloProducto.estado == 1
        ).first()
        if not modelo:
            raise HTTPException(status_code=400, detail="El modelo no existe o está inactivo.")

    # ❗ Validar duplicado por nombre + almacen
    nuevo_nombre = cambios.get("nombre", seccion.nombre)
    nuevo_almacen = cambios.get("almacenId", seccion.almacenId)

    if nuevo_nombre:
        duplicado = db.query(Seccion).filter(
            Seccion.nombre == nuevo_nombre,
            Seccion.almacenId == nuevo_almacen,
            Seccion.id != seccion_id,
            Seccion.estado == 1
        ).first()
        if duplicado:
            raise HTTPException(
                status_code=400,
                detail="Ya existe otra sección activa con ese nombre en este almacén."
            )

    # Aplicar cambios
    for key, value in cambios.items():
        setattr(seccion, key, value)

    db.commit()
    db.refresh(seccion)
    return seccion


# Eliminación lógica (mantengo simple, tu regla de modelos activos va en el controlador del Modelo)
def eliminar_seccion(db: Session, seccion_id: int):
    seccion = db.query(Seccion).filter(
        Seccion.id == seccion_id,
        Seccion.estado == 1
    ).first()

    if not seccion:
        raise HTTPException(
            status_code=404,
            detail="Sección no encontrada o ya eliminada"
        )

    stock = db.execute(
        text("""
            SELECT cantidad
            FROM vw_stock_por_sucursal_almacen_modelo
            WHERE almacenId = :almacenId
              AND modeloId = :modeloId
        """),
        {
            "almacenId": seccion.almacenId,
            "modeloId": seccion.modeloId,
        }
    ).mappings().first()

    cantidad = stock["cantidad"] if stock else 0

    if cantidad > 0:
        raise HTTPException(
            status_code=400,
            detail=f"No se puede eliminar la sección porque tiene stock disponible ({cantidad} unidades)."
        )

    seccion.estado = 0
    db.commit()

    return {"mensaje": "Sección eliminada correctamente"}

# Listar secciones (con join a almacén y modelo) y filtrado por almacén
def listar_secciones(
    db: Session,
    almacen_id: Optional[int] = None,
    search: Optional[str] = None,
    page: int = 1,
    pageSize: int = 10
):
    query = (
        db.query(
            Seccion,
            Almacen.nombre.label("almacenNombre"),
            ModeloProducto.nombreModelo.label("modeloNombre"),
        )
        .join(Almacen, Seccion.almacenId == Almacen.id)
        .join(ModeloProducto, Seccion.modeloId == ModeloProducto.id)
        .filter(Seccion.estado == 1)
    )

    if almacen_id is not None:
        query = query.filter(Seccion.almacenId == almacen_id)

    if search and search.strip():
        texto = f"%{search.strip()}%"
        query = query.filter(
            (Seccion.nombre.ilike(texto)) |
            (Seccion.descripcion.ilike(texto)) |
            (Almacen.nombre.ilike(texto)) |
            (ModeloProducto.nombreModelo.ilike(texto))
        )

    total = query.count()

    rows = (
        query
        .order_by(Seccion.id.desc())
        .offset((page - 1) * pageSize)
        .limit(pageSize)
        .all()
    )

    items = []
    for sec, alm_nombre, mod_nombre in rows:
        items.append({
            "id": sec.id,
            "nombre": sec.nombre,
            "almacenId": sec.almacenId,
            "modeloId": sec.modeloId,
            "descripcion": sec.descripcion,
            "fechaRegistro": sec.fechaRegistro,
            "estado": sec.estado,
            "almacenNombre": alm_nombre,
            "modeloNombre": mod_nombre,
        })

    return {
        "items": items,
        "total": total,
    }
