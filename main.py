from fastapi import FastAPI, Form, Depends, Request, HTTPException
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from twilio.request_validator import RequestValidator
import os

from database.database import init_db, get_db
from handlers.message_handler import manejar_mensaje_entrante
from services.whatsapp_service import enviar_mensaje
from config import TWILIO_AUTH_TOKEN

app = FastAPI(title="Asistente IA Consultorio")


@app.on_event("startup")
def startup():
    init_db()
    print("Base de datos inicializada.")


@app.get("/")
def health_check():
    return {"status": "ok", "mensaje": "Asistente IA Consultorio activo"}


@app.post("/webhook/whatsapp")
async def webhook_whatsapp(
    request: Request,
    From: str = Form(...),
    Body: str = Form(...),
    db: Session = Depends(get_db),
):
    # Validar que la solicitud viene de Twilio
    validator = RequestValidator(TWILIO_AUTH_TOKEN)
    url = str(request.url)
    form_data = dict(await request.form())
    signature = request.headers.get("X-Twilio-Signature", "")

    if not validator.validate(url, form_data, signature):
        raise HTTPException(status_code=403, detail="Firma invalida")

    telefono = From
    texto = Body.strip()

    if not texto:
        return PlainTextResponse("", status_code=200)

    try:
        respuesta = manejar_mensaje_entrante(telefono, texto, db)
        enviar_mensaje(telefono, respuesta)
    except Exception as e:
        print(f"Error procesando mensaje de {telefono}: {e}")
        enviar_mensaje(telefono, "Lo siento, ocurrio un error. Por favor intenta de nuevo en un momento.")

    # Twilio espera respuesta 200 vacia (el mensaje ya se envia via API)
    return PlainTextResponse("", status_code=200)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
