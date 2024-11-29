from Config import Config
from Users import UsuarioManager
from Utils import envioTemplateTxt
from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient

config = Config()

ultimos_mensajes = {}

app = Flask("Xeguridad_Bot_Main")

# Conexion a MongoDB con manejo de excepciones
try:
    client = MongoClient(config.mongo_uri())
    db = client[config.BASE_DATOS_MONGO]
    usuario_manager = UsuarioManager(db)
    print("Conexión a MongoDB exitosa.")
except Exception as e:
    print(f"Error al conectar a MongoDB: {e}")

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        # Verificación del webhook
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        print("Token webhook:",token)
        print("Challenge webhook:",challenge)
        if token == config.VERIFY_TOKEN:
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
    usuario = usuario_manager.buscar_usuario_por_telefono(numero)
    cuerpo_mensaje = ""

    if numero in ultimos_mensajes and ultimos_mensajes[numero] == message_id:
        print(f"Mensaje duplicado detectado: {message_id}")
        return
    ultimos_mensajes[numero] = message_id 

    if usuario_manager.manejar_inicio(numero):
        return
    
    if mensaje['type'] == 'button':
        cuerpo_mensaje = mensaje['button']['payload']
    else:   
        cuerpo_mensaje = mensaje.get('text', {}).get('body', '')

    print(f"Cuerpo del mensaje: {cuerpo_mensaje}")

    if cuerpo_mensaje.strip().lower() == "xeguridad":
        if not usuario_manager.manejar_respuesta_autenticacion(numero, cuerpo_mensaje):
            return
        envioTemplateTxt(numero, config.MENU_TEMPLATE_NAME)
        return

    if usuario_manager.usuario_autenticado(numero):
        # Lógica para usuarios autenticados
        #manejar_comandos_autenticados(numero, cuerpo_mensaje)
        print("Usuario autenticado. Procesando comandos.")
    else:
        print("Usuario no autenticado. Solicitando autenticación.")

