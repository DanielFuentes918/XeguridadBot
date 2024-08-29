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
                # Convertir la respuesta a JSON
                transmisiones = response.json()

                # Asegurarse de que transmisiones sea una lista o convertirla en una
                if isinstance(transmisiones, list):
                    for data in transmisiones:
                        # Añadir el número de unidad a cada registro de transmisión
                        data['unitnumber'] = unidad['unitnumber']
                    units_data.extend(transmisiones)  # Agregar las transmisiones procesadas
                else:
                    # Si no es una lista, crear una lista con el único elemento
                    units_data.append(transmisiones)
                    units_data[-1]['unitnumber'] = unidad['unitnumber']
                    
            except Exception as e:
                print(f"Error al procesar las transmisiones: {e}")
        else:
            print(f"Error en la solicitud: {response.status_code} - {response.text}")

    return units_data  # Retornar todos los datos de las unidades

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
