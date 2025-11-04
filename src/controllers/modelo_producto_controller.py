from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.models.modelo_producto import ModeloProducto
from src.schemas.modelo_producto import ModeloProductoCreate, ModeloProductoUpdate
from src.models.producto import Producto         # <- si tu modelo se llama distinto, cámbialo
from src.models.seccion import Seccion 
# Crear modelo
def crear_modelo(db: Session, modelo: ModeloProductoCreate):
    existente = db.query(ModeloProducto).filter(
        ModeloProducto.nombreModelo == modelo.nombreModelo,
        ModeloProducto.estado == 1
    ).first()

    if existente:
        raise HTTPException(status_code=400, detail="Ya existe un modelo activo con ese nombre.")

    nuevo = ModeloProducto(**modelo.dict())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

# Listar modelos activos
def listar_modelos(db: Session):
    return db.query(ModeloProducto).filter(ModeloProducto.estado == 1).all()

# Obtener modelo por ID
def obtener_modelo(db: Session, modelo_id: int):
    modelo = db.query(ModeloProducto).filter(
        ModeloProducto.id == modelo_id,
        ModeloProducto.estado == 1
    ).first()
    if not modelo:
        raise HTTPException(status_code=404, detail="Modelo no encontrado o inactivo")
    return modelo

# Actualizar modelo
def actualizar_modelo(db: Session, modelo_id: int, datos: ModeloProductoUpdate):
    modelo = db.query(ModeloProducto).filter(
        ModeloProducto.id == modelo_id,
        ModeloProducto.estado == 1
    ).first()
    if not modelo:
        raise HTTPException(status_code=404, detail="Modelo no encontrado o inactivo")

    if datos.nombreModelo:
        duplicado = db.query(ModeloProducto).filter(
            ModeloProducto.nombreModelo == datos.nombreModelo,
            ModeloProducto.id != modelo_id,
            ModeloProducto.estado == 1
        ).first()
        if duplicado:
            raise HTTPException(status_code=400, detail="Ya existe otro modelo activo con ese nombre.")

    for key, value in datos.dict(exclude_unset=True).items():
        setattr(modelo, key, value)

    db.commit()
    db.refresh(modelo)
    return modelo


# Eliminación lógica
def eliminar_modelo(db: Session, modelo_id: int):
    modelo = db.query(ModeloProducto).filter(
        ModeloProducto.id == modelo_id,
        ModeloProducto.estado == 1
    ).first()
    if not modelo:
        raise HTTPException(status_code=404, detail="Modelo no encontrado o ya eliminado")

    # 🔎 1) validar productos activos que usen este modelo
    productos_activos = db.query(Producto).filter(
        Producto.modeloId == modelo_id,     # cambia al nombre real de tu FK
        Producto.estado == 1                # o .activo == 1 según tu tabla
    ).count()

    if productos_activos > 0:
        raise HTTPException(
            status_code=400,
            detail=f"No se puede eliminar el modelo porque tiene {productos_activos} producto(s) activos vinculados."
        )

    # 🔎 2) validar secciones activas que usen este modelo
    secciones_activas = db.query(Seccion).filter(
        Seccion.modeloId == modelo_id,      # cambia al nombre real
        Seccion.estado == 1                 # o .activo == 1
    ).count()

    if secciones_activas > 0:
        raise HTTPException(
            status_code=400,
            detail=f"No se puede eliminar el modelo porque tiene {secciones_activas} sección(es) activas vinculadas."
        )

    # ✅ si no hay dependencias, eliminación lógica
    modelo.estado = 0
    db.commit()
    return {"mensaje": "Modelo eliminado correctamente (lógicamente)"}