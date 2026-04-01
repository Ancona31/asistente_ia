from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import os

from config import (
    GOOGLE_CREDENTIALS_FILE,
    GOOGLE_TOKEN_FILE,
    GOOGLE_CALENDAR_ID,
    HORARIO_INICIO,
    HORARIO_FIN,
    DURACION_TURNO_MINUTOS,
)

SCOPES = ["https://www.googleapis.com/auth/calendar"]


def get_calendar_service():
    creds = None

    if os.path.exists(GOOGLE_TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(GOOGLE_TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(GOOGLE_CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(GOOGLE_TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)


def ver_disponibilidad(fecha: str | None = None) -> list[dict]:
    """
    Devuelve lista de horarios disponibles para una fecha dada.
    fecha: 'AAAA-MM-DD', si es None usa el proximo dia habil.
    """
    service = get_calendar_service()

    if fecha is None:
        dia = datetime.now()
        if dia.weekday() >= 5:  # fin de semana
            dias_hasta_lunes = 7 - dia.weekday()
            dia = dia + timedelta(days=dias_hasta_lunes)
        else:
            dia = dia + timedelta(days=1)
        fecha = dia.strftime("%Y-%m-%d")

    inicio_jornada = datetime.strptime(f"{fecha} {HORARIO_INICIO}", "%Y-%m-%d %H:%M")
    fin_jornada = datetime.strptime(f"{fecha} {HORARIO_FIN}", "%Y-%m-%d %H:%M")

    # Obtener eventos existentes ese dia
    eventos = (
        service.events()
        .list(
            calendarId=GOOGLE_CALENDAR_ID,
            timeMin=inicio_jornada.isoformat() + "-06:00",
            timeMax=fin_jornada.isoformat() + "-06:00",
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
        .get("items", [])
    )

    ocupados = set()
    for evento in eventos:
        inicio_str = evento["start"].get("dateTime", "")
        if inicio_str:
            inicio_evento = datetime.fromisoformat(inicio_str)
            ocupados.add(inicio_evento.strftime("%H:%M"))

    # Generar slots disponibles
    disponibles = []
    slot = inicio_jornada
    while slot < fin_jornada:
        hora_str = slot.strftime("%H:%M")
        if hora_str not in ocupados:
            disponibles.append({
                "fecha": fecha,
                "hora": hora_str,
                "fecha_hora": slot.strftime("%Y-%m-%dT%H:%M"),
            })
        slot += timedelta(minutes=DURACION_TURNO_MINUTOS)

    return disponibles


def agendar_cita(
    nombre_paciente: str,
    email_paciente: str | None,
    fecha_hora: str,
    motivo: str = "Consulta general",
) -> dict:
    """
    Crea un evento en Google Calendar.
    fecha_hora: 'AAAA-MM-DDTHH:MM'
    Devuelve dict con id y link del evento.
    """
    service = get_calendar_service()

    inicio = datetime.strptime(fecha_hora, "%Y-%m-%dT%H:%M")
    fin = inicio + timedelta(minutes=DURACION_TURNO_MINUTOS)

    attendees = []
    if email_paciente:
        attendees.append({"email": email_paciente})

    evento = {
        "summary": f"Consulta: {nombre_paciente}",
        "description": motivo,
        "start": {"dateTime": inicio.isoformat(), "timeZone": "America/Mexico_City"},
        "end": {"dateTime": fin.isoformat(), "timeZone": "America/Mexico_City"},
        "attendees": attendees,
        "reminders": {
            "useDefault": False,
            "overrides": [
                {"method": "email", "minutes": 60},
                {"method": "popup", "minutes": 15},
            ],
        },
    }

    resultado = service.events().insert(calendarId=GOOGLE_CALENDAR_ID, body=evento, sendUpdates="all").execute()

    return {
        "event_id": resultado["id"],
        "link": resultado.get("htmlLink", ""),
    }


def cancelar_cita(event_id: str) -> bool:
    """Cancela un evento en Google Calendar."""
    service = get_calendar_service()
    try:
        service.events().delete(calendarId=GOOGLE_CALENDAR_ID, eventId=event_id).execute()
        return True
    except Exception:
        return False
