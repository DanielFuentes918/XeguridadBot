import requests
from datetime import datetime, timedelta, timezone

# Configuración de la API de WhatsApp
WHATSAPP_API_URL = "https://graph.facebook.com/v19.0/354178054449225/messages"
WHATSAPP_API_TOKEN = "EAAFiQXfoAV4BO10PdMbULG2wAmGa108puKpkvVzOzWiSMAusEp4xinrQ8DqcORjWZCzQ07DlNIR3jrcsNGbHVFx0zaJOOzn0GurZC0aTCATmCarHUgne5wWhdNp7qDQvpRMZBwFeWOOWC5ZCDpkmfjRUCMG5s51w4YlB7w1XZBdOgqQfENknQ4XdNsNWHQsZBGSQZDZD"
NAMESPACE = "Xeguridad"
TEMPLATE_NAME = "notificacion_xeguridad"

# Configuración de la API de dispositivos GPS
Xeguridad_API_URL = "https://mongol.brono.com/mongol/api.php"
Xeguridad_USERNAME = "developerexa"
Xeguridad_PASSWORD = "Dev345p1d4"

# Números de teléfono a los que se enviarán los mensajes
Numeros_telefonicos = ["50497338021"]

def formateando_fecha(timestamp):
    return datetime.strptime(timestamp, "%Y%m%d%H%M%S")

def formatear_fecha_dd_mm_aaaa(fecha):
    return fecha.strftime("%d/%m/%Y")

def obtener_unidades():
    # Realizar la solicitud para obtener todas las unidades
    params = {
        'commandname': 'get_units',
        'user': Xeguridad_USERNAME,
        'pass': Xeguridad_PASSWORD,
        'format': 'json1'
    }
    response = requests.get(Xeguridad_API_URL, params=params)
    print(f"Estado de la respuesta: {response.status_code}")
    print(f"Contenido de la respuesta: {response.text}")

    if response.status_code == 200:
        unidades = response.json()
        return unidades

def obtener_ultima_transmision(unidades):
    # Filtrar unidades que no están transmitiendo desde hace 24 horas
    ultima_transmision_unidades = []

    for unidad in unidades:
        params = {
            'commandname': 'get_last_transmit',
            'user': Xeguridad_USERNAME,
            'pass': Xeguridad_PASSWORD,
            'unitnumber': unidad['unitnumber'],
            'format': 'json1'
        }
        response = requests.get(Xeguridad_API_URL, params=params)
        print(f"Estado de la respuesta: {response.status_code}")
        #print(f"Contenido de la respuesta: {response.text}")

        if response.status_code == 200:
            try:
                transmisiones = response.json()
                print("transmisiones::>", transmisiones)
                for data in transmisiones:
                    print(data['datetime_utc'])
                    # Guardar la última transmisión
                    ultima_transmision = data['datetime_utc']
                    # Imprimir la última transmisión obtenida
                    print(f"Unidad: {unidad['unitnumber']} - Última transmisión: {ultima_transmision}")
                    # Creo un diccionario dentro del arreglo para poder acceder a ultima_transmision_unidades[0]['unitnumber'], ultima_transmision_unidades[0]['nombre'] etc...
                    ultima_transmision_unidades.append({'unitnumber':unidad['unitnumber'], 'ultima_trans':ultima_transmision, 'nombre':data['name']})
                    print("ARRAY INFO:", ultima_transmision_unidades[0]['unitnumber'])
            except Exception as e:
                print(f"Error al procesar las transmisiones: {e}")

    return ultima_transmision_unidades

def obtener_unidades_no_transmitiendo(ultima_transmision_unidades):
    unidades_no_transmitiendo = []
    ahora = datetime.now(timezone.utc)  # Asegurando que 'ahora' tiene información de zona horaria
    
    for unidad in ultima_transmision_unidades:
        print(unidad['ultima_trans'], "---**---")
        if unidad['ultima_trans']:
            print("ULTIMA TRANS:", unidad['ultima_trans'])
            try:
                ultima_transmision_dt = formateando_fecha(unidad['ultima_trans'])
                
                # Si 'ultima_transmision_dt' no tiene información de zona horaria, añade una.
                if ultima_transmision_dt.tzinfo is None:
                    ultima_transmision_dt = ultima_transmision_dt.replace(tzinfo=timezone.utc)
                
                diferencia = ahora - ultima_transmision_dt
                if diferencia >= timedelta(hours=24):
                    print("Diferencia:", diferencia, "--", str(timedelta(hours=24)))
                    unidad['ultima_trans'] = formatear_fecha_dd_mm_aaaa(ultima_transmision_dt)
                    unidades_no_transmitiendo.append(unidad)
            except Exception as e:
                print(f"Error al calcular la diferencia para la unidad {unidad}: {e}")

    return unidades_no_transmitiendo

def enviar_mensaje_whatsapp(numero, info_equipos):
    headers = {
        'Authorization': f'Bearer {WHATSAPP_API_TOKEN}',
        'Content-Type': 'application/json'
    }
    data = {
        'messaging_product': 'whatsapp',
        'to': numero,
        'type': 'template',
        'template': {
            'namespace': NAMESPACE,
            'name': TEMPLATE_NAME,
            'language': {
                'policy': 'deterministic',
                'code': 'es'
            },
            'components': [
                {
                    'type': 'body',
                    'parameters': [
                        {
                            'type': 'text',
                            'text': info_equipos  # Directamente como cadena de texto
                        }
                    ]
                }
            ]
        }
    }
    response = requests.post(WHATSAPP_API_URL, headers=headers, json=data)
    
    print(f"Estado de la respuesta: {response.status_code}")
    print(f"Contenido de la respuesta: {response.text}")
    
    return response.status_code

def dividir_en_mensajes(unidades_no_transmitiendo, max_unidades=10):
    mensajes = []
    for i in range(0, len(unidades_no_transmitiendo), max_unidades):
        chunk = unidades_no_transmitiendo[i:i + max_unidades]
        info_equipos = ""
        for unidad in chunk:
            info_equipos += f"Unidad: {unidad['unitnumber']} | Ultima transmision: {unidad['ultima_trans']} | Datos: {unidad['nombre']} || "
        mensajes.append(info_equipos)
    return mensajes

def main():
    unidades = obtener_unidades()
    if unidades:
        ultima_transmision_unidades = obtener_ultima_transmision(unidades)
        print("ultima_transmision_unidades::", ultima_transmision_unidades)
        unidades_no_transmitiendo = obtener_unidades_no_transmitiendo(ultima_transmision_unidades)
        if unidades_no_transmitiendo:
            mensajes = dividir_en_mensajes(unidades_no_transmitiendo)
            for mensaje in mensajes:
                status = enviar_mensaje_whatsapp(Numeros_telefonicos[0], mensaje)
                if status == 200:
                    print(f'Mensaje enviado')
                else:
                    print(f'Error al enviar mensaje')
        else:
            print("Todas las unidades GPS están transmitiendo correctamente.")
    else:
        print("No se pudieron obtener las unidades GPS.")

if __name__ == "__main__":
    main()
