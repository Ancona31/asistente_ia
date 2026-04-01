from sqlalchemy.orm import Session
from datetime import datetime

from database.models import Paciente, Cita, Mensaje
from services import claude_service, calendar_service, email_service, pdf_service, whatsapp_service
from config import DOCTOR_WHATSAPP


def obtener_historial(db: Session, telefono: str, limite: int = 20) -> list[dict]:
    """Recupera los ultimos mensajes de una conversacion."""
    mensajes = (
        db.query(Mensaje)
        .filter(Mensaje.telefono == telefono)
        .order_by(Mensaje.creado_en.desc())
        .limit(limite)
        .all()
    )
    mensajes.reverse()
    return [{"role": m.rol, "content": m.contenido} for m in mensajes]


def guardar_mensaje(db: Session, telefono: str, rol: str, contenido: str, paciente_id: int | None = None):
    msg = Mensaje(telefono=telefono, rol=rol, contenido=contenido, paciente_id=paciente_id)
    db.add(msg)
    db.commit()


def ejecutar_herramienta(nombre: str, args: dict, db: Session) -> dict:
    """Despacha la herramienta solicitada por Claude y devuelve el resultado."""

    if nombre == "buscar_paciente":
        query = db.query(Paciente)
        if args.get("telefono"):
            query = query.filter(Paciente.telefono.contains(args["telefono"]))
        elif args.get("nombre"):
            query = query.filter(Paciente.nombre.ilike(f"%{args['nombre']}%"))
        pacientes = query.limit(5).all()
        if not pacientes:
            return {"encontrado": False, "mensaje": "No se encontro ningun paciente."}
        return {
            "encontrado": True,
            "pacientes": [
                {
                    "id": p.id,
                    "nombre": p.nombre,
                    "telefono": p.telefono,
                    "email": p.email,
                    "fecha_nacimiento": p.fecha_nacimiento,
                }
                for p in pacientes
            ],
        }

    elif nombre == "registrar_paciente":
        existente = db.query(Paciente).filter(Paciente.telefono == args["telefono"]).first()
        if existente:
            return {"registrado": False, "mensaje": "El paciente ya existe.", "id": existente.id}
        paciente = Paciente(
            nombre=args["nombre"],
            telefono=args["telefono"],
            email=args.get("email"),
            fecha_nacimiento=args.get("fecha_nacimiento"),
            notas=args.get("notas", ""),
        )
        db.add(paciente)
        db.commit()
        db.refresh(paciente)
        return {"registrado": True, "id": paciente.id, "nombre": paciente.nombre}

    elif nombre == "ver_disponibilidad":
        slots = calendar_service.ver_disponibilidad(args.get("fecha"))
        if not slots:
            return {"disponible": False, "mensaje": "No hay horarios disponibles para esa fecha."}
        return {"disponible": True, "horarios": slots[:8]}  # max 8 opciones

    elif nombre == "agendar_cita":
        paciente = db.query(Paciente).filter(Paciente.id == args["paciente_id"]).first()
        if not paciente:
            return {"exitoso": False, "mensaje": "Paciente no encontrado."}

        resultado = calendar_service.agendar_cita(
            nombre_paciente=paciente.nombre,
            email_paciente=paciente.email,
            fecha_hora=args["fecha_hora"],
            motivo=args.get("motivo", "Consulta general"),
        )

        cita = Cita(
            paciente_id=paciente.id,
            google_event_id=resultado["event_id"],
            fecha_hora=datetime.strptime(args["fecha_hora"], "%Y-%m-%dT%H:%M"),
            motivo=args.get("motivo", "Consulta general"),
        )
        db.add(cita)
        db.commit()
        db.refresh(cita)

        return {
            "exitoso": True,
            "cita_id": cita.id,
            "fecha_hora": args["fecha_hora"],
            "motivo": cita.motivo,
        }

    elif nombre == "cancelar_cita":
        cita = db.query(Cita).filter(Cita.id == args["cita_id"]).first()
        if not cita:
            return {"exitoso": False, "mensaje": "Cita no encontrada."}

        if cita.google_event_id:
            calendar_service.cancelar_cita(cita.google_event_id)

        cita.estado = "cancelada"
        db.commit()
        return {"exitoso": True, "mensaje": "Cita cancelada correctamente."}

    elif nombre == "ver_citas_paciente":
        query = db.query(Cita).filter(Cita.paciente_id == args["paciente_id"])
        if args.get("solo_proximas", True):
            query = query.filter(Cita.fecha_hora >= datetime.utcnow())
        citas = query.order_by(Cita.fecha_hora).limit(5).all()
        return {
            "citas": [
                {
                    "id": c.id,
                    "fecha_hora": c.fecha_hora.strftime("%d/%m/%Y %H:%M"),
                    "motivo": c.motivo,
                    "estado": c.estado,
                }
                for c in citas
            ]
        }

    elif nombre == "enviar_email":
        ok = email_service.enviar_email(
            destinatario=args["destinatario_email"],
            asunto=args["asunto"],
            cuerpo=args["cuerpo"],
            adjunto_path=args.get("adjunto_pdf"),
        )
        return {"exitoso": ok}

    elif nombre == "generar_receta":
        paciente = db.query(Paciente).filter(Paciente.id == args["paciente_id"]).first()
        if not paciente:
            return {"exitoso": False, "mensaje": "Paciente no encontrado."}

        ruta_pdf = pdf_service.generar_receta(
            paciente_nombre=paciente.nombre,
            medicamentos=args["medicamentos"],
            indicaciones=args.get("indicaciones", ""),
        )
        return {"exitoso": True, "ruta_pdf": ruta_pdf, "paciente_email": paciente.email}

    elif nombre == "notificar_doctor":
        if DOCTOR_WHATSAPP:
            whatsapp_service.enviar_mensaje(DOCTOR_WHATSAPP, f"⚠️ NOTIFICACION ASISTENTE:\n{args['mensaje']}")
        return {"enviado": True}

    return {"error": f"Herramienta '{nombre}' no implementada."}


def manejar_mensaje_entrante(telefono: str, texto: str, db: Session) -> str:
    """
    Punto de entrada principal para cada mensaje de WhatsApp.
    Devuelve el texto de respuesta.
    """
    # Normalizar telefono
    telefono_limpio = telefono.replace("whatsapp:", "")

    # Buscar paciente por telefono
    paciente = db.query(Paciente).filter(Paciente.telefono.contains(telefono_limpio[-10:])).first()
    paciente_id = paciente.id if paciente else None

    # Guardar mensaje del usuario
    guardar_mensaje(db, telefono_limpio, "user", texto, paciente_id)

    # Obtener historial de la conversacion
    historial = obtener_historial(db, telefono_limpio)

    # Procesar con Claude
    respuesta = claude_service.procesar_mensaje(
        historial=historial,
        herramienta_ejecutor=lambda nombre, args: ejecutar_herramienta(nombre, args, db),
    )

    # Guardar respuesta del asistente
    guardar_mensaje(db, telefono_limpio, "assistant", respuesta, paciente_id)

    return respuesta
