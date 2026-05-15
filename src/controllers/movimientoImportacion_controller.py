# src/controllers/movimientoImportacion_controller.py

from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from src.models.movimiento_importacion import MovimientoImportacion
from src.models.alerta import Alerta
from src.models.importacion import Importacion        
from src.models.empleado import Empleado    
from src.controllers.alerta_controller import (
    obtener_configuracion_alerta,
)
from src.schemas.movimiento_importacion import (
    MovimientoImportacionCreate,
    MovimientoImportacionUpdate,
)
from src.schemas.movimiento_importacion import (
    MovimientoImportacionOut,
    MovimientoEstadoOut,
    
)
from src.utils.mailer import (
    enviar_notificacion_movimiento,
    enviar_notificacion_importacion_concluida,
)
# 👇 mismo orden/códigos que en el front
PASOS = [
    {"code": "PEDIDO", "label": "Pedido confirmado"},
    {"code": "PRODUCCION", "label": "En producción"},
    {"code": "TRANS_INT", "label": "En tránsito internacional"},
    {"code": "PUERTO", "label": "Llegada a puerto"},
    {"code": "LISTO_ENV", "label": "Listo para envío"},
    {"code": "ADUANA_BO", "label": "Despacho aduanero Bolivia"},
    {"code": "TRANS_NAC", "label": "En tránsito nacional"},
    {"code": "ENTREGADO", "label": "Entregado"},
]

def verificar_y_concluir_importacion(db: Session, importacion_id: int):
    movimientos = listar_por_importacion(db, importacion_id)

    pasos_requeridos = {p["code"] for p in PASOS}
    pasos_registrados = {
        (m.tipoMovimiento or "").upper().strip()
        for m in movimientos
    }

    if not pasos_requeridos.issubset(pasos_registrados):
        return

    importacion = db.query(Importacion).filter(Importacion.id == importacion_id).first()

    if not importacion:
        return

    if int(importacion.estado or 0) == 2:
        return

    importacion.estado = 2
    db.commit()
    db.refresh(importacion)

    config = obtener_configuracion_alerta(db, "IMPORTACION_CONCLUIDA")

    if not config or not config["activo"]:
        print("ℹ️ Alerta IMPORTACION_CONCLUIDA desactivada por configuración.")
        return

    admins = (
        db.query(Empleado)
        .filter(
            Empleado.rol.in_(["ADMIN", "Administrador", "Adminnistrador"]),
            Empleado.estado == 1,
        )
        .all()
    )

    resumen = "\n".join([
        f"- {m.tipoMovimiento}: {m.descripcion or 'Sin descripción'}"
        for m in movimientos
    ])

    mensaje_alerta = (
        f"La importación {importacion.codigo} fue concluida correctamente."
    )

    for admin in admins:
        if config["enviarCorreo"] and admin.correo:
            enviar_notificacion_importacion_concluida(
                correo_admin=admin.correo,
                codigo_importacion=importacion.codigo,
                descripcion=importacion.descripcion,
                fecha_llegada=str(importacion.fechaLlegada),
                movimientos=resumen,
            )

        if config["crearNotificacion"]:
            alerta = Alerta(
                tipo="IMPORTACION_CONCLUIDA",
                mensaje=mensaje_alerta,
                empleadoId=admin.id,
            )
            db.add(alerta)

    db.commit()
    print("✅ Alertas IMPORTACION_CONCLUIDA procesadas según configuración.")

def crear_movimiento_importacion(
    db: Session,
    data: MovimientoImportacionCreate,
) -> MovimientoImportacion:
    nuevo = MovimientoImportacion(
        importacionId=data.importacionId,
        tipoMovimiento=(data.tipoMovimiento or "").upper().strip(),
        descripcion=data.descripcion,
        rutaArchivo=data.rutaArchivo,
        idEmpleadoEncargado=data.idEmpleadoEncargado,
    )

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    
    # ────────────── 🔔 Notificación por correo + ALERTA ──────────────
    try:
        # 1) Importación (para el código)
        importacion = (
            db.query(Importacion)
            .filter(Importacion.id == data.importacionId)
            .first()
        )
        codigo_importacion = (
            importacion.codigo if importacion and importacion.codigo else str(data.importacionId)
        )

        # 2) Empleado encargado (para el mensaje)
        empleado_encargado = (
            db.query(Empleado)
            .filter(Empleado.id == data.idEmpleadoEncargado)
            .first()
        )
        nombre_encargado = (
            f"{empleado_encargado.nombre} {empleado_encargado.apellido}"
            if empleado_encargado
            else None
        )

        # 3) Admin activo (en tu caso Carlos)
        config = obtener_configuracion_alerta(db, "MOV_IMPORTACION")

        if not config or not config["activo"]:
            print("ℹ️ Alerta MOV_IMPORTACION desactivada por configuración.")
        else:
            admins = (
                db.query(Empleado)
                .filter(
                    Empleado.rol.in_(["ADMIN", "Administrador", "Adminnistrador"]),
                    Empleado.estado == 1,
                )
                .all()
            )

            mensaje_alerta = (
                f"Nuevo movimiento {nuevo.tipoMovimiento} en importación "
                f"{codigo_importacion} (encargado: {nombre_encargado or 'N/D'})."
            )

            for admin in admins:
                if config["enviarCorreo"] and admin.correo:
                    enviar_notificacion_movimiento(
                        correo_admin=admin.correo,
                        codigo_importacion=codigo_importacion,
                        tipo_movimiento=nuevo.tipoMovimiento,
                        descripcion=nuevo.descripcion,
                        empleado_encargado=nombre_encargado,
                    )

                if config["crearNotificacion"]:
                    alerta = Alerta(
                        tipo="MOV_IMPORTACION",
                        mensaje=mensaje_alerta,
                        empleadoId=admin.id,
                    )
                    db.add(alerta)

            db.commit()
            print("✅ Alertas MOV_IMPORTACION procesadas según configuración.")
    except Exception as e:
        # No romper el flujo si falla
        print(f"❌ Error al procesar notificación/alerta de movimiento: {e}")
    verificar_y_concluir_importacion(db, data.importacionId)

    return nuevo


