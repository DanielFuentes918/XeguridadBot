import os
from urllib.parse import quote_plus
from pymongo import MongoClient

USUARIO_MONGO = "admin"
CONTRASEÑA_MONGO = os.getenv("MONGO_DB_PASSWORD")
CONTRASEÑA_MONGO_ESCAPADA = quote_plus(CONTRASEÑA_MONGO)
BASE_DATOS_MONGO = "XeguridadBotDB"
AUTH_DB = "admin"

uri = f"mongodb://{USUARIO_MONGO}:{CONTRASEÑA_MONGO_ESCAPADA}@localhost:27017/{BASE_DATOS_MONGO}?authSource={AUTH_DB}"

# Conexion a MongoDB con manejo de excepciones
try:
    client = MongoClient(uri)
    db = client[BASE_DATOS_MONGO]
    collectionUsuarios = db['usuarios']
    print("Conexión a MongoDB exitosa.")
except Exception as e:
    print(f"Error al conectar a MongoDB: {e}")