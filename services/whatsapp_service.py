from twilio.rest import Client
from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER


def get_twilio_client() -> Client:
    return Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


def enviar_mensaje(destinatario: str, mensaje: str) -> str:
    """
    Envia un mensaje de WhatsApp.
    destinatario: numero con formato 'whatsapp:+521234567890'
    """
    client = get_twilio_client()

    # Asegurar formato correcto
    if not destinatario.startswith("whatsapp:"):
        destinatario = f"whatsapp:{destinatario}"

    message = client.messages.create(
        from_=TWILIO_WHATSAPP_NUMBER,
        to=destinatario,
        body=mensaje,
    )
    return message.sid


def enviar_documento(destinatario: str, mensaje: str, url_archivo: str) -> str:
    """
    Envia un mensaje de WhatsApp con un archivo adjunto.
    url_archivo: URL publica del archivo (debe ser accesible desde internet)
    """
    client = get_twilio_client()

    if not destinatario.startswith("whatsapp:"):
        destinatario = f"whatsapp:{destinatario}"

    message = client.messages.create(
        from_=TWILIO_WHATSAPP_NUMBER,
        to=destinatario,
        body=mensaje,
        media_url=[url_archivo],
    )
    return message.sid
