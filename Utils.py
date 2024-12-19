from Config import Config
import requests
import re
from datetime import datetime

config = Config()

user_requests = {}

def envioTemplateTxt(numero, template_name, components):
    response_status = envioMsj(numero, template_name, components)
    print(f"Estado de la respuesta al enviar mensaje: {response_status}")

def envioMsj(numero, template_name, components):
    headers = {
        'Authorization': f'Bearer {config.WHATSAPP_API_TOKEN}',
        'Content-Type': 'application/json'
    }
    data = {
        'messaging_product': 'whatsapp',
        'to': numero,
        'type': 'template',
        'template': {
            'namespace': config.NAMESPACE,
            'name': template_name,
            'language': {
                'policy': 'deterministic',
                'code': 'es'
            },
            'components': components
        }
    }
    response = requests.post(config.WHATSAPP_API_URL, headers=headers, json=data)
    print(f"Estado de la respuesta: {response.status_code}")
    print(f"Contenido de la respuesta: {response.text}")
    return response.status_code

def buscar_unitnumber_por_placa(placa):
    params = {
        'commandname': 'get_units',
        'user': config.XEGURIDAD_USERNAME,
        'pass': config.XEGURIDAD_PASSWORD,
        'format': 'json1'
    }
    response = requests.get(config.XEGURIDAD_API_URL, params=params)
    print(f"Estado de la respuesta de la API: {response.status_code}")
    if response.status_code == 200:
        unidades = response.json()
        print(f"Unidades recibidas: {unidades}")
        for unidad in unidades:
            nombre_placa = extraer_placa(unidad['name'])
            print(f"Nombre de la unidad: {unidad['name']}, Placa extraída: {nombre_placa}")
            if nombre_placa == placa:
                print(f"Unitnumber encontrado: {unidad['unitnumber']} para la placa {placa}")
                return unidad['unitnumber']
    return None

def extraer_placa(nombre):
    print(f"Extrayendo placa del nombre: {nombre}")
    match = re.search(r'\b[A-Z]{3}\d{4}\b', nombre)
    if match:
        print(f"Placa encontrada: {match.group(0)}")
    else:
        print("No se encontró una placa en el nombre")
    return match.group(0) if match else nombre  # Retorna el nombre completo si no se encuentra placa

def obtener_ultima_transmision(unitnumber, numero):
    params = {
        'commandname': 'get_last_transmit',
        'unitnumber': unitnumber,
        'user': config.XEGURIDAD_USERNAME,
        'pass': config.XEGURIDAD_PASSWORD,
        'format': 'json1'
    }
    response = requests.get(config.XEGURIDAD_API_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        if data:
            transmision = data[0]
            latitud = transmision.get("latitude")
            longitud = transmision.get("longitude")
            address = transmision.get("address")
            perimeter = transmision.get("perimeter", "No definido")
            datetime_actual = transmision.get("datetime_actual")

            # Convertir datetime_actual a formato legible
            datetime_actual = datetime.strptime(datetime_actual, "%Y%m%d%H%M%S")
            datetime_actual = datetime_actual.strftime("%Y-%m-%d %H:%M:%S")

            fecha_hora_obj = datetime.strptime(datetime_actual, "%Y-%m-%d %H:%M:%S") 
            placa = user_requests[numero]['placa']
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
                    "parameters": [
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

            hora_envio_placa = user_requests[numero]['hora']
            if fecha_hora_obj >= hora_envio_placa:
                envioTemplateTxt(numero, config.RESPUESTA_COMANDOS_TEMPLATE,components)
            else:
                
                print("PLACA::",placa)
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
                envioTemplateTxt(numero, config.COMANDO_NO_RECIBIDO_TEMPLATE, components)
        else:
            return "No se encontró la última transmisión."
    else:
        return "No se pudo obtener la última transmisión."
    
def descargar_imagen(media_id, access_token):
    # Endpoint para obtener la URL del archivo
    url = f"https://graph.facebook.com/v21.0/{media_id}"
    headers = {"Authorization": f"Bearer {access_token}"}

    try:
        # Obtener la URL de descarga
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            download_url = response.json().get('url')
            if download_url:
                # Descargar la imagen desde la URL obtenida
                image_response = requests.get(download_url, headers=headers)
                if image_response.status_code == 200:
                    filename = f"/tmp/{media_id}.jpg"
                    with open(filename, 'wb') as file:
                        file.write(image_response.content)
                    print(f"Imagen descargada exitosamente: {filename}")
                    return filename
                else:
                    print(f"Error al descargar la imagen: {image_response.status_code}")
            else:
                print("No se pudo obtener la URL de descarga.")
        else:
            print(f"Error al obtener la URL de descarga: {response.status_code} {response.text}")
    except Exception as e:
        print(f"Excepción al intentar descargar la imagen: {e}")
    return None
