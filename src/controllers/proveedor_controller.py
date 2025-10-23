from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.models.proveedor import Proveedor
from src.schemas.proveedor import ProveedorCreate, ProveedorUpdate

# Crear proveedor
def crear_proveedor(db: Session, proveedor: ProveedorCreate):
    existente = db.query(Proveedor).filter(
        (Proveedor.razonSocial == proveedor.razonSocial) & (Proveedor.estado == 1)
    ).first()

    if existente:
        raise HTTPException(status_code=400, detail="Ya existe un proveedor activo con esa razón social.")

    nuevo = Proveedor(**proveedor.dict())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

# Listar proveedores activos
def listar_proveedores(db: Session):
    return db.query(Proveedor).filter(Proveedor.estado == 1).all()

# Obtener proveedor por ID
def obtener_proveedor(db: Session, proveedor_id: int):
    proveedor = db.query(Proveedor).filter(Proveedor.id == proveedor_id, Proveedor.estado == 1).first()
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado o inactivo")
    return proveedor

# Actualizar proveedor
def actualizar_proveedor(db: Session, proveedor_id: int, datos: ProveedorUpdate):
    proveedor = db.query(Proveedor).filter(Proveedor.id == proveedor_id, Proveedor.estado == 1).first()
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado o inactivo")

    for key, value in datos.dict(exclude_unset=True).items():
        setattr(proveedor, key, value)

    db.commit()
    db.refresh(proveedor)
    return proveedor

# Eliminación lógica
def eliminar_proveedor(db: Session, proveedor_id: int):
    proveedor = db.query(Proveedor).filter(Proveedor.id == proveedor_id, Proveedor.estado == 1).first()
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado o ya eliminado")

    proveedor.estado = 0
    db.commit()
    return {"mensaje": "Proveedor eliminado correctamente (lógicamente)"}
