import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuración del servidor SMTP
SMTP_SERVER = 'mail.exasa.net'  # Cambia esto a tu servidor SMTP
SMTP_PORT = 465 # Puerto seguro para el servidor SMTP
EMAIL_USER = 'comunicaciones@exasa.net'
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")  # Usa variables de entorno para la seguridad

# Función para enviar el correo de queja
def enviar_queja_anonima(denuncia):
    try:
        # Configurar el correo
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = 'comunicaciones@exasa.net'  # Aquí va el destinatario
        msg['Subject'] = 'Nueva Queja Anónima'

        # Cuerpo del correo
        cuerpo = f"Se ha recibido la siguiente queja anónima:\n\n{denuncia}"
        msg.attach(MIMEText(cuerpo, 'plain'))

        # Conexión al servidor SMTP
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Iniciar la conexión segura
        server.login(EMAIL_USER, EMAIL_PASSWORD)

        # Enviar correo
        server.sendmail(EMAIL_USER, 'comunicaciones@exasa.net', msg.as_string())
        server.quit()

        print("Correo enviado exitosamente.")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")