import os
import subprocess
from threading import Thread
from datetime import datetime
from Config import Config
from Users import UsuarioManager
from Utils import envioTemplateTxt, buscar_unitnumber_por_placa, obtener_ultima_transmision, descargar_imagen
from DenunciasReclamos_SMTP import enviar_queja_anonima
from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from XeguridadCrawler import execute_crawler
config = Config()

ultimos_mensajes = {}

esperando_denuncia = {}

esperando_placa = {}

user_requests = {}

denuncia = {}

imagenes = {}

empresa = {}

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
    cuerpo_mensaje = ""

    if cuerpo_mensaje.lower().lstrip() == "Volver a menú principal":
        envioTemplateTxt(numero, config.STARTER_MENU_TEMPLATE, [])
        return

    # Manejo de mensajes duplicados
    if numero in ultimos_mensajes and ultimos_mensajes[numero] == message_id:
        print(f"Mensaje duplicado detectado: {message_id}")
        return
    ultimos_mensajes[numero] = message_id

    # Manejar diferentes tipos de mensajes
    if mensaje['type'] == 'text':
        cuerpo_mensaje = mensaje['text']['body']
    elif mensaje['type'] == 'image':
        media_id = mensaje['image']['id']
        cuerpo_mensaje = mensaje['image']['caption']
        # Usar la función de descarga desde Utils
        imagen_path = descargar_imagen(media_id, config.WHATSAPP_API_TOKEN)
        if numero not in imagenes:
            imagenes[numero] = []
        if imagen_path:
            imagenes[numero].append(imagen_path)
        print(f"Imagen asociada al usuario {numero}: {imagen_path}")
        return  # No procesar más si es una imagen

    # Detectar tipo de mensaje y obtener el cuerpo del mensaje
    if mensaje['type'] == 'button':
        cuerpo_mensaje = mensaje['button']['payload']
    else:   
        cuerpo_mensaje = mensaje.get('text', {}).get('body', '').strip()

    print(f"Cuerpo del mensaje: {cuerpo_mensaje}")

    # Manejar opción de "denuncia o reclamos"
    if cuerpo_mensaje.lower() == "denuncias o reclamos":
        print("Enviando plantilla de selección de compañía...")
        envioTemplateTxt(numero, config.COMPANY_SELECTION_TEMPLATE, [])
        empresa[numero] = None  # Estado de selección de empresa
        esperando_denuncia[numero] = False
        denuncia[numero] = []
        imagenes[numero] = []
        return

    # Manejar selección de compañía
    if numero in empresa and empresa[numero] is None:
        if cuerpo_mensaje.lower() in ["exa", "conmoxa"]:
            empresa[numero] = cuerpo_mensaje.upper()
            print(f"Empresa seleccionada: {empresa[numero]}")
            envioTemplateTxt(numero, config.COMPLAINT_CLAIMS_TEMPLATE, [])  # Solicitar denuncia/reclamo
            esperando_denuncia[numero] = True
            return
        else:
            envioTemplateTxt(numero, config.COMPANY_SELECTION_TEMPLATE, [])
            print("Respuesta inválida para selección de empresa.")
            return

    # Recepción de denuncia o reclamo
    if numero in esperando_denuncia and esperando_denuncia[numero]:
        if cuerpo_mensaje.lower() == "enviar":
            if denuncia[numero] or imagenes[numero]:
                # Concatenar mensajes de denuncia
                denuncia_concatenada = "\n".join(denuncia[numero])
                enviar_queja_anonima(denuncia_concatenada, imagenes[numero], empresa[numero])
                print(f"Denuncia enviada para empresa {empresa[numero]}.")

                # Limpiar estado
                del esperando_denuncia[numero]
                del empresa[numero]
                del denuncia[numero]
                for img in imagenes.pop(numero, []):
                    os.remove(img)
                envioTemplateTxt(numero, config.COMPLAINT_CLAIMS_NOTIFICATION_TEMPLATE, [])
                return
            else:
                envioTemplateTxt(numero, config.STARTER_MENU_TEMPLATE, [])
                print("No hay mensajes o imágenes para enviar.")
        else:
            denuncia[numero].append(cuerpo_mensaje)
            print(f"Mensaje agregado a la denuncia: {cuerpo_mensaje}")
        return

    # Fallback para mensajes no reconocidos
    if numero not in esperando_denuncia or not esperando_denuncia[numero]:
        envioTemplateTxt(numero, config.STARTER_MENU_TEMPLATE, [])
        print("El mensaje no es una denuncia o reclamo.")

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

