from flask import Flask, request, jsonify, render_template
from whatsapp import enviar_auth_template, enviar_auth_failed_template, enviar_menu_template, enviar_solicitud_unidad_comandos_template, enviar_cargando_comandos_template, enviar_placa_no_encontrada_template, enviar_respuesta_comandos_template, enviar_comando_no_recibido_template
from datetime import datetime
from datetime import datetime, timedelta
from BotCrawler import execute_crawler
from utils import extraer_placa
import requests
import bcrypt
from pymongo import MongoClient
import re
from UnitsData import obtener_datos, obtener_unidades
from flask import Flask, send_from_directory
import os

VERIFY_TOKEN = "9189189189"
WHATSAPP_API_URL = "https://graph.facebook.com/v19.0/354178054449225/messages"
WHATSAPP_API_TOKEN = "EAAFiQXfoAV4BO10PdMbULG2wAmGa108puKpkvVzOzWiSMAusEp4xinrQ8DqcORjWZCzQ07DlNIR3jrcsNGbHVFx0zaJOOzn0GurZC0aTCATmCarHUgne5wWhdNp7qDQvpRMZBwFeWOOWC5ZCDpkmfjRUCMG5s51w4YlB7w1XZBdOgqQfENknQ4XdNsNWHQsZBGSQZDZD"
XEGURIDAD_API_URL = "https://mongol.brono.com/mongol/api.php"
XEGURIDAD_USERNAME = "dhnexasa"
XEGURIDAD_PASSWORD = "dhnexasa2022/487-"
USUARIO_MONGO = "exasa"
PASSWORD_MONGO = os.getenv("MONGO_DB_PASSWORD")
PASSWORD_MONGO_ESCAPADA = (PASSWORD_MONGO)
BASE_DATOS_MONGO = "XeguridadBotDB"
AUTH_DB = "admin"

app = Flask("Xeguridad_Bot_Flask")

# Diccionario para rastrear números de teléfono que esperan una placa
esperando_placa = {}

# Diccionario para almacenar los últimos mensajes procesados
ultimos_mensajes = {}

# Variables globales para almacenar datos
user_requests = {}

usuarios_autenticados = {}

usuarios_esperando_password = {}

uri = f"mongodb://{USUARIO_MONGO}:{PASSWORD_MONGO_ESCAPADA}@localhost:27017/{BASE_DATOS_MONGO}?authSource={AUTH_DB}"

# Conexion a MongoDB con manejo de excepciones
try:
    client = MongoClient(uri)
    db = client[BASE_DATOS_MONGO]
    collectionUsuarios = db['usuarios']
    print("Conexión a MongoDB exitosa.")
except Exception as e:
    print(f"Error al conectar a MongoDB: {e}")

def check_password(stored_hash: bytes, provided_password: str) -> bool:
    if isinstance(stored_hash, str):
        stored_hash = stored_hash.encode('utf-8')
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_hash)


def autenticar_usuario(username: str, password: str) -> bool:
    # Busca el usuario por el número de teléfono
    usuario = collectionUsuarios.find_one({'telefono': username})
    
    # Verifica si se encontró el usuario
    if usuario:
        stored_hash = usuario['password']
        print(f"Contraseña en mongo: {stored_hash}, contraseña ingresada: {password}")
        
        # Verifica si la contraseña ingresada coincide con el hash almacenado
        if check_password(stored_hash, password):
            usuarios_autenticados[username] = datetime.now()
            return True
    
    # Si el usuario no se encuentra o la contraseña no coincide, retorna False
    return False

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        # Verificación del webhook
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        if token == VERIFY_TOKEN:
            return str(challenge)
        return "Verificación de token fallida", 403
    elif request.method == 'POST':
        # Manejo de mensajes entrantes
        data = request.json
        print(f"Datos recibidos: {data}")

        if 'entry' in data:
            for entry in data['entry']:
                if 'changes' in entry:
                    for change in entry['changes']:
                        if 'value' in change:
                            value = change['value']
                            if 'messages' in value:
                                for message in value['messages']:
                                    manejar_mensaje_entrante(message)
        return jsonify({'status': 'success'}), 200
    
    
