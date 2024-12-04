from Config import Config
from Users import UsuarioManager
from Utils import envioTemplateTxt
from DenunciasReclamos_SMTP import enviar_queja_anonima
from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient

config = Config()

ultimos_mensajes = {}

esperando_denuncia = {}

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
    print ("Webhook recibido")
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

    # Manejo de mensajes duplicados
    if numero in ultimos_mensajes and ultimos_mensajes[numero] == message_id:
        print(f"Mensaje duplicado detectado: {message_id}")
        return
    ultimos_mensajes[numero] = message_id 

    # Detecta si es primera vez que el usuario envía un mensaje para enviar starter_menu
    if usuario_manager.manejar_inicio(numero):
        return
    
    # Detectar tipo de mensaje y obtener el cuerpo del mensaje
    if mensaje['type'] == 'button':
        cuerpo_mensaje = mensaje['button']['payload']
    else:   
        cuerpo_mensaje = mensaje.get('text', {}).get('body', '')

    print(f"Cuerpo del mensaje: {cuerpo_mensaje}")

    if cuerpo_mensaje.strip().lower() == "xeguridad":
        if not usuario_manager.manejar_respuesta_autenticacion(numero, cuerpo_mensaje):
            return
        envioTemplateTxt(numero, config.MENU_TEMPLATE_NAME, [])  # Enviar menú principal
        return
    
    if cuerpo_mensaje.strip().lower() == "denuncias o reclamos":
        print("El usuario ha seleccionado la opción de 'denuncias o reclamos'")
        envioTemplateTxt(numero, config.COMPLAINT_CLAIMS_TEMPLATE, [])  # Enviar plantilla de denuncias/reclamos
        esperando_denuncia[numero] = True
    elif numero in esperando_denuncia:
        denuncia= cuerpo_mensaje
        print(f"Denuncia recibida: {denuncia}")
        enviar_queja_anonima(denuncia)  # Llama a la función que envía la denuncia por correo
        print("Llamada a enviar_queja_anonima realizada")
        envioTemplateTxt(numero, config.COMPLAINT_CLAIMS_NOTIFICATION_TEMPLATE, components)
        components = [
            {
                "type": "body",
                    "parameters": components + [
                        {
                            "type": "text",
                            "text": denuncia
                        },
                    ]
            }
        ]
        return jsonify({"status": "denuncia recibida y enviada por correo"}), 200
    else:
        print("El mensaje no es una denuncia o reclamo.")
        return jsonify({"error": "no se encontró el campo 'denuncia' en el request"}), 400

    if usuario_manager.usuario_autenticado(numero):
        # Lógica para usuarios autenticados
        #manejar_comandos_autenticados(numero, cuerpo_mensaje)
        print("Usuario autenticado. Procesando comandos.")
    else:
        print("Usuario no autenticado. Solicitando autenticación.")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=config.PORT)  # Ejecutar la aplicación en el puerto segun la variable de entorno del ambiente

