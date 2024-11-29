import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "9189189189")
    WHATSAPP_API_URL = os.getenv("WHATSAPP_API_URL")
    WHATSAPP_API_TOKEN = os.getenv("WHATSAPP_API_TOKEN")
    NAMESPACE = os.getenv("NAMESPACE")
    XEGURIDAD_API_URL = os.getenv("XEGURIDAD_API_URL")
    XEGURIDAD_USERNAME = os.getenv("XEGURIDAD_USERNAME", "dhnexasa")
    XEGURIDAD_PASSWORD = os.getenv("XEGURIDAD_PASSWORD")
    USUARIO_MONGO = os.getenv("USUARIO_MONGO", "exasa")
    PASSWORD_MONGO = os.getenv("PASSWORD_MONGO")
    BASE_DATOS_MONGO = os.getenv("BASE_DATOS_MONGO", "XeguridadBotDB")
    AUTH_DB = os.getenv("AUTH_DB", "admin")
    PORT = os.getenv("PORT", 5000)
