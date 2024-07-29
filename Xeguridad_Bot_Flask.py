from flask import Flask, request, jsonify
import requests

app = Flask("Xeguridad_Bot_Flask")

# Configura tu verify token aquí
VERIFY_TOKEN = "9189189189"
WHATSAPP_API_URL = "https://graph.facebook.com/v19.0/354178054449225/messages"
WHATSAPP_API_TOKEN = "EAAFiQXfoAV4BO10PdMbULG2wAmGa108puKpkvVzOzWiSMAusEp4xinrQ8DqcORjWZCzQ07DlNIR3jrcsNGbHVFx0zaJOOzn0GurZC0aTCATmCarHUgne5wWhdNp7qDQvpRMZBwFeWOOWC5ZCDpkmfjRUCMG5s51w4YlB7w1XZBdOgqQfENknQ4XdNsNWHQsZBGSQZDZD"
NAMESPACE = "Xeguridad"
MENU_TEMPLATE_NAME = "menu_xeguridad"  # Asegúrate de que este nombre coincida con el de tu plantilla de menú

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
    components = {
        'type': 'body',
        'parameters': [
            {'type': 'text', 'text': '¡Hola, bienvenido! Soy Xegurbot, ¿en qué te puedo ayudar el día de hoy?'}
        ]
    }
    response_status = enviar_mensaje_whatsapp(numero, MENU_TEMPLATE_NAME, components)
    print(f"Estado de la respuesta al enviar mensaje: {response_status}")

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
            'components': [components]
        }
    }
    response = requests.post(WHATSAPP_API_URL, headers=headers, json=data)
    print(f"Estado de la respuesta: {response.status_code}")
    print(f"Contenido de la respuesta: {response.text}")
    return response.status_code

@app.route('/')
def home():
    return "Servidor Flask en funcionamiento."

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)






