# src/utils/mailer.py
import smtplib
from email.mime.text import MIMEText

SMTP_USER = "foxbolivia.fbol@gmail.com"
SMTP_PASS = "qjuqxebmjhvcvtmr"
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587

def enviar_credenciales(destino: str, usuario: str, password_plano: str):
    asunto = "FOX BOLIVIA - Credenciales de acceso"
    cuerpo = (
        f"Hola,\n\n"
        f"Se creó o restableció tu cuenta en el sistema FOX BOLIVIA.\n\n"
        f"Usuario: {usuario}\n"
        f"Contraseña: {password_plano}\n\n"
        f"Por seguridad, cambia tu contraseña cuando ingreses.\n"
        f"Saludos."
    )

    msg = MIMEText(cuerpo, "plain", "utf-8")
    msg["Subject"] = asunto
    msg["From"] = SMTP_USER
    msg["To"] = destino

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, [destino], msg.as_string())
