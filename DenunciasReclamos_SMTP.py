import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración del servidor SMTP
SMTP_SERVER = 'mail.exasa.net'  # Cambia esto a tu servidor SMTP
SMTP_PORT = 465 # Puerto seguro para el servidor SMTP
EMAIL_USER = 'not-reply@exasa.net'
EMAIL_DESTINATION = os.getenv("EMAIL_DESTINATION")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")  # Usa variables de entorno para la seguridad

# Función para enviar el correo de queja
def enviar_queja_anonima(denuncia, archivos=[], empresa=""):
    try:
        # Configurar el correo
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER # Aquí va el remitente
        msg['To'] = EMAIL_DESTINATION  # Aquí va el destinatario
        msg['Subject'] = 'Nueva Denuncia Anónima'

        # Concatenar mensajes de la denuncia
        cuerpo = f"Se ha recibido la siguiente denuncia anónima interpuesta en la empresa {empresa}:\n\n{denuncia}"
        msg.attach(MIMEText(cuerpo, 'plain'))

        # Adjuntar archivos (imágenes)
        for archivo in archivos:
            try:
                with open(archivo, 'rb') as file:
                    mime_base = MIMEBase('application', 'octet-stream')
                    mime_base.set_payload(file.read())
                    encoders.encode_base64(mime_base)
                    mime_base.add_header('Content-Disposition', f'attachment; filename={os.path.basename(archivo)}')
                    msg.attach(mime_base)
                    print(f"Archivo adjuntado: {archivo}")
            except Exception as e:
                print(f"Error al adjuntar el archivo {archivo}: {e}")

        # Conexión al servidor SMTP (SSL para el puerto 465)
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(EMAIL_USER, EMAIL_PASSWORD)

        # Enviar correo
        server.sendmail(EMAIL_USER, EMAIL_DESTINATION, msg.as_string())
        server.quit()

        print("Correo enviado exitosamente.")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")
