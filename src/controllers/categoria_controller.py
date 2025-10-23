from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.models.categoria import Categoria
from src.schemas.categoria import CategoriaCreate, CategoriaUpdate

# Crear categoría
def crear_categoria(db: Session, categoria: CategoriaCreate):
    existente = db.query(Categoria).filter(
        Categoria.nombre == categoria.nombre,
        Categoria.estado == 1
    ).first()

    if existente:
        raise HTTPException(status_code=400, detail="Ya existe una categoría activa con ese nombre.")

    nueva = Categoria(**categoria.dict())
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

# Listar categorías activas
def listar_categorias(db: Session):
    return db.query(Categoria).filter(Categoria.estado == 1).all()

# Obtener por ID
def obtener_categoria(db: Session, categoria_id: int):
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id, Categoria.estado == 1).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada o inactiva")
    return categoria

# Actualizar
def actualizar_categoria(db: Session, categoria_id: int, datos: CategoriaUpdate):
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id, Categoria.estado == 1).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada o inactiva")

    if datos.nombre:
        duplicado = db.query(Categoria).filter(
            Categoria.nombre == datos.nombre,
            Categoria.id != categoria_id,
            Categoria.estado == 1
        ).first()
        if duplicado:
            raise HTTPException(status_code=400, detail="Ya existe otra categoría activa con ese nombre.")

    for key, value in datos.dict(exclude_unset=True).items():
        setattr(categoria, key, value)

    db.commit()
    db.refresh(categoria)
    return categoria

# Eliminación lógica
def eliminar_categoria(db: Session, categoria_id: int):
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id, Categoria.estado == 1).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada o ya eliminada")

    categoria.estado = 0
    db.commit()
    return {"mensaje": "Categoría eliminada correctamente (lógicamente)"}
