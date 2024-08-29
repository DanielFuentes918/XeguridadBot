import requests
from datetime import datetime, timedelta

# Configuración de la API de dispositivos GPS
Xeguridad_API_URL = "https://mongol.brono.com/mongol/api.php"
Xeguridad_USERNAME = "dhnexasa"
Xeguridad_PASSWORD = "dhnexasa2022/487-"

def obtener_datos(unidades):
    units_data = []

    # Calcular las fechas de inicio y fin de acuerdo al formato requerido por la API
    start = (datetime.now() - timedelta(days=1)).replace(hour=0, minute=0, second=0).strftime("%Y%m%d%H%M%S")
    end = (datetime.now() - timedelta(days=1)).replace(hour=23, minute=59, second=59).strftime("%Y%m%d%H%M%S")

    for unidad in unidades:
        # Construcción del URL con los parámetros correctos
        params = {
            'commandname': 'get_history',
            'user': Xeguridad_USERNAME,
            'pass': Xeguridad_PASSWORD,
            'unitnumber': unidad['unitnumber'],
            'start': start,
            'end': end,
            'format': 'json1'
        }

        response = requests.get(Xeguridad_API_URL, params=params)
        print(f"Estado de la respuesta: {response.status_code}")
        print(f"Contenido de la respuesta: {response.text}")

        if response.status_code == 200:
            try:
                transmisiones = response.json()
                transmisiones = transmisiones.unidad=unidad['unitnumber']

                # if isinstance(transmisiones, list) and len(transmisiones) > 0:
                #     for data in transmisiones:
                #         # Verificar si las claves existen antes de acceder a ellas
                #         ultima_transmision = data.get('datetime_utc', 'Desconocido')
                #         nombre_unidad = data.get('name', 'Nombre no disponible')
                #         units_data.append({'unitnumber': unidad['unitnumber'], 'ultima_trans': ultima_transmision, 'nombre': nombre_unidad})
                # else:
                #     print(f"No hay transmisiones para la unidad {unidad['unitnumber']}")
            except Exception as e:
                print(f"Error al procesar las transmisiones: {e}")
        else:
            print(f"Error en la solicitud: {response.status_code} - {response.text}")

    return transmisiones

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
    else:
        return []

def main():
    # Llamar a la función para obtener todas las unidades
    unidades = obtener_unidades()

    if unidades:
        # Llamar a la función para obtener los datos de cada unidad
        datos_unidades = obtener_datos(unidades)
        print(f"Datos de las unidades: {datos_unidades}")
    else:
        print("No se obtuvieron unidades.")