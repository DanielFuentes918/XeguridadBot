import os
from dotenv import load_dotenv
import requests
from whatsapp_templates import TEMPLATES

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

WHATSAPP_API_URL = "https://graph.facebook.com/v19.0/354178054449225/messages"
WHATSAPP_API_TOKEN = os.getenv("WHATSAPP_API_TOKEN")

def enviar_mensaje_whatsapp(numero, template_key, components=None):
    if components is None:
        components = []
    
    # Obtener la plantilla usando la clave proporcionada
    template = TEMPLATES.get(template_key)
    
    if not template:
        raise ValueError(f"Template key '{template_key}' not found in TEMPLATES.")

    headers = {
        'Authorization': f'Bearer {WHATSAPP_API_TOKEN}',
        'Content-Type': 'application/json'
    }
    data = {
        'messaging_product': 'whatsapp',
        'to': numero,
        'type': 'template',
        'template': {
            'namespace': template['namespace'],
            'name': template['name'],
            'language': template['language'],
            'components': components
        }
    }
    
    response = requests.post(WHATSAPP_API_URL, headers=headers, json=data)
    print(f"Estado de la respuesta: {response.status_code}")
    print(f"Contenido de la respuesta: {response.text}")
    return response.status_code

# Funciones específicas para enviar mensajes con diferentes plantillas

def enviar_cargando_comandos(numero, placa):
    components = [
        {
            "type": "body",
            "parameters": [
                {"type": "text", "text": placa}
            ]
        }
    ]
    return enviar_mensaje_whatsapp(numero, "CARGANDO_COMANDOS_TEMPLATE_NAME", components)

def enviar_placa_no_encontrada(numero, placa):
    components = [
        {
            "type": "body",
            "parameters": [
                {"type": "text", "text": placa}
            ]
        }
    ]
    return enviar_mensaje_whatsapp(numero, "PLACA_NO_ENCONTRADA_TEMPLATE", components)

def enviar_ubicacion_comando(numero, longitud, latitud, address, datetime_actual):
    components = [
        {
            "type": "header",
            "parameters": [
                {
                    "type": "location",
                    "location": {
                        "longitude": longitud,
                        "latitude": latitud,
                        "name": f"{latitud},{longitud}",
                        "address": address
                    }
                }
            ]
        },
        {
            "type": "body",
            "parameters": [
                {"type": "text", "text": address},
                {"type": "text", "text": datetime_actual.strftime("%Y-%m-%d %H:%M:%S")}
            ]
        }
    ]
    return enviar_mensaje_whatsapp(numero, "RESPUESTA_COMANDOS_TEMPLATE", components)

def enviar_comando_no_recibido(numero, longitud, latitud, address, datetime_actual, placa):
    components = [
        {
            "type": "header",
            "parameters": [
                {
                    "type": "location",
                    "location": {
                        "longitude": longitud,
                        "latitude": latitud,
                        "name": f"{latitud},{longitud}",
                        "address": address
                    }
                }
            ]
        },
        {
            "type": "body",
            "parameters": [
                {"type": "text", "text": placa},
                {"type": "text", "text": datetime_actual.strftime("%Y-%m-%d %H:%M:%S")},
                {"type": "text", "text": address}
            ]
        }
    ]
    return enviar_mensaje_whatsapp(numero, "COMANDO_NO_RECIBIDO_TEMPLATE", components)

def prueba_envio_mensaje(numero):
    """
    Función para probar el envío de un mensaje utilizando la plantilla 'MENU_TEMPLATE_NAME'.
    """
    # Define los componentes que quieres enviar con la plantilla, si es necesario
    components = [
        {
            "type": "body",
            "parameters": [
                {"type": "text", "text": "Este es un mensaje de prueba."}
            ]
        }
    ]
    
    # Llama a la función `enviar_mensaje_whatsapp` para enviar el mensaje
    status_code = enviar_mensaje_whatsapp(numero, "MENU_TEMPLATE_NAME", components)
    
    if status_code == 200:
        print("Mensaje enviado exitosamente.")
    else:
        print(f"Fallo en el envío del mensaje. Código de estado: {status_code}")