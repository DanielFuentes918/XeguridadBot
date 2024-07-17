import requests
from datetime import datetime, timedelta, timezone
import re

# Configuración de la API de WhatsApp
WHATSAPP_API_URL = "https://graph.facebook.com/v19.0/354178054449225/messages"
WHATSAPP_API_TOKEN = "EAAFiQXfoAV4BO10PdMbULG2wAmGa108puKpkvVzOzWiSMAusEp4xinrQ8DqcORjWZCzQ07DlNIR3jrcsNGbHVFx0zaJOOzn0GurZC0aTCATmCarHUgne5wWhdNp7qDQvpRMZBwFeWOOWC5ZCDpkmfjRUCMG5s51w4YlB7w1XZBdOgqQfENknQ4XdNsNWHQsZBGSQZDZD"
NAMESPACE = "Xeguridad"
TEMPLATE_NAME = "notificacion10u_xeguridad"

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

        if response.status_code == 200:
            try:
                transmisiones = response.json()
                for data in transmisiones:
                    # Guardar la última transmisión
                    ultima_transmision = data['datetime_utc']
                    # Imprimir la última transmisión obtenida
                    print(f"Unidad: {unidad['unitnumber']} - Última transmisión: {ultima_transmision}")
                    ultima_transmision_unidades.append({'unitnumber':unidad['unitnumber'], 'ultima_trans':ultima_transmision, 'nombre':data['name']})
            except Exception as e:
                print(f"Error al procesar las transmisiones: {e}")

    return ultima_transmision_unidades

def obtener_unidades_no_transmitiendo(ultima_transmision_unidades):
    unidades_no_transmitiendo = []
    ahora = datetime.now(timezone.utc)  # Asegurando que 'ahora' tiene información de zona horaria
    
    for unidad in ultima_transmision_unidades:
        if unidad['ultima_trans']:
            try:
                ultima_transmision_dt = formateando_fecha(unidad['ultima_trans'])
                
                # Si 'ultima_transmision_dt' no tiene información de zona horaria, añade una.
                if ultima_transmision_dt.tzinfo is None:
                    ultima_transmision_dt = ultima_transmision_dt.replace(tzinfo=timezone.utc)
                
                diferencia = ahora - ultima_transmision_dt
                if diferencia >= timedelta(hours=24):
                    unidad['ultima_trans'] = formatear_fecha_dd_mm_aaaa(ultima_transmision_dt)
                    unidades_no_transmitiendo.append(unidad)
            except Exception as e:
                print(f"Error al calcular la diferencia para la unidad {unidad}: {e}")

    return unidades_no_transmitiendo

def enviar_mensaje_whatsapp(numero, variables):
    headers = {
        'Authorization': f'Bearer {WHATSAPP_API_TOKEN}',
        'Content-Type': 'application/json'
    }
    components = {
        'type': 'body',
        'parameters': [{'type': 'text', 'text': variables[f'var{i}']} for i in range(1, 11)]
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
            'components': [components]
        }
    }
    response = requests.post(WHATSAPP_API_URL, headers=headers, json=data)
    
    print(f"Estado de la respuesta: {response.status_code}")
    print(f"Contenido de la respuesta: {response.text}")
    
    return response.status_code

def extraer_placa(nombre):
    match = re.search(r'\b[A-Z]{3}\d{4}\b', nombre)
    return match.group(0) if match else nombre  # Retorna el nombre completo si no se encuentra placa

def dividir_en_mensajes(unidades_no_transmitiendo, max_unidades=10):
    mensajes = []
    contador_global = 1  # Iniciar el contador global
    for i in range(0, len(unidades_no_transmitiendo), max_unidades):
        chunk = unidades_no_transmitiendo[i:i + max_unidades]
        variables = {}
        for index, unidad in enumerate(chunk):
            key = f'var{index + 1}'
            placa = extraer_placa(unidad['nombre'])
            variables[key] = f"*{contador_global})* Unidad: {placa} con dispositivo: {unidad['unitnumber']} no transmite desde: {unidad['ultima_trans']}"
            contador_global += 1  # Incrementar el contador global
        
        # Añadir variables vacías si hay menos de 10 unidades en el último grupo
        for j in range(len(chunk), 10):
            variables[f'var{j + 1}'] = "."

        mensajes.append(variables)
    return mensajes

def main():
    unidades = obtener_unidades()
    if unidades:
        ultima_transmision_unidades = obtener_ultima_transmision(unidades)
        unidades_no_transmitiendo = obtener_unidades_no_transmitiendo(ultima_transmision_unidades)
        if unidades_no_transmitiendo:
            mensajes = dividir_en_mensajes(unidades_no_transmitiendo)
            for mensaje in mensajes:
                status = enviar_mensaje_whatsapp(Numeros_telefonicos[0], mensaje)
                if status == 200:
                    print('Mensaje enviado')
                else:
                    print('Error al enviar mensaje')
        else:
            print("Todas las unidades GPS están transmitiendo correctamente.")
    else:
        print("No se pudieron obtener las unidades GPS.")

if __name__ == "__main__":
    main()
