import requests
from datetime import datetime, timedelta, timezone

# Configuración de la API de dispositivos GPS
Xeguridad_API_URL = "https://mongol.brono.com/mongol/api.php"
Xeguridad_USERNAME = "dhnexasa"
Xeguridad_PASSWORD = "dhnexasa2022/487-"

def obtener_datos(unidades):
    # Filtrar unidades que no están transmitiendo en el día anterior completo
    units_data = []

    # Calcular la fecha de ayer
    fecha_ayer = datetime.now() - timedelta(days=1)
    
    # Obtener los tiempos de inicio y fin para el día anterior (desde las 00:00 hasta las 23:59)
    start = fecha_ayer.replace(hour=0, minute=0, second=0).strftime("%Y%m%d%H%M%S")
    end = fecha_ayer.replace(hour=23, minute=59, second=59).strftime("%Y%m%d%H%M%S")

    for unidad in unidades:
        params = {
            'commandname': 'get_historial',
            'user': Xeguridad_USERNAME,
            'pass': Xeguridad_PASSWORD,
            'unitnumber': unidad['unitnumber'],
            'start': start,
            'end': end,
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
                    units_data.append(
                        {'unitnumber': unidad['unitnumber'], 'ultima_trans': ultima_transmision,
                         'nombre': data['name']})
            except Exception as e:
                print(f"Error al procesar las transmisiones: {e}")

    return units_data


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