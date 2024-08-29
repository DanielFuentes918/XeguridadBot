import re

def extraer_placa(nombre):
    match = re.search(r'\b[A-Z]{3}\d{4}\b', nombre)
    return match.group(0) if match else nombre

def serialize_document(doc):
    if doc is None:
        return None
    doc = dict(doc)
    doc['_id'] = str(doc['_id'])
    return doc