# 📍 Listar TODOS los movimientos
def listar_movimientos_importacion(db: Session) -> List[MovimientoImportacion]:
    return db.query(MovimientoImportacion).all()


# 📍 Obtener movimiento por ID
def obtener_movimiento_importacion(
    db: Session,
    movimiento_id: int,
) -> MovimientoImportacion:
    movimiento = db.query(MovimientoImportacion).filter_by(id=movimiento_id).first()
    if not movimiento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movimiento de importación no encontrado",
        )
    return movimiento


# 📍 Actualizar movimiento
def actualizar_movimiento_importacion(
    db: Session,
    movimiento_id: int,
    data: MovimientoImportacionUpdate,
) -> MovimientoImportacion:
    movimiento = db.query(MovimientoImportacion).filter_by(id=movimiento_id).first()
    if not movimiento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movimiento de importación no encontrado",
        )

    update_data = data.dict(exclude_unset=True)

    # si viene tipoMovimiento, también lo normalizamos a MAYÚSCULAS
    if "tipoMovimiento" in update_data and update_data["tipoMovimiento"] is not None:
        update_data["tipoMovimiento"] = (
            update_data["tipoMovimiento"].upper().strip()
        )

    for field, value in update_data.items():
        setattr(movimiento, field, value)

    db.commit()
    db.refresh(movimiento)
    verificar_y_concluir_importacion(db, movimiento.importacionId)
    return movimiento


# 📍 Eliminar movimiento
def eliminar_movimiento_importacion(
    db: Session,
    movimiento_id: int,
) -> None:
    movimiento = db.query(MovimientoImportacion).filter_by(id=movimiento_id).first()
    if not movimiento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movimiento de importación no encontrado",
        )

    db.delete(movimiento)
    db.commit()


# 📍 Listar movimientos de UNA importación
def listar_por_importacion(
    db: Session,
    importacion_id: int,
) -> List[MovimientoImportacion]:
    """
    Devuelve todos los movimientos de una importación concreta,
    ordenados por fechaRegistro ASC.
    """
    return (
        db.query(MovimientoImportacion)
        .filter(MovimientoImportacion.importacionId == importacion_id)
        .order_by(MovimientoImportacion.fechaRegistro.asc())
        .all()
    )


# 📍 Obtener "estado" de los movimientos de una importación
def obtener_estado_movimientos(
    db: Session,
    importacion_id: int,
) -> List[MovimientoEstadoOut]:
    """
    Devuelve para CADA PASO:
      - code (ej: PEDIDO)
      - label (ej: Pedido confirmado)
      - completado: True/False
      - movimiento: datos del movimiento si existe, o None

    Esto es lo que usa el front para pintar los círculos en verde/rojo
    y mostrar detalle cuando hacen click.
    """
    # 1) Traemos todos los movimientos de esa importación
    movimientos = listar_por_importacion(db, importacion_id)

    # 2) Conjunto de tipos presentes, en MAYÚSCULAS
    tipos_presentes = {
        (m.tipoMovimiento or "").upper() for m in movimientos
    }

    resultado: List[MovimientoEstadoOut] = []

    for paso in PASOS:
        code = paso["code"]
        label = paso["label"]
        completado = code in tipos_presentes

        movimiento_out = None
        if completado:
            # buscamos el movimiento correspondiente a ese tipo
            mov = next(
                (m for m in movimientos if (m.tipoMovimiento or "").upper() == code),
                None,
            )
            if mov is not None:
                movimiento_out = MovimientoImportacionOut.from_orm(mov)

        resultado.append(
            MovimientoEstadoOut(
                code=code,
                label=label,
                completado=completado,
                movimiento=movimiento_out,
            )
        )

    return resultado
