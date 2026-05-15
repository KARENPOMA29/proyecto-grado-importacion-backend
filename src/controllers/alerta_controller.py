# src/controllers/alerta_controller.py
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text

from src.models.alerta import Alerta
from src.models.empleado import Empleado
from src.schemas.alerta import AlertaCreate


def crear_alerta(db: Session, data: AlertaCreate) -> Alerta:
    nueva = Alerta(
        tipo=data.tipo,
        mensaje=data.mensaje,
        empleadoId=data.empleadoId,
        fecha=datetime.now(),
        estado=data.estado if data.estado is not None else 1,
    )

    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva


def marcar_leida(db: Session, alerta_id: int) -> Alerta | None:
    alerta = db.query(Alerta).filter(Alerta.id == alerta_id).first()
    if not alerta:
        return None

    alerta.estado = 0
    db.commit()
    db.refresh(alerta)
    return alerta


# ============================================================
# CONFIGURACIÓN DE ALERTAS
# ============================================================

def obtener_configuracion_alerta(db: Session, tipo_alerta: str):
    """
    Lee la configuración desde la tabla ConfiguracionAlerta.
    Ejemplo tipo_alerta:
    - MOV_IMPORTACION
    - IMPORTACION_CONCLUIDA
    - STOCK_BAJO
    """
    result = db.execute(
        text("""
            SELECT TOP 1
                id,
                tipoAlerta,
                activo,
                enviarCorreo,
                crearNotificacion,
                prioridad,
                frecuenciaMinutos,
                destinatariosRol
            FROM ConfiguracionAlerta
            WHERE tipoAlerta = :tipoAlerta
        """),
        {"tipoAlerta": tipo_alerta}
    ).first()

    return dict(result._mapping) if result else None


def obtener_administradores_activos(db: Session, rol_destino: str | None = None):
    """
    Obtiene empleados administradores activos.
    Se acepta ADMIN, Administrador y Adminnistrador por seguridad.
    """
    roles = ["ADMIN", "Administrador", "Adminnistrador"]

    if rol_destino and rol_destino not in roles:
        roles.append(rol_destino)

    return (
        db.query(Empleado)
        .filter(
            Empleado.rol.in_(roles),
            Empleado.estado == 1,
        )
        .all()
    )


def crear_alerta_directa(
    db: Session,
    tipo: str,
    mensaje: str,
    empleado_id: int,
) -> Alerta:
    """
    Crea alerta interna sin depender del schema.
    Esto nos sirve para movimientos, stock bajo, importación concluida, etc.
    """
    alerta = Alerta(
        tipo=tipo,
        mensaje=mensaje,
        empleadoId=empleado_id,
        fecha=datetime.now(),
        estado=1,
    )

    db.add(alerta)
    db.commit()
    db.refresh(alerta)
    return alerta


# ============================================================
# ALERTAS DE STOCK BAJO
# ============================================================

def verificar_stock_bajo(db: Session):
    config = obtener_configuracion_alerta(db, "STOCK_BAJO")

    if not config or not config["activo"]:
        print("ℹ️ Alerta STOCK_BAJO desactivada por configuración.")
        return {
            "ok": True,
            "mensaje": "Alerta STOCK_BAJO desactivada.",
            "alertasCreadas": 0,
        }

    productos_bajos = db.execute(
        text("""
            SELECT
                ciudadId,
                ciudad,
                sucursalId,
                sucursal,
                almacenId,
                almacen,
                modeloId,
                nombreModelo,
                cantidad,
                stockMinimo,
                estadoStock
            FROM vw_reporte_stock_actual
            WHERE estadoStock = 'Stock Bajo'
        """)
    ).fetchall()

    if not productos_bajos:
        print("✅ No hay productos con stock bajo.")
        return {
            "ok": True,
            "mensaje": "No hay productos con stock bajo.",
            "alertasCreadas": 0,
        }

    admins = obtener_administradores_activos(
        db,
        config.get("destinatariosRol")
    )

    alertas_creadas = 0

    for row in productos_bajos:
        item = dict(row._mapping)

        referencia = (
            f"STOCK_BAJO-"
            f"{item['ciudadId']}-"
            f"{item['sucursalId']}-"
            f"{item['almacenId']}-"
            f"{item['modeloId']}"
        )

        mensaje = (
            f"Stock bajo detectado: {item['nombreModelo']} | "
            f"Ciudad: {item['ciudad'] or 'N/D'} | "
            f"Sucursal: {item['sucursal'] or 'N/D'} | "
            f"Almacén: {item['almacen'] or 'N/D'} | "
            f"Stock actual: {item['cantidad']} | "
            f"Stock mínimo: {item['stockMinimo']}."
        )

        for admin in admins:
            # Evitar duplicados activos
            existe = db.query(Alerta).filter(
                Alerta.tipo == "STOCK_BAJO",
                Alerta.referencia == referencia,
                Alerta.empleadoId == admin.id,
                Alerta.estado == 1,
            ).first()

            if existe:
                continue

            if config["crearNotificacion"]:
                alerta = Alerta(
                    tipo="STOCK_BAJO",
                    referencia=referencia,
                    mensaje=mensaje,
                    empleadoId=admin.id,
                    fecha=datetime.now(),
                    estado=1,
                )
                db.add(alerta)
                alertas_creadas += 1

            if config["enviarCorreo"] and admin.correo:
                # Por ahora solo usamos correo simple si ya tienes función propia.
                # Si tienes enviar_alerta_stock en mailer.py, lo conectamos después.
                print(f"📧 Stock bajo para enviar a {admin.correo}: {mensaje}")

    db.commit()

    print(f"✅ Alertas STOCK_BAJO creadas: {alertas_creadas}")

    return {
        "ok": True,
        "mensaje": "Verificación de stock bajo completada.",
        "alertasCreadas": alertas_creadas,
    }