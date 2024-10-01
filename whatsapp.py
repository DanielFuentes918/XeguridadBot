import os
import requests
from whatsapp_templates import TEMPLATES

WHATSAPP_API_URL = "https://graph.facebook.com/v20.0/443756312149340/messages"
WHATSAPP_API_TOKEN = "EAARCdrR4dXkBO8dUuQyWQG4G6vVMNywfLepNxDZAK3dko619JnEWX5Ar4ZBzheXB77L6fukmQYsNvIMzgQuFXVoAWb1kqwJ1A5VA27X9i7WTDKT5SbHSrQjKpTZAF5TRZAOsFfeIgNxMbddXyMUuYYqy6VB4lqm9KzR98L3ZALqo8pum5JZCZABivP30ZCKPQpQ26rFlcC5mtmwGcZADZBNbr7ZA3jPEzsZD"

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

def enviar_auth_template(numero):
    components = []
    return enviar_mensaje_whatsapp(numero, "AUTH_TEMPLATE", components)

def enviar_auth_failed_template(numero):
    components = []
    return enviar_mensaje_whatsapp(numero, "AUTH_FAILED_TEMPLATE", components)

def enviar_menu_template(numero):
    components = []
    return enviar_mensaje_whatsapp(numero, "MENU_TEMPLATE", components)

def enviar_solicitud_unidad_comandos_template(numero):
    components = []
    return enviar_mensaje_whatsapp(numero, "SOLICITUD_UNIDAD_COMANDOS_TEMPLATE", components)

def enviar_cargando_comandos_template(numero):
    components = []
    return enviar_mensaje_whatsapp(numero, "CARGANDO_COMANDOS_TEMPLATE_NAME", components)

def enviar_placa_no_encontrada_template(numero):
    components = []
    return enviar_mensaje_whatsapp(numero, "PLACA_NO_ENCONTRADA_TEMPLATE", components)

def enviar_respuesta_comandos_template(numero, longitud, latitud, address, components, datetime_actual):
    components = [
        {
            "type": "header",
                    "parameters": [
                        {
                            "type": "location",
                            "location": {
                                "longitude": longitud,
                                "latitude": latitud,
                                "name": str(latitud)+","+str(longitud),
                                "address": str(latitud)+","+str(longitud)
                            }
                        }
                    ]
        },
        {
            "type": "body",
                    "parameters": components + [
                        {
                            "type": "text",
                            "text": address
                        },
                        {
                            "type": "text",
                            "text": datetime_actual.strftime("%Y-%m-%d %H:%M:%S")
                        }
                    ]
        }
    ]
    return enviar_mensaje_whatsapp(numero, "RESPUESTA_COMANDOS_TEMPLATE", components)

def enviar_comando_no_recibido_template(numero, longitud, latitud, address, datetime_actual, placa):
    components = [
        {
            "type": "header",
                    "parameters": [
                        {
                            "type": "location",
                            "location": {
                                "longitude": longitud,
                                "latitude": latitud,
                                "name": str(latitud)+","+str(longitud),
                                "address": str(latitud)+","+str(longitud)
                            }
                        }
                    ]
        },
        {
            "type": "body",
                    "parameters": components + [
                        {
                            "type": "text",
                            "text": placa
                        },
                        {
                            "type": "text",
                            "text": datetime_actual.strftime("%Y-%m-%d %H:%M:%S")  # Convertir a cadena de texto
                        },
                        {
                            "type": "text",
                            "text": address
                        }
                    ]
        }
    ]
    return enviar_mensaje_whatsapp(numero, "COMANDO_NO_RECIBIDO_TEMPLATE", components)
    response = requests.post(WHATSAPP_API_URL, headers=headers, json=data)
    print(f"Estado de la respuesta: {response.status_code}")
    print(f"Contenido de la respuesta: {response.text}")
    # Eliminar el número de esperando_placa si el mensaje se envió correctamente
    if response.status_code == 200:
        if numero in esperando_placa:
            del esperando_placa[numero]
            print(f"Número {numero} eliminado de esperando_placa")
    else:
        print(f"Error al enviar mensaje, estado de la respuesta: {response.status_code}")
    return response.status_code