from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import os

from config import DOCTOR_NAME, CONSULTORIO_NOMBRE, CONSULTORIO_DIRECCION, CONSULTORIO_TELEFONO


def generar_receta(
    paciente_nombre: str,
    medicamentos: list[dict],
    indicaciones: str = "",
    output_dir: str = "temp",
) -> str:
    """
    Genera un PDF de receta medica.
    Devuelve la ruta al archivo generado.

    medicamentos: lista de dicts con claves: nombre, dosis, frecuencia, duracion
    """
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"receta_{paciente_nombre.replace(' ', '_')}_{timestamp}.pdf"
    ruta = os.path.join(output_dir, nombre_archivo)

    doc = SimpleDocTemplate(ruta, pagesize=letter, topMargin=2 * cm, bottomMargin=2 * cm)
    styles = getSampleStyleSheet()

    estilo_titulo = ParagraphStyle("titulo", parent=styles["Heading1"], alignment=TA_CENTER, fontSize=16)
    estilo_subtitulo = ParagraphStyle("subtitulo", parent=styles["Normal"], alignment=TA_CENTER, fontSize=11, textColor=colors.grey)
    estilo_normal = ParagraphStyle("normal", parent=styles["Normal"], fontSize=11, leading=16)
    estilo_negrita = ParagraphStyle("negrita", parent=styles["Normal"], fontSize=11, fontName="Helvetica-Bold")

    elementos = []

    # Encabezado
    elementos.append(Paragraph(CONSULTORIO_NOMBRE, estilo_titulo))
    elementos.append(Paragraph(DOCTOR_NAME, estilo_subtitulo))
    if CONSULTORIO_DIRECCION:
        elementos.append(Paragraph(CONSULTORIO_DIRECCION, estilo_subtitulo))
    if CONSULTORIO_TELEFONO:
        elementos.append(Paragraph(f"Tel: {CONSULTORIO_TELEFONO}", estilo_subtitulo))
    elementos.append(Spacer(1, 0.5 * cm))
    elementos.append(HRFlowable(width="100%", thickness=1, color=colors.black))
    elementos.append(Spacer(1, 0.5 * cm))

    # Datos del paciente y fecha
    fecha_str = datetime.now().strftime("%d/%m/%Y")
    elementos.append(Paragraph(f"<b>Paciente:</b> {paciente_nombre}", estilo_normal))
    elementos.append(Paragraph(f"<b>Fecha:</b> {fecha_str}", estilo_normal))
    elementos.append(Spacer(1, 0.5 * cm))
    elementos.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    elementos.append(Spacer(1, 0.5 * cm))

    # Rx
    elementos.append(Paragraph("℞ RECETA", estilo_negrita))
    elementos.append(Spacer(1, 0.3 * cm))

    for i, med in enumerate(medicamentos, 1):
        nombre = med.get("nombre", "")
        dosis = med.get("dosis", "")
        frecuencia = med.get("frecuencia", "")
        duracion = med.get("duracion", "")

        elementos.append(Paragraph(f"<b>{i}. {nombre}</b>", estilo_normal))
        detalle = []
        if dosis:
            detalle.append(f"Dosis: {dosis}")
        if frecuencia:
            detalle.append(f"Frecuencia: {frecuencia}")
        if duracion:
            detalle.append(f"Duracion: {duracion}")
        if detalle:
            elementos.append(Paragraph("    " + " | ".join(detalle), estilo_normal))
        elementos.append(Spacer(1, 0.2 * cm))

    if indicaciones:
        elementos.append(Spacer(1, 0.5 * cm))
        elementos.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
        elementos.append(Spacer(1, 0.3 * cm))
        elementos.append(Paragraph("<b>Indicaciones generales:</b>", estilo_normal))
        elementos.append(Paragraph(indicaciones, estilo_normal))

    # Firma
    elementos.append(Spacer(1, 2 * cm))
    elementos.append(HRFlowable(width="40%", thickness=1, color=colors.black))
    elementos.append(Paragraph(DOCTOR_NAME, estilo_normal))
    elementos.append(Paragraph("Firma y sello", ParagraphStyle("firma", parent=styles["Normal"], fontSize=9, textColor=colors.grey)))

    doc.build(elementos)
    return ruta
