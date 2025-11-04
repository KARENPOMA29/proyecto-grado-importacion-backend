from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.models.cliente import Cliente
from src.schemas.cliente import ClienteCreate, ClienteUpdate
from src.models.venta import Venta
# Crear cliente

def crear_cliente(db: Session, cliente: ClienteCreate):
    # normalizamos un poco por si vienen con espacios
    nombre = (cliente.nombre or "").strip()
    apellido = (cliente.apellido or "").strip()

    # 1) validar correo/ci duplicado
    existente = db.query(Cliente).filter(
        (
            (Cliente.correo == cliente.correo) |
            (Cliente.ci == cliente.ci)
        ) &
        (Cliente.estado == 1)
    ).first()
    if existente:
        raise HTTPException(
            status_code=400,
            detail="Ya existe un cliente activo con ese correo o CI."
        )

    # 2) validar nombre + apellido duplicado
    if nombre and apellido:
      mismo_nombre = db.query(Cliente).filter(
          Cliente.nombre == nombre,
          Cliente.apellido == apellido,
          Cliente.segundoApellido == cliente.segundoApellido,
          Cliente.estado == 1
      ).first()
      if mismo_nombre:
          raise HTTPException(
              status_code=400,
              detail="Ya existe un cliente activo con el mismo nombre y apellidos."
          )

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
    cliente = db.query(Cliente).filter(
        Cliente.id == cliente_id,
        Cliente.estado == 1
    ).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado o inactivo")

    # vamos a sacar lo que viene
    payload = datos.dict(exclude_unset=True)

    nuevo_correo = payload.get("correo")
    nuevo_ci = payload.get("ci")
    nuevo_nombre = (payload.get("nombre") or cliente.nombre or "").strip()
    nuevo_apellido = (payload.get("apellido") or cliente.apellido or "").strip()

    # 1) validar correo duplicado (en otro cliente activo)
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

    # 2) validar CI duplicado (en otro cliente activo)
    if nuevo_ci:
        duplicado_ci = db.query(Cliente).filter(
            Cliente.ci == nuevo_ci,
            Cliente.id != cliente_id,
            Cliente.estado == 1
        ).first()
        if duplicado_ci:
            raise HTTPException(
                status_code=400,
                detail="CI ya registrado por otro cliente activo."
            )

    # 3) validar nombre + apellido duplicado (en otro cliente activo)
    if nuevo_nombre and nuevo_apellido:
        duplicado_nombre = db.query(Cliente).filter(
            Cliente.nombre == nuevo_nombre,
            Cliente.apellido == nuevo_apellido,
            Cliente.segundoApellido == cliente.segundoApellido,
            Cliente.id != cliente_id,
            Cliente.estado == 1
        ).first()
        if duplicado_nombre:
            raise HTTPException(
                status_code=400,
                detail="Ya existe otro cliente activo con el mismo nombre y apellidos."
            )

    # ✅ si todo OK, actualizamos
    for key, value in payload.items():
        setattr(cliente, key, value)

    db.commit()
    db.refresh(cliente)
    return cliente

# Eliminación lógica

def eliminar_cliente(db: Session, cliente_id: int):
    # Buscar cliente activo
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id, Cliente.estado == 1).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado o ya eliminado")

    # ⚠️ Verificar si tiene ventas activas
    ventas_activas = db.query(Venta).filter(
        Venta.clienteId == cliente_id,
        Venta.estado == 1  # o Venta.activo == 1 según tu modelo
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
