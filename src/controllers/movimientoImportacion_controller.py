# src/controllers/movimientoImportacion_controller.py

from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from src.models.movimiento_importacion import MovimientoImportacion
from src.models.alerta import Alerta
from src.models.importacion import Importacion        
from src.models.empleado import Empleado    
from src.schemas.movimiento_importacion import (
    MovimientoImportacionCreate,
    MovimientoImportacionUpdate,
)
from src.schemas.movimiento_importacion import (
    MovimientoImportacionOut,
    MovimientoEstadoOut,
    
)
from src.utils.mailer import enviar_notificacion_movimiento
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
        admin = (
            db.query(Empleado)
            .filter(
                Empleado.rol.in_(["ADMIN", "Administrador"]),
                Empleado.estado == 1,
            )
            .first()
        )

        if admin:
            # 3.1 correo
            if admin.correo:
                enviar_notificacion_movimiento(
                    correo_admin=admin.correo,
                    codigo_importacion=codigo_importacion,
                    tipo_movimiento=nuevo.tipoMovimiento,
                    descripcion=nuevo.descripcion,
                    empleado_encargado=nombre_encargado,
                )

            # 3.2 alerta en BD
            mensaje_alerta = (
                f"Nuevo movimiento {nuevo.tipoMovimiento} en importación "
                f"{codigo_importacion} (encargado: {nombre_encargado or 'N/D'})."
            )

            alerta = Alerta(
                tipo="MOV_IMPORTACION",
                mensaje=mensaje_alerta,
                empleadoId=admin.id,       # 👈 aquí se guarda el 1 (Carlos)
                fecha=datetime.utcnow(),
            )
            db.add(alerta)
            db.commit()

            print("✅ Alerta de movimiento creada para empleadoId =", admin.id)
        else:
            print("⚠️ No se encontró administrador activo para crear alerta.")

    except Exception as e:
        # No romper el flujo si falla
        print(f"❌ Error al procesar notificación/alerta de movimiento: {e}")

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
