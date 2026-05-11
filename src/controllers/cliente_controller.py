from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.models.cliente import Cliente
from src.schemas.cliente import ClienteCreate, ClienteUpdate
from src.models.venta import Venta
from sqlalchemy import or_

# Crear cliente
def crear_cliente(db: Session, cliente: ClienteCreate):
    # Normalizamos un poco por si vienen con espacios
    razon = (cliente.razonSocial or "").strip()
    nit = (cliente.nit or "").strip()
    correo = (cliente.correo or "").strip()
    telefono = (cliente.telefono or "").strip()

    if not razon:
        raise HTTPException(status_code=400, detail="La razón social es obligatoria.")
    if not nit:
        raise HTTPException(status_code=400, detail="El NIT es obligatorio.")

    # 1) Validar NIT duplicado
    existente_nit = db.query(Cliente).filter(
        Cliente.nit == nit,
        Cliente.estado == 1
    ).first()
    if existente_nit:
        raise HTTPException(
            status_code=400,
            detail="Ya existe un cliente activo con ese NIT."
        )

    # 2) Validar razón social duplicada
    existente_razon = db.query(Cliente).filter(
        Cliente.razonSocial == razon,
        Cliente.estado == 1
    ).first()
    if existente_razon:
        raise HTTPException(
            status_code=400,
            detail="Ya existe un cliente activo con esa razón social."
        )

    # 3) Validar correo duplicado
    existente_correo = db.query(Cliente).filter(
        Cliente.correo == correo,
        Cliente.estado == 1
    ).first()
    if existente_correo:
        raise HTTPException(
            status_code=400,
            detail="Ya existe un cliente activo con ese correo."
        )

    nuevo = Cliente(
        razonSocial=razon,
        nit=nit,
        correo=correo,
        telefono=telefono
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


# Listar todos los clientes activos
#def listar_clientes(db: Session):
#   return db.query(Cliente).filter(Cliente.estado == 1).all()


def listar_clientes(db: Session, search: str = None, page: int = 1, pageSize: int = 10):
    query = db.query(Cliente).filter(Cliente.estado == 1)

    if search:
        texto = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Cliente.razonSocial.ilike(texto),
                Cliente.nit.ilike(texto),
                Cliente.correo.ilike(texto),
                Cliente.telefono.ilike(texto),
            )
        )

    total = query.count()

    items = (
        query
        .order_by(Cliente.razonSocial.asc())
        .offset((page - 1) * pageSize)
        .limit(pageSize)
        .all()
    )

    return {
        "items": items,
        "total": total
    }

# Obtener cliente por ID (solo activos)
def obtener_cliente(db: Session, cliente_id: int):
    cliente = db.query(Cliente).filter(
        Cliente.id == cliente_id,
        Cliente.estado == 1
    ).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado o inactivo")
    return cliente


# Actualizar datos
def actualizar_cliente(db: Session, cliente_id: int, datos: ClienteUpdate):
    cliente = db.query(Cliente).filter(
        Cliente.id == cliente_id,
        Cliente.estado == 1
    ).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado o inactivo")

    # Sacamos lo que viene en el payload
    payload = datos.model_dump(exclude_unset=True)

    # Normalizamos campos nuevos (si vienen)
    if "razonSocial" in payload and payload["razonSocial"] is not None:
        nueva_razon = (payload["razonSocial"] or "").strip()
    else:
        nueva_razon = (cliente.razonSocial or "").strip()

    nuevo_nit = payload.get("nit", cliente.nit)
    nuevo_correo = payload.get("correo", cliente.correo)

    # 1) Validar NIT duplicado (en otro cliente activo)
    if nuevo_nit:
        duplicado_nit = db.query(Cliente).filter(
            Cliente.nit == nuevo_nit,
            Cliente.id != cliente_id,
            Cliente.estado == 1
        ).first()
        if duplicado_nit:
            raise HTTPException(
                status_code=400,
                detail="NIT ya registrado por otro cliente activo."
            )

    # 2) Validar correo duplicado (en otro cliente activo)
    if nuevo_correo:
        duplicado_correo = db.query(Cliente).filter(
            Cliente.correo == nuevo_correo,
            Cliente.id != cliente_id,
            Cliente.estado == 1
        ).first()
        if duplicado_correo:
            raise HTTPException(
                status_code=400,
                detail="Correo ya registrado por otro cliente activo."
            )

    # 3) Validar razón social duplicada (en otro cliente activo)
    if nueva_razon:
        duplicado_razon = db.query(Cliente).filter(
            Cliente.razonSocial == nueva_razon,
            Cliente.id != cliente_id,
            Cliente.estado == 1
        ).first()
        if duplicado_razon:
            raise HTTPException(
                status_code=400,
                detail="Ya existe otro cliente activo con esa razón social."
            )

    # Actualizamos el payload normalizado
    if "razonSocial" in payload:
        payload["razonSocial"] = nueva_razon

    # ✅ Si todo OK, actualizamos
    for key, value in payload.items():
        setattr(cliente, key, value)

    db.commit()
    db.refresh(cliente)
    return cliente


# Eliminación lógica
def eliminar_cliente(db: Session, cliente_id: int):
    # Buscar cliente activo
    cliente = db.query(Cliente).filter(
        Cliente.id == cliente_id,
        Cliente.estado == 1
    ).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado o ya eliminado")

    # ⚠️ Verificar si tiene ventas activas
    ventas_activas = db.query(Venta).filter(
        Venta.clienteId == cliente_id,
        Venta.estado == 1  # Ajusta al campo real de tu modelo Venta
    ).count()

    if ventas_activas > 0:
        raise HTTPException(
            status_code=400,
            detail=f"No se puede eliminar el cliente porque tiene {ventas_activas} ventas activas."
        )

    # ✅ Eliminación lógica si no tiene ventas activas
    cliente.estado = 0
    db.commit()

    return {"mensaje": "Cliente eliminado correctamente (lógicamente)"}
