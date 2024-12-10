import os
import subprocess
from threading import Thread
from datetime import datetime
from Config import Config
from Users import UsuarioManager
from Utils import envioTemplateTxt, buscar_unitnumber_por_placa, obtener_ultima_transmision
from DenunciasReclamos_SMTP import enviar_queja_anonima
from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from XeguridadCrawler import execute_crawler
config = Config()

ultimos_mensajes = {}

esperando_denuncia = {}

esperando_placa = {}

user_requests = {}

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
    elif cuerpo_mensaje.strip().lower() == "denuncias o reclamos":
        print("El usuario ha seleccionado la opción de 'denuncias o reclamos'")
        envioTemplateTxt(numero, config.COMPLAINT_CLAIMS_TEMPLATE, [])  # Enviar plantilla de denuncias/reclamos
        esperando_denuncia[numero] = True
    elif numero in esperando_denuncia:
        denuncia= cuerpo_mensaje
        print(f"Denuncia recibida: {denuncia}")
        enviar_queja_anonima(denuncia)  # Llama a la función que envía la denuncia por correo
        print("Llamada a enviar_queja_anonima realizada")
        components = [
            {
                "type": "body",
                    "parameters": [
                        {
                            "type": "text",
                            "text": denuncia
                        },
                    ]
            }
        ]
        envioTemplateTxt(numero, config.COMPLAINT_CLAIMS_NOTIFICATION_TEMPLATE, components)
        return jsonify({"status": "denuncia recibida y enviada por correo"}), 200
    else:
        envioTemplateTxt(numero, config.STARTER_MENU_TEMPLATE, [])
        print("El mensaje no es una denuncia o reclamo.")
        return jsonify({"error": "no se encontró el campo 'denuncia' en el request"}), 400

    # Verificar autenticación del usuario
    if usuario_manager.usuario_autenticado(numero):
        # Lógica para usuarios autenticados
        #manejar_comandos_autenticados(numero, cuerpo_mensaje)
        print("Usuario autenticado. Procesando comandos.")
    else:
        print("Usuario no autenticado. Solicitando autenticación.")

    # Manejo de comandos
    if cuerpo_mensaje.strip(): 
            if cuerpo_mensaje == "Mandar comandos a unidad":
                envioTemplateTxt(numero, config.SOLICITUD_UNIDAD_COMANDOS_TEMPLATE_NAME, [])
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
                    envioTemplateTxt(numero, config.CARGANDO_COMANDOS_TEMPLATE_NAME, [])
                    if execute_crawler(unitnumber):
                        print("Crawler ejecutado correctamente.")
                        obtener_ultima_transmision(unitnumber, numero)
                    else:
                        print("Error al ejecutar el crawler.")
                else:
                    print(f"No se encontró el unitnumber para la placa {placa}.")
                    components = [
                        {
                            "type": "body",
                            "parameters": components + [
                                {
                                    "type": "text",
                                    "text": placa
                                },
                            ]
                        }    
                    ]
                    envioTemplateTxt(numero, config.PLACA_NO_ENCONTRADA_TEMPLATE,components)
                del esperando_placa[numero]  
            else:
                print("Cuerpo del mensaje no coincide con la expresión regular o no se está esperando una placa.")
                #envioTemplateTxt(numero, config.MENU_TEMPLATE_NAME, [])

@app.route('/')
def home():
    return "Servidor Flask en funcionamiento."

@app.route('/politica_privacidad', methods=['GET'])
def politica_privacidad():
    return render_template('PoliticasSeguridad.html')

@app.route('/pull', methods=['GET','POST'])
def pull():    

    # Responder inmediatamente al webhook de GitHub
    response = {"status": "success", "message": "Operación recibida y en proceso."}
    # Enviar la respuesta inmediatamente
    try:
        # Usar un hilo para ejecutar las operaciones si es necesario (alternativa)
        def execute_operations():
            try:
                repo_path = os.getenv("repo_path")
                service = os.getenv("service")
                os.chdir(repo_path)

                # Ejecutar git pull
                pull_result = subprocess.run(["git", "pull"], capture_output=True, text=True)
                print(f"Git pull stdout: {pull_result.stdout}")
                print(f"Git pull stderr: {pull_result.stderr}")

                # Verificar si git pull tuvo éxito
                if pull_result.returncode != 0:
                    print(f"Error al ejecutar git pull: {pull_result.stderr}")

                # Reiniciar el servicio
                restart_result = subprocess.run(["sudo", "systemctl", "restart", service], capture_output=True, text=True)
                print(f"Service restart stdout: {restart_result.stdout}")
                print(f"Service restart stderr: {restart_result.stderr}")

                if restart_result.returncode != 0:
                    print(f"Error al reiniciar el servicio: {restart_result.stderr}")

            except Exception as e:
                print(f"Excepción al ejecutar operaciones: {e}")

        # Ejecutar las operaciones en un hilo separado para no bloquear la respuesta
        Thread(target=execute_operations).start()  # Usa hilos si quieres ejecutar en segundo plano

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Ocurrió un error: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=config.PORT)  # Ejecutar la aplicación en el puerto segun la variable de entorno del ambiente

