import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

class Config:
#Clase que manejara la configuracion global de la aplicacion
    def __init__(self):
        
        load_dotenv()
        # Varaibles de entorno
        self.VERIFY_TOKEN = "9189189189"
        self.WHATSAPP_API_URL = os.getenv("WHATSAPP_API_URL")
        self.WHATSAPP_API_TOKEN = os.getenv("WHATSAPP_API_TOKEN")
        self.NAMESPACE = os.getenv("NAMESPACE")
        self.XEGURIDAD_API_URL = os.getenv("XEGURIDAD_API_URL")
        self.XEGURIDAD_USERNAME = "dhnexasa"
        self.XEGURIDAD_PASSWORD = os.getenv("XEGURIDAD_PASSWORD")
        self.USUARIO_MONGO = "exasa"
        self.PASSWORD_MONGO = os.getenv("PASSWORD_MONGO")
        self.PASSWORD_MONGO_ESCAPADA = quote_plus(self.PASSWORD_MONGO)
        self.BASE_DATOS_MONGO = "XeguridadBotDB"
        self.AUTH_DB = "admin"
        self.PORT = os.getenv("PORT")

        # Plantillas
        self.STARTER_MENU_TEMPLATE = "starter_menu"
        self.AUTH_TEMPLATE = "auth_request"
        self.AUTH_FAILED_TEMPLATE = "auth_failed"
        self.MENU_TEMPLATE_NAME = "xeguridad_menu"
        self.SOLICITUD_UNIDAD_COMANDOS_TEMPLATE_NAME = "plate_number__request"
        self.CARGANDO_COMANDOS_TEMPLATE_NAME = "lt_command__loading"
        self.RESPUESTA_COMANDOS_TEMPLATE = "lt_command__response"
        self.COMANDO_NO_RECIBIDO_TEMPLATE = "lt_command__failed"
        self.PLACA_NO_ENCONTRADA_TEMPLATE = "plate_number_wasnt_find"
        self.COMPLAINT_CLAIMS_TEMPLATE = "complaint_claims_request"
        self.COMPLAINT_CLAIMS_COPY_TEMPLATE = "complaint_claims_copy"
        self.COMPLAINT_CLAIMS_NOTIFICATION_TEMPLATE = "complaint_claims_notification"
        self.COMPANY_SELECTION_TEMPLATE = "company_selection"

    def mongo_uri(self):
        return f"mongodb://{self.USUARIO_MONGO}:{self.PASSWORD_MONGO_ESCAPADA}@localhost:27017/{self.BASE_DATOS_MONGO}?authSource={self.AUTH_DB}"