def manejar_mensaje_entrante(mensaje):
    print(f"Manejando mensaje entrante: {mensaje}")
    numero = mensaje['from']
    message_id = mensaje.get('id')
    cuerpo_mensaje = " "
    usuario = collectionUsuarios.find_one({'telefono': numero})
    components = []

    if usuario:
        # Si el usuario es encontrado, puedes acceder a su nombre
        nombre_usuario = usuario['nombre']
        print(f"Nombre del usuario: {nombre_usuario}")
    else:
        # Si el usuario no es encontrado
        print("Usuario no encontrado.")

    # Evitar procesar el mismo mensaje dos veces
    if numero in ultimos_mensajes and ultimos_mensajes[numero] == message_id:
        print(f"Mensaje duplicado detectado: {message_id}")
        return
    ultimos_mensajes[numero] = message_id

    # Detectar tipo de mensaje y obtener el cuerpo del mensaje
    if mensaje['type'] == 'button':
        cuerpo_mensaje = mensaje['button']['payload']
    else:
        cuerpo_mensaje = mensaje.get('text', {}).get('body', '')

    print(f"Cuerpo del mensaje: {cuerpo_mensaje}")

    # Verificar autenticación del usuario
    if numero in usuarios_autenticados:
        hora_autenticacion = usuarios_autenticados[numero]
        
        # Verificar si la sesión ha expirado (más de 24 horas)
        if datetime.now() - hora_autenticacion > timedelta(hours=24):
            print("Sesión expirada. El usuario necesita autenticarse de nuevo.")
            del usuarios_autenticados[numero]
            enviar_auth_template(numero)  # Envía mensaje solicitando autenticación
            return
        
        # Si el usuario está autenticado, manejar comandos
        if cuerpo_mensaje.strip():  # Si el mensaje no está vacío
            if cuerpo_mensaje == "Mandar comandos a unidad":
                enviar_solicitud_unidad_comandos_template(numero)
                esperando_placa[numero] = True
            elif numero in esperando_placa:
                placa = cuerpo_mensaje.upper()
                print(f"Placa detectada: {placa}")
                unitnumber = buscar_unitnumber_por_placa(placa)
                if unitnumber:
                    print(f"El unitnumber para la placa {placa} es {unitnumber}.")
                    user_requests[numero] = {
                        "placa": placa,
                        "hora": datetime.now()
                    }
                    # enviar_cargando_comandos(numero, CARGANDO_COMANDOS_TEMPLATE_NAME, components, placa) 
                    enviar_cargando_comandos_template(numero) # Enviar plantilla de cargando
                    if execute_crawler(unitnumber):
                        print("Crawler ejecutado correctamente.")
                        obtener_ultima_transmision(unitnumber, numero)
                    else:
                        print("Error al ejecutar el crawler.")
                else:
                    print(f"No se encontró el unitnumber para la placa {placa}.")
                    enviar_placa_no_encontrada_template(numero)
                del esperando_placa[numero]  # Eliminamos el número de teléfono del diccionario
            else:
                print("Cuerpo del mensaje no coincide con la expresión regular o no se está esperando una placa.")
                # enviar_menu(numero, MENU_TEMPLATE_NAME, components, nombre_usuario)
                enviar_menu_template(numero)  # Envía el menú de opciones
    
    else:
        # Usuario no autenticado
        if numero not in usuarios_esperando_password:
            # Envía la plantilla solicitando la contraseña
            enviar_auth_template(numero)
            usuarios_esperando_password[numero] = True  # Ahora está esperando una contraseña
        else:
            # El usuario ha enviado la contraseña, ahora la autenticamos
            if autenticar_usuario(numero, cuerpo_mensaje):
                print("Autenticación exitosa. Bienvenido.")
                # enviar_menu(numero, MENU_TEMPLATE_NAME, components, nombre_usuario)  
                enviar_menu_template(numero) # Envía el menú de opciones tras autenticación
                del usuarios_esperando_password[numero]  # Ya no está esperando la contraseña
            else:
                print("Autenticación fallida. Usuario o contraseña incorrectos.")
                enviar_auth_failed_template(numero)  # Envía mensaje de fallo de autenticación
                del usuarios_esperando_password[numero]  # Resetear el proceso de autenticación


def buscar_unitnumber_por_placa(placa):
    response = requests.get("https://mongol.brono.com/mongol/api.php", params={
        'commandname': 'get_units',
        'user': "dhnexasa",
        'pass': "dhnexasa2022/487-",
        'format': 'json1'
    })
    if response.status_code == 200:
        unidades = response.json()
        for unidad in unidades:
            if extraer_placa(unidad['name']) == placa:
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
        'user': XEGURIDAD_USERNAME,
        'pass': XEGURIDAD_PASSWORD,
        'format': 'json1'
    }
    response = requests.get(XEGURIDAD_API_URL, params=params)
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
            components = []

            hora_envio_placa = user_requests[numero]['hora']
            if fecha_hora_obj >= hora_envio_placa:
                #numero, RESPUESTA_COMANDOS_TEMPLATE, longitud, latitud, address, components, datetime_actual
                # enviar_ubicacion_comando(numero, RESPUESTA_COMANDOS_TEMPLATE, longitud, latitud, address, components, fecha_hora_obj)
                enviar_respuesta_comandos_template(numero, transmision["longitude"], transmision["latitude"], transmision.get("address"), [], fecha_hora_obj)
            else:
                
                print("PLACA::",placa)
                enviar_comando_no_recibido_template(numero, transmision["longitude"], transmision["latitude"], transmision.get("address"), [], datetime_actual, placa)
        else:
            return "No se encontró la última transmisión."
    else:
        return "No se pudo obtener la última transmisión."    
    
    # Eliminar el número de esperando_placa si el mensaje se envió correctamente
    if response.status_code == 200:
        if numero in esperando_placa:
            del esperando_placa[numero]
            print(f"Número {numero} eliminado de esperando_placa")
    else:
        print(f"Error al enviar mensaje, estado de la respuesta: {response.status_code}")
    return response.status_code

#######################################################################################################

@app.route('/templates/politica_privacidad', methods=['GET'])
def politica_privacidad():
    return render_template('PoliticasSeguridad.html')

@app.route('/test_mongodb', methods=['GET'])
def test_mongodb_connection():
    if db is None:
        return jsonify({'status': 'error', 'message': 'No se pudo conectar a la base de datos.'}), 500
    try:
        # Realiza una consulta simple para verificar la conexión
        db.command('ping')
        usuarioPrueba = collectionUsuarios.find_one({"telefono": "50497338021"})
        if usuarioPrueba:
            return jsonify({'status': 'success', 'data': serialize_document(usuarioPrueba)}), 200
        else:
            return jsonify({'status': 'success', 'message': 'Usuario no encontrado.'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    
@app.route('/logo_xeguridad')
def mostrar_imagen():
    # 'static' es la carpeta en la que está almacenada la imagen
    return send_from_directory('static', 'logo_xeguridad.png')

@app.route('/units_data', methods=['GET'])
def obtener_datos_route():
    unidades = obtener_unidades()
    if unidades:
        datos = obtener_datos(unidades)
        return jsonify(datos)  # Devuelve los datos en formato JSON
    else:
        return jsonify({'error': 'No se encontraron unidades o hubo un problema con la solicitud'}), 404
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)
