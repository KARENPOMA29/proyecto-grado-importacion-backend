from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload
from src.models.modelo_producto import ModeloProducto
from src.models.producto import Producto
from src.models.seccion import Seccion
from src.models.alerta import Alerta
from src.models.marca import Marca
from src.schemas.modelo_producto import ModeloProductoCreate, ModeloProductoUpdate


def _evaluar_alerta_stock(db: Session, modelo: ModeloProducto):
    stock_actual = modelo.stockActual or 0
    stock_minimo = getattr(modelo, "stockMinimo", 0) or 0

    if stock_actual > stock_minimo:
        return

    mensaje = (
        f"El modelo '{modelo.nombreModelo}' tiene stock bajo "
        f"({stock_actual}) (mínimo recomendado: {stock_minimo})."
    )

    alerta = Alerta(
        tipo="STOCK_BAJO",
        mensaje=mensaje,
        empleadoId=None,
        fecha=datetime.utcnow(),
    )

    db.add(alerta)
    db.commit()
    db.refresh(alerta)
    return alerta


# 📍 Crear modelo
def crear_modelo(db: Session, modelo: ModeloProductoCreate):
    existente = (
        db.query(ModeloProducto)
        .filter(
            ModeloProducto.nombreModelo == modelo.nombreModelo,
            ModeloProducto.estado == 1,
        )
        .first()
    )

    if existente:
        raise HTTPException(
            status_code=400,
            detail="Ya existe un modelo activo con ese nombre.",
        )

    # Validar marca si viene idMarca
    if modelo.idMarca is not None:
        marca = db.query(Marca).filter(Marca.id == modelo.idMarca).first()
        if not marca:
            raise HTTPException(status_code=400, detail="La marca indicada no existe.")

    data = modelo.model_dump()
    data["stockActual"] = data.get("stockActual") or 0

    nuevo = ModeloProducto(**data)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


# 📍 Listar modelos activos
def listar_modelos(db: Session):
    return (
        db.query(ModeloProducto)
        .options(joinedload(ModeloProducto.marca))  # 👈 importante
        .filter(ModeloProducto.estado == 1)
        .all()
    )


# 📍 Obtener modelo por ID
def obtener_modelo(db: Session, modelo_id: int):
    modelo = (
        db.query(ModeloProducto)
        .options(joinedload(ModeloProducto.marca))  # 👈 también aquí
        .filter(
            ModeloProducto.id == modelo_id,
            ModeloProducto.estado == 1,
        )
        .first()
    )

    if not modelo:
        raise HTTPException(status_code=404, detail="Modelo no encontrado o inactivo")

    return modelo

# 📍 Actualizar modelo
def actualizar_modelo(db: Session, modelo_id: int, datos: ModeloProductoUpdate):
    modelo = (
        db.query(ModeloProducto)
        .filter(
            ModeloProducto.id == modelo_id,
            ModeloProducto.estado == 1,
        )
        .first()
    )

    if not modelo:
        raise HTTPException(status_code=404, detail="Modelo no encontrado o inactivo")

    update_data = datos.model_dump(exclude_unset=True)

    # Validar duplicado si cambia el nombre
    nuevo_nombre = update_data.get("nombreModelo")
    if nuevo_nombre:
        duplicado = (
            db.query(ModeloProducto)
            .filter(
                ModeloProducto.nombreModelo == nuevo_nombre,
                ModeloProducto.id != modelo_id,
                ModeloProducto.estado == 1,
            )
            .first()
        )
        if duplicado:
            raise HTTPException(
                status_code=400,
                detail="Ya existe otro modelo activo con ese nombre.",
            )

    # Validar marca si se cambia idMarca
    if "idMarca" in update_data and update_data["idMarca"] is not None:
        marca = db.query(Marca).filter(Marca.id == update_data["idMarca"]).first()
        if not marca:
            raise HTTPException(status_code=400, detail="La nueva marca no existe.")

    for key, value in update_data.items():
        setattr(modelo, key, value)

    db.commit()
    db.refresh(modelo)
    return modelo


# 📍 Eliminación lógica con validación
def eliminar_modelo(db: Session, modelo_id: int):
    modelo = (
        db.query(ModeloProducto)
        .filter(
            ModeloProducto.id == modelo_id,
            ModeloProducto.estado == 1,
        )
        .first()
    )

    if not modelo:
        raise HTTPException(
            status_code=404, detail="Modelo no encontrado o ya eliminado"
        )

    productos_activos = (
        db.query(Producto)
        .filter(Producto.modeloId == modelo_id, Producto.estado == 1)
        .count()
    )

    if productos_activos > 0:
        raise HTTPException(
            status_code=400,
            detail=f"No se puede eliminar: hay {productos_activos} producto(s) vinculados.",
        )

    secciones_activas = (
        db.query(Seccion)
        .filter(Seccion.modeloId == modelo_id, Seccion.estado == 1)
        .count()
    )

    if secciones_activas > 0:
        raise HTTPException(
            status_code=400,
            detail=f"No se puede eliminar: hay {secciones_activas} sección(es) vinculadas.",
        )

    modelo.estado = 0
    db.commit()
    return {"mensaje": "Modelo eliminado correctamente (lógicamente)"}
