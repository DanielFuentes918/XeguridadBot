from Config import Config
import requests
import re
from datetime import datetime
import asyncio
import pytz
from aiohttp import ClientSession
from pytile import async_login

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

def buscar_unitnumber_por_genset(genset):
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
            nombre_genset = extraer_genset(unidad['name'])
            print(f"Nombre de la unidad: {unidad['name']}, Placa extraída: {nombre_genset}")
            if nombre_genset == genset:
                print(f"Unitnumber encontrado: {unidad['unitnumber']} para la placa {genset}")
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

def extraer_genset(nombre):
    print(f"Extrayendo genset del nombre: {nombre}")
    match = re.search(r'GN-([A-Z]\d{5})\b', nombre)
    if match:
        print(f"Genset encontrado: {match.group(1)}")
    else:
        print("No se encontró un genset en el nombre")
    return match.group(1) if match else nombre  # Retorna el nombre completo si no se encuentra Genset


def obtener_ultima_transmision(unitnumber, numero, user_requests):
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
                            "text": datetime_actual
                        }
                    ]
                }
            ]

            hora_envio_placa = user_requests[numero]['hora']
            if fecha_hora_obj >= hora_envio_placa:
                envioTemplateTxt(numero, config.ACTUAL_LOCATION_TEMPLATE,components)
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
                        "parameters": [
                            {
                                "type": "text",
                                "text": placa
                            },
                            {
                                "type": "text",
                                "text": datetime_actual
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
    
def descargar_multimedia(media_id, access_token, tipo="imagen"):
    # Endpoint para obtener la URL del archivo
    url = f"https://graph.facebook.com/v21.0/{media_id}"
    headers = {"Authorization": f"Bearer {access_token}"}

    try:
        # Obtener la URL de descarga
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            download_url = response.json().get('url')
            if download_url:
                # Descargar el archivo desde la URL obtenida
                extension = "mp4" if tipo == "video" else "jpg"
                filename = f"/tmp/{media_id}.{extension}"
                media_response = requests.get(download_url, headers=headers)
                if media_response.status_code == 200:
                    with open(filename, 'wb') as file:
                        file.write(media_response.content)
                    print(f"{tipo.capitalize()} descargado exitosamente: {filename}")
                    return filename
                else:
                    print(f"Error al descargar el {tipo}: {media_response.status_code}")
            else:
                print("No se pudo obtener la URL de descarga.")
        else:
            print(f"Error al obtener la URL de descarga: {response.status_code} {response.text}")
    except Exception as e:
        print(f"Excepción al intentar descargar el {tipo}: {e}")
    return None

async def enviar_ubicacion_tile(tile_name, numero, email, password):
    """
    Envía la ubicación de un Tile específico como plantilla de WhatsApp.
    
    Args:
        tile_name (str): Nombre del Tile a buscar.
        numero (str): Número de teléfono del usuario para WhatsApp.
        email (str): Correo electrónico para la API de Tile.
        password (str): Contraseña para la API de Tile.
    """
    from aiohttp import ClientSession
    from pytile import async_login
    import pytz

    local_tz = pytz.timezone('America/Tegucigalpa')
    utc_tz = pytz.UTC

    async with ClientSession() as session:
        try:
            # Inicia sesión en la API de Tile
            api = await async_login(email, password, session)

            # Obtén todas las balizas asociadas
            tiles = await api.async_get_tiles()

            # Busca el Tile específico
            tile = next((t for t in tiles.values() if t.name == tile_name), None)

            if not tile:
                print(f"Tile con nombre '{tile_name}' no encontrado.")
                components = [
                    {
                        "type": "body",
                        "parameters": [
                            {"type": "text", "text": f"Tile '{tile_name}' no encontrado."}
                        ]
                    }
                ]
                envioTemplateTxt(numero, config.TEMPLATE_ERROR_TILE, components)
                return

            # Convertir la última marca de tiempo
            last_timestamp_utc = tile.last_timestamp.replace(tzinfo=utc_tz)
            last_timestamp_local = last_timestamp_utc.astimezone(local_tz)
            last_transmission = last_timestamp_local.strftime('%Y-%m-%d %H:%M:%S')

            # Crear los componentes de la plantilla
            components = [
                {
                    "type": "header",
                    "parameters": [
                        {
                            "type": "location",
                            "location": {
                                "longitude": tile.longitude,
                                "latitude": tile.latitude,
                                "name": f"{tile.latitude}, {tile.longitude}",
                                "address": f"{tile.latitude}, {tile.longitude}"
                            }
                        }
                    ]
                },
                {
                    "type": "body",
                    "parameters": [
                        {
                        "type": "text",
                        "text": last_transmission
                        }
                    ]
                }
            ]

            # Envía la plantilla de WhatsApp
            envioTemplateTxt(numero, config.TILE_LOCATION_TEMPLATE, components)
            print(f"Ubicación del Tile '{tile_name}' enviada a {numero}.")
        except Exception as e:
            print(f"Error al enviar la ubicación del Tile: {str(e)}")
            components = [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": f"Error al procesar la solicitud: {str(e)}"}
                    ]
                }
            ]
            envioTemplateTxt(numero, config.TEMPLATE_ERROR_TILE, components)

# Función auxiliar para ejecutarlo desde un entorno síncrono
def enviar_ubicacion_tile_sync(tile_name, numero, email, password):
    asyncio.run(enviar_ubicacion_tile(tile_name, numero, email, password))
