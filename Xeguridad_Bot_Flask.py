from flask import Flask, request, jsonify, render_template
import requests
import re
from pruebaCrawler import execute_crawler

app = Flask("Xeguridad_Bot_Flask")

# Configura tu verify token aquí
VERIFY_TOKEN = "9189189189"
WHATSAPP_API_URL = "https://graph.facebook.com/v19.0/354178054449225/messages"
WHATSAPP_API_TOKEN = "EAAFiQXfoAV4BO10PdMbULG2wAmGa108puKpkvVzOzWiSMAusEp4xinrQ8DqcORjWZCzQ07DlNIR3jrcsNGbHVFx0zaJOOzn0GurZC0aTCATmCarHUgne5wWhdNp7qDQvpRMZBwFeWOOWC5ZCDpkmfjRUCMG5s51w4YlB7w1XZBdOgqQfENknQ4XdNsNWHQsZBGSQZDZD"
NAMESPACE = "Xeguridad"
MENU_TEMPLATE_NAME = "menu2_xeguridad"  # Asegúrate de que este nombre coincida con el de tu plantilla de menú
SOLICITUD_UNIDAD_COMANDOS_TEMPLATE_NAME = "solicitud_unidad_comandos"  # Nombre de la plantilla para solicitud de comandos a unidad
XEGURIDAD_API_URL = "https://mongol.brono.com/mongol/api.php"
XEGURIDAD_USERNAME = "dhnexasa"
XEGURIDAD_PASSWORD = "dhnexasa2022/487-"

# Diccionario para rastrear números de teléfono que esperan una placa
esperando_placa = {}

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
    cuerpo_mensaje = ""

    if mensaje['type'] == 'button':
        cuerpo_mensaje = mensaje['button']['payload'].lower()
    else:
        cuerpo_mensaje = mensaje.get('text', {}).get('body', '').lower()

    print(f"Cuerpo del mensaje: {cuerpo_mensaje}")

    if cuerpo_mensaje == "mandar comandos a unidad":
        manejar_respuesta_usuario(numero, SOLICITUD_UNIDAD_COMANDOS_TEMPLATE_NAME)
        esperando_placa[numero] = True
    elif numero in esperando_placa:
        placa = cuerpo_mensaje.upper()
        print(f"Placa detectada: {placa}")
        unitnumber = buscar_unitnumber_por_placa(placa)
        if unitnumber:
            # Solo imprimir el unitnumber en consola
            print(f"El unitnumber para la placa {placa} es {unitnumber}.")
            execute_crawler(unitnumber)
            
        else:
            # Informar que no se encontró el unitnumber
            print(f"No se encontró el unitnumber para la placa {placa}.")
        del esperando_placa[numero]  # Eliminamos el número de teléfono del diccionario
    else:
        print("Cuerpo del mensaje no coincide con la expresión regular o no se está esperando una placa.")
        components = []  # No enviar parámetros si la plantilla no los espera
        response_status = enviar_mensaje_whatsapp(numero, MENU_TEMPLATE_NAME, components)
        print(f"Estado de la respuesta al enviar mensaje: {response_status}")

def manejar_respuesta_usuario(numero, template_name):
    components = []  # Añadir los parámetros necesarios si los hay
    response_status = enviar_mensaje_whatsapp(numero, template_name, components)
    print(f"Estado de la respuesta al enviar mensaje: {response_status}")

def buscar_unitnumber_por_placa(placa):
    params = {
        'commandname': 'get_units',
        'user': XEGURIDAD_USERNAME,
        'pass': XEGURIDAD_PASSWORD,
        'format': 'json1'
    }
    response = requests.get(XEGURIDAD_API_URL, params=params)
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

def enviar_mensaje_whatsapp(numero, template_name, components):
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
            'name': template_name,
            'language': {
                'policy': 'deterministic',
                'code': 'es'
            },
            'components': components
        }
    }
    response = requests.post(WHATSAPP_API_URL, headers=headers, json=data)
    print(f"Estado de la respuesta: {response.status_code}")
    print(f"Contenido de la respuesta: {response.text}")
    return response.status_code

@app.route('/')
def home():
    return "Servidor Flask en funcionamiento."

@app.route('/politica_privacidad', methods=['GET'])
def politica_privacidad():
    return render_template('PoliticasSeguridad.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
