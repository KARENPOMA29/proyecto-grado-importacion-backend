# src/controllers/alerta_controller.py
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text
from src.utils.mailer import _enviar_correo
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

    referencias_actuales = set()
    productos = []

    for row in productos_bajos:
        item = dict(row._mapping)

        referencia = (
            f"STOCK_BAJO-"
            f"{item['ciudadId']}-"
            f"{item['sucursalId']}-"
            f"{item['almacenId']}-"
            f"{item['modeloId']}"
        )

        item["referencia"] = referencia
        referencias_actuales.add(referencia)
        productos.append(item)

    # Cierra automáticamente las alertas que ya no están en stock bajo
    query = db.query(Alerta).filter(
        Alerta.tipo == "STOCK_BAJO",
        Alerta.estado == 1,
    )

    if referencias_actuales:
        alertas_cerradas = query.filter(
            ~Alerta.referencia.in_(referencias_actuales)
        ).update({Alerta.estado: 0}, synchronize_session=False)
    else:
        alertas_cerradas = query.update(
            {Alerta.estado: 0},
            synchronize_session=False
        )

    if not config or not config["activo"]:
        db.commit()
        return {
            "ok": True,
            "mensaje": "STOCK_BAJO desactivado. Alertas cerradas.",
            "alertasCreadas": 0,
            "alertasCerradas": alertas_cerradas,
        }

    admins = obtener_administradores_activos(db, config.get("destinatariosRol"))

    alertas_creadas = 0

    for item in productos:
        mensaje = (
            f"Stock bajo detectado: {item['nombreModelo']} | "
            f"Ciudad: {item['ciudad'] or 'N/D'} | "
            f"Sucursal: {item['sucursal'] or 'N/D'} | "
            f"Almacén: {item['almacen'] or 'N/D'} | "
            f"Stock actual: {item['cantidad']} | "
            f"Stock mínimo: {item['stockMinimo']}."
        )

        for admin in admins:
            # Busca cualquier alerta existente, activa o cerrada
            existe = db.query(Alerta).filter(
                Alerta.tipo == "STOCK_BAJO",
                Alerta.referencia == item["referencia"],
                Alerta.empleadoId == admin.id,
            ).first()

            if existe:
                # Si sigue en stock bajo, la mantiene activa y actualiza mensaje/fecha
                existe.estado = 1
                existe.mensaje = mensaje
                existe.fecha = datetime.now()
                continue

            alerta = Alerta(
                tipo="STOCK_BAJO",
                referencia=item["referencia"],
                mensaje=mensaje,
                empleadoId=admin.id,
                fecha=datetime.now(),
                estado=1,
            )
            db.add(alerta)
            alertas_creadas += 1

    db.commit()

    return {
        "ok": True,
        "mensaje": "Verificación de stock bajo completada.",
        "alertasCreadas": alertas_creadas,
        "alertasCerradas": alertas_cerradas,
    }


# ============================================================
# ENVIAR RESUMEN STOCK BAJO POR CORREO
# ============================================================

def enviar_resumen_stock_bajo_correo(db: Session):
    alertas = db.query(Alerta).filter(
        Alerta.tipo == "STOCK_BAJO",
        Alerta.estado == 1,
    ).all()

    if not alertas:
        return {
            "ok": True,
            "mensaje": "No hay alertas de stock bajo para enviar.",
            "enviados": 0,
        }

    admins = obtener_administradores_activos(db)

    asunto = "IMPORT SYSTEM - Resumen de stock bajo"

    cuerpo = "Estimado Administrador,\n\n"
    cuerpo += "Actualmente existen los siguientes productos con stock bajo:\n\n"

    for alerta in alertas:
        cuerpo += f"- {alerta.mensaje}\n"

    cuerpo += "\nPor favor, revise el inventario.\n\n"
    cuerpo += "Saludos,\nSistema de Gestión de Importaciones"

    enviados = 0
    correos_enviados = set()

    for admin in admins:

        if not admin.correo:
            continue

        correo = admin.correo.strip().lower()

        # evita duplicados
        if correo in correos_enviados:
            continue

        ok = _enviar_correo(
            destinatario=correo,
            asunto=asunto,
            cuerpo=cuerpo,
        )

        if ok:
            enviados += 1
            correos_enviados.add(correo)

    return {
        "ok": True,
        "mensaje": "Resumen de stock bajo enviado al correo.",
        "enviados": enviados,
    }
