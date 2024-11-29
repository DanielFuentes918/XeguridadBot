import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración del servidor SMTP
SMTP_SERVER = 'mail.exasa.net'  # Cambia esto a tu servidor SMTP
SMTP_PORT = 465 # Puerto seguro para el servidor SMTP
EMAIL_USER = 'not-reply@exasa.net'
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")  # Usa variables de entorno para la seguridad

# Función para enviar el correo de queja
def enviar_queja_anonima(denuncia):
    try:
        # Configurar el correo
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = 'sistemas2@exasa.net'  # Aquí va el destinatario
        msg['Subject'] = 'Nueva Denuncia Anónima'

        # Cuerpo del correo
        cuerpo = f"Se ha recibido la siguiente denuncia anónima:\n\n{denuncia}"
        msg.attach(MIMEText(cuerpo, 'plain'))

        # Conexión al servidor SMTP (SSL para el puerto 465)
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)  # Usar SMTP_SSL en lugar de SMTP
        server.login(EMAIL_USER, EMAIL_PASSWORD)

        # Enviar correo
        server.sendmail(EMAIL_USER, 'sistemas2@exasa.net', msg.as_string())
        server.quit()

        print("Correo enviado exitosamente.")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")