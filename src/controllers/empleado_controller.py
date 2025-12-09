from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.models.empleado import Empleado
from src.schemas.empleado import EmpleadoCreate, EmpleadoUpdate
from src.utils.security import md5_hash
from src.utils.mailer import enviar_credenciales


def crear_empleado(db: Session, empleado: EmpleadoCreate):
    # Normalizamos strings
    nombre = (empleado.nombre or "").strip()
    apellido = (empleado.apellido or "").strip()
    segundo_apellido = (empleado.segundoApellido or "").strip() if empleado.segundoApellido else None
    ci = (empleado.ci or "").strip()
    telefono = (empleado.telefono or "").strip()
    rol = (empleado.rol or "").strip()
    usuario = (empleado.usuario or "").strip()
    correo = (empleado.correo or "").strip() if empleado.correo else None
    # 👇 urlImagen puede venir del endpoint de upload
    url_imagen = (empleado.urlImagen or "").strip() if empleado.urlImagen else None
    # 👇 sucursal (puedes decidir si obligatoria o no)
    id_sucursal = empleado.idSucursal

    # Validaciones básicas
    if not nombre or not apellido or not ci or not telefono or not rol or not usuario:
        raise HTTPException(status_code=400, detail="Faltan datos obligatorios del empleado.")

    # 👉 Si quieres que idSucursal sea OBLIGATORIO al crear:
    if id_sucursal is None:
        raise HTTPException(status_code=400, detail="La sucursal es obligatoria para el empleado.")

    if not empleado.contrasena:
        raise HTTPException(status_code=400, detail="La contraseña es obligatoria.")

    # 🔎 CI único (entre empleados activos)
    existente_ci = db.query(Empleado).filter(
        Empleado.ci == ci,
        Empleado.estado == 1
    ).first()
    if existente_ci:
        raise HTTPException(
            status_code=400,
            detail="Ya existe un empleado activo con ese CI."
        )

    # 🔎 Usuario único
    existente_usuario = db.query(Empleado).filter(
        Empleado.usuario == usuario,
        Empleado.estado == 1
    ).first()
    if existente_usuario:
        raise HTTPException(
            status_code=400,
            detail="Ya existe un empleado activo con ese usuario."
        )

    # 🔎 Correo único (si viene)
    if correo:
        existente_correo = db.query(Empleado).filter(
            Empleado.correo == correo,
            Empleado.estado == 1
        ).first()
        if existente_correo:
            raise HTTPException(
                status_code=400,
                detail="Ya existe un empleado activo con ese correo."
            )

    # ✅ Antes de crear, intentamos enviar el correo
    password_plano = empleado.contrasena

    if correo:
        enviado = enviar_credenciales(correo, usuario, password_plano)
        if not enviado:
            # si falla el envío, NO creamos el empleado
            raise HTTPException(
                status_code=500,
                detail="No se pudo enviar el correo de credenciales. Verifique la configuración de correo."
            )

    # Armamos dict desde Pydantic v2
    empleado_dict = empleado.model_dump()
    empleado_dict["nombre"] = nombre
    empleado_dict["apellido"] = apellido
    empleado_dict["segundoApellido"] = segundo_apellido
    empleado_dict["ci"] = ci
    empleado_dict["telefono"] = telefono
    empleado_dict["rol"] = rol
    empleado_dict["usuario"] = usuario
    empleado_dict["correo"] = correo
    empleado_dict["urlImagen"] = url_imagen
    empleado_dict["idSucursal"] = id_sucursal

    # 🔐 Hasheamos contraseña
    empleado_dict["contrasena"] = md5_hash(password_plano)

    nuevo = Empleado(**empleado_dict)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    return nuevo


def listar_empleados(db: Session):
    return db.query(Empleado).filter(Empleado.estado == 1).all()


def obtener_empleado_por_id(db: Session, empleado_id: int):
    empleado = db.query(Empleado).filter(
        Empleado.id == empleado_id,
        Empleado.estado == 1
    ).first()
    return empleado


def eliminar_empleado(db: Session, empleado_id: int):
    # Eliminación lógica solo si está activo
    empleado = db.query(Empleado).filter(
        Empleado.id == empleado_id,
        Empleado.estado == 1
    ).first()

    if not empleado:
        return False

    empleado.estado = 0
    db.commit()
    db.refresh(empleado)
    return True


def actualizar_empleado(db: Session, empleado_id: int, datos: EmpleadoUpdate):
    empleado = db.query(Empleado).filter(
        Empleado.id == empleado_id,
        Empleado.estado == 1
    ).first()

    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado o inactivo")

    # Sacamos payload parcial
    update_data = datos.model_dump(exclude_unset=True)

    # Normalizamos posibles nuevos valores
    nuevo_ci = (update_data.get("ci") or empleado.ci or "").strip()
    nuevo_usuario = (update_data.get("usuario") or empleado.usuario or "").strip()
    nuevo_correo = (update_data.get("correo") or empleado.correo or "").strip() if (update_data.get("correo") or empleado.correo) else None

    # Si viene urlImagen, la normalizamos
    if "urlImagen" in update_data:
        url_imagen = update_data.get("urlImagen")
        update_data["urlImagen"] = url_imagen.strip() if url_imagen else None

    # Si viene idSucursal, podrías validar algo extra si quisieras
    # (por ejemplo, que exista la sucursal), pero eso ya depende de tu lógica.

    # 🔎 Validar CI duplicado si cambia
    if "ci" in update_data:
        duplicado_ci = db.query(Empleado).filter(
            Empleado.ci == nuevo_ci,
            Empleado.id != empleado_id,
            Empleado.estado == 1
        ).first()
        if duplicado_ci:
            raise HTTPException(
                status_code=400,
                detail="Otro empleado activo ya tiene ese CI."
            )

    # 🔎 Validar usuario duplicado si cambia
    if "usuario" in update_data:
        duplicado_usuario = db.query(Empleado).filter(
            Empleado.usuario == nuevo_usuario,
            Empleado.id != empleado_id,
            Empleado.estado == 1
        ).first()
        if duplicado_usuario:
            raise HTTPException(
                status_code=400,
                detail="Otro empleado activo ya tiene ese usuario."
            )

    # 🔎 Validar correo duplicado si cambia y no es vacío
    if "correo" in update_data and nuevo_correo:
        duplicado_correo = db.query(Empleado).filter(
            Empleado.correo == nuevo_correo,
            Empleado.id != empleado_id,
            Empleado.estado == 1
        ).first()
        if duplicado_correo:
            raise HTTPException(
                status_code=400,
                detail="Otro empleado activo ya tiene ese correo."
            )

    # 🔐 Si viene contraseña nueva → hashear
    if "contrasena" in update_data:
        if update_data["contrasena"]:
            update_data["contrasena"] = md5_hash(update_data["contrasena"])
        else:
            # si viene vacía, no tocar la actual
            update_data.pop("contrasena")

    # Asignamos campos
    for key, value in update_data.items():
        setattr(empleado, key, value)

    db.commit()
    db.refresh(empleado)
    return empleado
