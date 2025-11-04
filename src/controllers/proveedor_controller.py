from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.models.proveedor import Proveedor
from src.schemas.proveedor import ProveedorCreate, ProveedorUpdate
from src.models.importacion import Importacion

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
    proveedor = db.query(Proveedor).filter(
        Proveedor.id == proveedor_id,
        Proveedor.estado == 1
    ).first()
    if not proveedor:
      raise HTTPException(status_code=404, detail="Proveedor no encontrado o inactivo")

    payload = datos.dict(exclude_unset=True)

    # 👀 si quiere cambiar la razón social, validamos que no exista en otro activo
    nueva_razon = payload.get("razonSocial")
    if nueva_razon:
        duplicado = db.query(Proveedor).filter(
            Proveedor.razonSocial == nueva_razon,
            Proveedor.id != proveedor_id,     # 👈 excluimos al mismo
            Proveedor.estado == 1
        ).first()
        if duplicado:
            raise HTTPException(
                status_code=400,
                detail="Ya existe otro proveedor activo con esa razón social."
            )

    # ✅ aplicar cambios
    for key, value in payload.items():
        setattr(proveedor, key, value)

    db.commit()
    db.refresh(proveedor)
    return proveedor


# Eliminación lógica
def eliminar_proveedor(db: Session, proveedor_id: int):
    proveedor = db.query(Proveedor).filter(Proveedor.id == proveedor_id, Proveedor.estado == 1).first()
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado o ya eliminado")

    # ⚠️ validar si tiene importaciones activas
    importaciones_activas = db.query(Importacion).filter(
        Importacion.proveedorId == proveedor_id,
        # usa el campo que tengas: estado == "En aduana"/"En tránsito" o activo == 1
        # si en tu tabla usas "activo" como en el JSON que me pasaste:
        Importacion.activo == 1
    ).count()

    if importaciones_activas > 0:
        raise HTTPException(
            status_code=400,
            detail=f"No se puede eliminar el proveedor porque tiene {importaciones_activas} importación(es) activa(s)."
        )

    proveedor.estado = 0
    db.commit()
    return {"mensaje": "Proveedor eliminado correctamente (lógicamente)"}