from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()


class Paciente(Base):
    __tablename__ = "pacientes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    telefono = Column(String(30), unique=True, index=True)
    email = Column(String(150))
    fecha_nacimiento = Column(String(20))
    notas = Column(Text, default="")
    creado_en = Column(DateTime, default=datetime.utcnow)

    citas = relationship("Cita", back_populates="paciente")
    mensajes = relationship("Mensaje", back_populates="paciente")


class Cita(Base):
    __tablename__ = "citas"

    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id"), nullable=False)
    google_event_id = Column(String(200))
    fecha_hora = Column(DateTime, nullable=False)
    motivo = Column(String(300), default="Consulta general")
    estado = Column(String(30), default="confirmada")  # confirmada, cancelada, completada
    creado_en = Column(DateTime, default=datetime.utcnow)

    paciente = relationship("Paciente", back_populates="citas")


class Mensaje(Base):
    __tablename__ = "mensajes"

    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id"), nullable=True)
    telefono = Column(String(30), nullable=False)
    rol = Column(String(10))  # "user" o "assistant"
    contenido = Column(Text, nullable=False)
    creado_en = Column(DateTime, default=datetime.utcnow)

    paciente = relationship("Paciente", back_populates="mensajes")
