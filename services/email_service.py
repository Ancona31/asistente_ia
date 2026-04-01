import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from config import GMAIL_SENDER


def enviar_email(
    destinatario: str,
    asunto: str,
    cuerpo: str,
    adjunto_path: str | None = None,
) -> bool:
    """
    Envia un email via Gmail usando SMTP con App Password.
    Requiere habilitar 'App Passwords' en la cuenta de Google.
    La contrasena de aplicacion se lee de la variable de entorno GMAIL_APP_PASSWORD.
    """
    gmail_app_password = os.getenv("GMAIL_APP_PASSWORD")

    msg = MIMEMultipart()
    msg["From"] = GMAIL_SENDER
    msg["To"] = destinatario
    msg["Subject"] = asunto
    msg.attach(MIMEText(cuerpo, "plain", "utf-8"))

    if adjunto_path and os.path.exists(adjunto_path):
        with open(adjunto_path, "rb") as f:
            parte = MIMEBase("application", "octet-stream")
            parte.set_payload(f.read())
        encoders.encode_base64(parte)
        nombre_archivo = os.path.basename(adjunto_path)
        parte.add_header("Content-Disposition", f"attachment; filename={nombre_archivo}")
        msg.attach(parte)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_SENDER, gmail_app_password)
            server.sendmail(GMAIL_SENDER, destinatario, msg.as_string())
        return True
    except Exception as e:
        print(f"Error enviando email: {e}")
        return False
