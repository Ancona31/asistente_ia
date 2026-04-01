# Guia de configuracion

## 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

## 2. Crear archivo .env

```bash
cp .env.example .env
```
Llena todos los valores en `.env`.

## 3. Credenciales de Twilio (WhatsApp)

1. Crea cuenta en https://www.twilio.com
2. Activa el Sandbox de WhatsApp en: Console → Messaging → Try it out → WhatsApp
3. Copia `Account SID` y `Auth Token` al `.env`
4. El numero del sandbox es tu `TWILIO_WHATSAPP_NUMBER`

## 4. Credenciales de Google Calendar

1. Ve a https://console.cloud.google.com
2. Crea un proyecto nuevo
3. Activa la API: "Google Calendar API"
4. Ve a Credenciales → Crear credenciales → ID de cliente OAuth 2.0
5. Tipo: "Aplicacion de escritorio"
6. Descarga el JSON y guardalo como `credentials.json` en la raiz del proyecto
7. La primera vez que corras el proyecto se abrira un navegador para autorizar → genera `token.json`

## 5. Gmail (App Password)

1. En tu cuenta Google ve a: Seguridad → Verificacion en 2 pasos (activar si no esta)
2. Luego: Seguridad → Contrasenas de aplicaciones
3. Genera una para "Correo" en "Windows"
4. Agrega esa contrasena de 16 caracteres como `GMAIL_APP_PASSWORD` en tu `.env`

## 6. Correr el servidor

```bash
python main.py
```

## 7. Exponer al internet (para que Twilio llegue al webhook)

Usa ngrok durante desarrollo:
```bash
ngrok http 8000
```
Copia la URL https que da ngrok (ej: `https://abc123.ngrok.io`)

En Twilio → Sandbox de WhatsApp → "When a message comes in":
```
https://abc123.ngrok.io/webhook/whatsapp
```
Metodo: POST

## 8. Probar

Envia un mensaje al numero del sandbox de Twilio desde tu WhatsApp.
El asistente deberia responder automaticamente.
