import requests
from datetime import datetime, timedelta, timezone

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
            'start': start,  # Formato YYYYMMDDHHMMSS para el inicio
            'end': end,  # Formato YYYYMMDDHHMMSS para el fin
            'format': 'json1'
        }

        response = requests.get(Xeguridad_API_URL, params=params)
        print(f"Estado de la respuesta: {response.status_code}")
        print(f"Contenido de la respuesta: {response.text}")  # Imprimir el contenido completo de la respuesta

        if response.status_code == 200:
            try:
                transmisiones = response.json()

                if isinstance(transmisiones, list) and len(transmisiones) > 0:
                    for data in transmisiones:
                        # Verificar si las claves existen antes de acceder a ellas
                        ultima_transmision = data.get('datetime_utc', 'Desconocido')
                        nombre_unidad = data.get('name', 'Nombre no disponible')  # Verifica si existe la clave 'name'
                        units_data.append({'unitnumber': unidad['unitnumber'], 'ultima_trans': ultima_transmision, 'nombre': nombre_unidad})
                else:
                    print(f"No hay transmisiones para la unidad {unidad['unitnumber']}")

            except Exception as e:
                print(f"Error al procesar las transmisiones: {e}")
        else:
            print(f"Error en la solicitud: {response.status_code} - {response.text}")

    return units_data
