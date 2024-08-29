import os
from urllib.parse import quote_plus
from pymongo import MongoClient
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

USUARIO_MONGO = os.getenv("MONGO_DB_USERNAME")
PASSWORD_MONGO = os.getenv("MONGO_DB_PASSWORD")
PASSWORD_MONGO_ESCAPADA = quote_plus(PASSWORD_MONGO)
BASE_DATOS_MONGO = "XeguridadBotDB"
AUTH_DB = "admin"

uri = f"mongodb://{USUARIO_MONGO}:{PASSWORD_MONGO_ESCAPADA}@localhost:27017/{BASE_DATOS_MONGO}?authSource={AUTH_DB}"

try:
    client = MongoClient(uri)
    db = client[BASE_DATOS_MONGO]
    collectionUsuarios = db['usuarios']
    print("Conexión a MongoDB exitosa.")
except Exception as e:
    print(f"Error al conectar a MongoDB: {e}")

usuarios_autenticados = {}

# Definición de `serialize_document`
def serialize_document(doc):
    """Convierte un documento de MongoDB a un formato JSON serializable."""
    if doc is None:
        return None
    doc = dict(doc)  # Convertir BSON a diccionario
    doc['_id'] = str(doc['_id'])  # Convertir ObjectId a string
    return doc