from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.models.cliente import Cliente
from src.schemas.cliente import ClienteCreate, ClienteUpdate

# Crear cliente
def crear_cliente(db: Session, cliente: ClienteCreate):
    existente = db.query(Cliente).filter(
        ((Cliente.correo == cliente.correo) | (Cliente.ci == cliente.ci)) & (Cliente.estado == 1)
    ).first()
    if existente:
        raise HTTPException(status_code=400, detail="Ya existe un cliente activo con ese correo o CI.")

    nuevo = Cliente(**cliente.dict())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

# Listar todos los clientes activos
def listar_clientes(db: Session):
    return db.query(Cliente).filter(Cliente.estado == 1).all()

# Obtener cliente por ID (solo activos)
def obtener_cliente(db: Session, cliente_id: int):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id, Cliente.estado == 1).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado o inactivo")
    return cliente

# Actualizar datos
def actualizar_cliente(db: Session, cliente_id: int, datos: ClienteUpdate):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id, Cliente.estado == 1).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado o inactivo")

    if datos.correo:
        duplicado = db.query(Cliente).filter(
            Cliente.correo == datos.correo, Cliente.id != cliente_id, Cliente.estado == 1
        ).first()
        if duplicado:
            raise HTTPException(status_code=400, detail="Correo ya registrado por otro cliente activo.")

    for key, value in datos.dict(exclude_unset=True).items():
        setattr(cliente, key, value)

    db.commit()
    db.refresh(cliente)
    return cliente

# Eliminación lógica
def eliminar_cliente(db: Session, cliente_id: int):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id, Cliente.estado == 1).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado o ya eliminado")

    cliente.estado = 0  # cambio lógico
    db.commit()
    return {"mensaje": "Cliente eliminado correctamente (lógicamente)"}
