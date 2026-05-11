import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SMTP_USER = os.getenv("SMTP_USER", "karencitarosaura8@gmail.com")
SMTP_PASS = os.getenv("SMTP_PASS", "qpxlqdazhcaeyoia")  # sin espacios
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))


def _enviar_correo(destinatario: str, asunto: str, cuerpo: str) -> bool:
    if os.getenv("TESTING") == "1":
        print(f"[TESTING] No se envía correo real. Destino: {destinatario}")
        print(cuerpo)
        return True

    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = destinatario
    msg["Subject"] = asunto
    msg.attach(MIMEText(cuerpo, "plain", "utf-8"))

    try:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=30) as server:
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)

        print(f"✅ Correo enviado correctamente a {destinatario}")
        return True

    except Exception as e:
        print(f"❌ Error enviando correo a {destinatario}: {e}")
        return False
def enviar_credenciales(destino: str, usuario: str, password_plano: str) -> bool:
    asunto = "IMPORT SYSTEM - Credenciales de acceso"
    cuerpo = f"""
    Hola,

    Se creó o restableció tu cuenta en el sistema IMPORT SYSTEM.    

    Usuario: {usuario}
    Contraseña: {password_plano}

    Por seguridad, cambia tu contraseña cuando ingreses.

    Saludos,
    El equipo de IMPORT SYSTEM.
    """
    return _enviar_correo(destino, asunto, cuerpo.strip())


def enviar_alerta_stock(
    correo_admin: str,
    modelo_nombre: str,
    stock_actual: int,
    stock_minimo: int,
) -> bool:
    asunto = "⚠️ Alerta de Stock Bajo"
    cuerpo = f"""
    Estimado Administrador,

    Se ha detectado un modelo con stock bajo en el sistema:

    📦 Modelo: {modelo_nombre}
    📉 Stock actual: {stock_actual}
    🔻 Stock mínimo recomendado: {stock_minimo}

    Por favor, revise el inventario y considere realizar una reposición.

    Saludos,
    Sistema de Gestión de Importaciones
    """
    return _enviar_correo(correo_admin, asunto, cuerpo.strip())


def enviar_notificacion_movimiento(
    correo_admin: str,
    codigo_importacion: str,
    tipo_movimiento: str,
    descripcion: str | None,
    empleado_encargado: str | None,
) -> bool:
    """Notifica al admin que se registró un movimiento en una importación."""
    asunto = f"IMPORT SYSTEM - Nuevo movimiento en importación {codigo_importacion}"

    cuerpo = f"""
    Estimado Administrador,

    Se ha registrado un nuevo movimiento para la importación {codigo_importacion}.

    ➤ Tipo de movimiento: {tipo_movimiento}
    ➤ Descripción: {descripcion or 'Sin descripción'}
    ➤ Empleado encargado: {empleado_encargado or 'N/D'}

    Saludos,
    Sistema de Gestión de Importaciones
    """

    return _enviar_correo(correo_admin, asunto, cuerpo.strip())

def enviar_notificacion_importacion_concluida(
    correo_admin,
    codigo_importacion,
    descripcion,
    fecha_llegada,
    movimientos,
):
    asunto = f"IMPORT SYSTEM - Importación concluida: {codigo_importacion}"

    cuerpo = f"""
Estimado Administrador,

La importación {codigo_importacion} ha concluido correctamente.

DATOS DE LA IMPORTACIÓN
Código: {codigo_importacion}
Descripción: {descripcion or 'Sin descripción'}
Fecha de llegada: {fecha_llegada or 'No registrada'}
Estado: Concluida

MOVIMIENTOS REGISTRADOS
{movimientos}

El sistema cambió automáticamente el estado de la importación a CONCLUIDA.

Saludos,
Sistema de Gestión de Importaciones
"""

    return _enviar_correo(
        destinatario=correo_admin,
        asunto=asunto,
        cuerpo=cuerpo.strip(),
    )