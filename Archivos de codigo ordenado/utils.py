from bson import ObjectId
import re

def serialize_document(doc):
    """Convierte un documento de MongoDB a un formato JSON serializable."""
    if doc is None:
        return None
    doc = dict(doc)  # Convertir BSON a diccionario
    doc['_id'] = str(doc['_id'])  # Convertir ObjectId a string
    return doc

def check_password(stored_hash, provided_password):
    """Verifica si un hash bcrypt coincide con la contraseña proporcionada."""
    import bcrypt
    if isinstance(stored_hash, str):
        stored_hash = stored_hash.encode('utf-8')
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_hash)

def extraer_placa(nombre):
    """Extrae la placa del nombre de la unidad usando expresiones regulares."""
    print(f"Extrayendo placa del nombre: {nombre}")
    match = re.search(r'\b[A-Z]{3}\d{4}\b', nombre)
    if match:
        print(f"Placa encontrada: {match.group(0)}")
    else:
        print("No se encontró una placa en el nombre")
    return match.group(0) if match else nombre  # Retorna el nombre completo si no se encuentra placa
