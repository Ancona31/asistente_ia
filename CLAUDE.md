# Asistente IA Consultorio Dr. Ancona

## Quien es el usuario
Dr. Angel M. Ancona Pérez — Traumatologo y Cirujano de Columna Vertebral en Mérida, Mexico.
Atiende en múltiples ubicaciones con horarios variables (no tiene horario fijo).
- Email: drangelmanconaperez@gmail.com
- WhatsApp: +52 9996364504
- Direccion: Esquina C. 34 x C. 13, Los Reyes, Mérida, Mexico, 97156
- GitHub: Ancona31

## Que es este proyecto
Asistente IA para gestionar el consultorio via WhatsApp. Responde pacientes de forma autonoma,
agenda citas en Google Calendar, envia emails, genera recetas en PDF.

## Stack
- Python 3.12
- FastAPI + uvicorn (servidor webhook)
- Claude API claude-sonnet-4-6 (cerebro del asistente)
- Twilio WhatsApp Sandbox (mensajeria)
- Google Calendar API (agenda)
- Gmail SMTP con App Password (correos)
- ReportLab (generacion de PDFs)
- SQLAlchemy + SQLite (base de datos local)

## Estado actual del proyecto
- [x] Estructura base creada
- [x] Dependencias instaladas
- [x] Credenciales configuradas en .env
- [x] Google Calendar autorizado (token.json generado)
- [x] Twilio Sandbox configurado y funcionando
- [x] Servidor corriendo y respondiendo mensajes por WhatsApp
- [ ] Implementar logica de bloques DISPONIBLE CONSULTAS en Google Calendar
- [ ] Educar al asistente con perfil medico completo (especialidades, hospitales, seguros, etc.)
- [ ] Deploy en Railway para correr 24/7
- [ ] Registrar numero oficial de WhatsApp Business (cuando este listo para produccion)

## Archivos NO versionados (copiar manualmente entre PCs)
- .env — credenciales y configuracion
- credentials.json — OAuth Google
- token.json — token de acceso Google Calendar
- ngrok.exe — para desarrollo local

## Como correr en desarrollo
```bash
# Terminal 1 — servidor
python main.py

# Terminal 2 — tunel ngrok
./ngrok.exe http 8000
```
Luego actualizar la URL del webhook en Twilio Sandbox Settings.

## Pendientes importantes
1. Logica de disponibilidad: el asistente debe buscar eventos llamados "DISPONIBLE CONSULTAS"
   en Google Calendar y solo ofrecer slots dentro de esos bloques.
2. Completar el system prompt con info medica real del doctor.
3. Deploy en Railway conectado al repo de GitHub.
