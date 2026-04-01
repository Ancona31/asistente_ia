import anthropic
import json
from datetime import datetime

from config import ANTHROPIC_API_KEY, DOCTOR_NAME, CONSULTORIO_NOMBRE, HORARIO_INICIO, HORARIO_FIN
from tools.agent_tools import TOOLS

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = f"""Eres el asistente virtual del {CONSULTORIO_NOMBRE}, a cargo de {DOCTOR_NAME}.
Tu trabajo es atender pacientes y personas que escriben por WhatsApp de forma amable, profesional y eficiente.

Fecha y hora actual: {{fecha_hora}}

Tus responsabilidades:
- Registrar nuevos pacientes cuando sea necesario
- Agendar, cancelar o reprogramar citas medicas
- Informar sobre disponibilidad de horarios
- Enviar confirmaciones y recordatorios por email
- Generar y enviar recetas medicas cuando el doctor lo indique
- Notificar al doctor si hay una emergencia o situacion urgente

Horario de atencion: {HORARIO_INICIO} a {HORARIO_FIN} horas, de lunes a viernes.

Reglas importantes:
- Siempre saluda de forma cordial y presenta el consultorio
- Si alguien describe una EMERGENCIA MEDICA, dile que llame al 911 y notifica al doctor inmediatamente
- Antes de agendar una cita, verifica que el paciente este registrado; si no, registralo primero
- Confirma siempre los datos de la cita antes de crearla (fecha, hora, motivo)
- No compartas informacion medica de un paciente con otra persona
- Responde siempre en español
- Sé conciso en tus respuestas de WhatsApp (maximo 3-4 lineas por mensaje)
"""


def procesar_mensaje(
    historial: list[dict],
    herramienta_ejecutor,
) -> str:
    """
    Envia el historial al modelo y maneja el loop de herramientas.
    herramienta_ejecutor: funcion(nombre, argumentos) -> str
    Devuelve el texto final de respuesta.
    """
    system = SYSTEM_PROMPT.replace("{fecha_hora}", datetime.now().strftime("%d/%m/%Y %H:%M"))

    messages = list(historial)

    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=system,
            tools=TOOLS,
            messages=messages,
        )

        # Si el modelo quiere usar una herramienta
        if response.stop_reason == "tool_use":
            # Agregar respuesta del asistente al historial
            messages.append({"role": "assistant", "content": response.content})

            # Ejecutar cada herramienta solicitada
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    resultado = herramienta_ejecutor(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(resultado, ensure_ascii=False),
                    })

            messages.append({"role": "user", "content": tool_results})
            continue

        # Respuesta final en texto
        for block in response.content:
            if hasattr(block, "text"):
                return block.text

        return ""
