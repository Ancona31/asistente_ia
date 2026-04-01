# Definiciones de herramientas que Claude puede invocar

TOOLS = [
    {
        "name": "buscar_paciente",
        "description": "Busca un paciente en la base de datos por nombre o numero de telefono.",
        "input_schema": {
            "type": "object",
            "properties": {
                "nombre": {"type": "string", "description": "Nombre del paciente (parcial o completo)"},
                "telefono": {"type": "string", "description": "Numero de telefono del paciente"},
            },
        },
    },
    {
        "name": "registrar_paciente",
        "description": "Registra un nuevo paciente en el sistema.",
        "input_schema": {
            "type": "object",
            "properties": {
                "nombre": {"type": "string", "description": "Nombre completo del paciente"},
                "telefono": {"type": "string", "description": "Numero de telefono con codigo de pais"},
                "email": {"type": "string", "description": "Correo electronico del paciente"},
                "fecha_nacimiento": {"type": "string", "description": "Fecha de nacimiento en formato DD/MM/AAAA"},
                "notas": {"type": "string", "description": "Notas adicionales sobre el paciente"},
            },
            "required": ["nombre", "telefono"],
        },
    },
    {
        "name": "ver_disponibilidad",
        "description": "Consulta los horarios disponibles en Google Calendar para agendar una cita.",
        "input_schema": {
            "type": "object",
            "properties": {
                "fecha": {"type": "string", "description": "Fecha en formato AAAA-MM-DD. Si no se especifica, usa el proximo dia habil."},
            },
        },
    },
    {
        "name": "agendar_cita",
        "description": "Agrega una cita en Google Calendar y la registra en la base de datos.",
        "input_schema": {
            "type": "object",
            "properties": {
                "paciente_id": {"type": "integer", "description": "ID del paciente en el sistema"},
                "fecha_hora": {"type": "string", "description": "Fecha y hora en formato AAAA-MM-DDTHH:MM"},
                "motivo": {"type": "string", "description": "Motivo de la consulta"},
            },
            "required": ["paciente_id", "fecha_hora"],
        },
    },
    {
        "name": "cancelar_cita",
        "description": "Cancela una cita existente en Google Calendar y actualiza el estado en la base de datos.",
        "input_schema": {
            "type": "object",
            "properties": {
                "cita_id": {"type": "integer", "description": "ID de la cita en el sistema"},
            },
            "required": ["cita_id"],
        },
    },
    {
        "name": "ver_citas_paciente",
        "description": "Muestra las citas proximas o pasadas de un paciente.",
        "input_schema": {
            "type": "object",
            "properties": {
                "paciente_id": {"type": "integer", "description": "ID del paciente"},
                "solo_proximas": {"type": "boolean", "description": "Si es true, solo muestra citas futuras"},
            },
            "required": ["paciente_id"],
        },
    },
    {
        "name": "enviar_email",
        "description": "Envia un correo electronico al paciente, opcionalmente con un PDF adjunto.",
        "input_schema": {
            "type": "object",
            "properties": {
                "destinatario_email": {"type": "string", "description": "Correo del destinatario"},
                "asunto": {"type": "string", "description": "Asunto del correo"},
                "cuerpo": {"type": "string", "description": "Cuerpo del correo en texto plano"},
                "adjunto_pdf": {"type": "string", "description": "Ruta al archivo PDF a adjuntar (opcional)"},
            },
            "required": ["destinatario_email", "asunto", "cuerpo"],
        },
    },
    {
        "name": "generar_receta",
        "description": "Genera un PDF de receta medica para un paciente.",
        "input_schema": {
            "type": "object",
            "properties": {
                "paciente_id": {"type": "integer", "description": "ID del paciente"},
                "medicamentos": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "nombre": {"type": "string"},
                            "dosis": {"type": "string"},
                            "frecuencia": {"type": "string"},
                            "duracion": {"type": "string"},
                        },
                    },
                    "description": "Lista de medicamentos con dosis e instrucciones",
                },
                "indicaciones": {"type": "string", "description": "Indicaciones generales para el paciente"},
            },
            "required": ["paciente_id", "medicamentos"],
        },
    },
    {
        "name": "notificar_doctor",
        "description": "Envia una notificacion urgente al doctor por WhatsApp cuando se requiere atencion inmediata.",
        "input_schema": {
            "type": "object",
            "properties": {
                "mensaje": {"type": "string", "description": "Mensaje de notificacion para el doctor"},
            },
            "required": ["mensaje"],
        },
    },
]
