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
    data = request.json
    print(f"Datos recibidos: {data}")
    for entry in data.get('entry', []):
        for change in entry.get('changes', []):
            message = change.get('value', {}).get('messages', [])[0]
            numero = message['from']
            message_id = message.get('id')
            cuerpo_mensaje = ""

            # Manejo de mensajes duplicados
            if numero in ultimos_mensajes and ultimos_mensajes[numero] == message_id:
                print(f"Mensaje duplicado detectado: {message_id}")
                return
            ultimos_mensajes[numero] = message_id

            # Manejar diferentes tipos de mensajes
            if message['type'] == 'text':
                cuerpo_mensaje = message['text']['body']
            elif message['type'] == 'image':
                media_id = message['image']['id']
                imagen_path = descargar_imagen(media_id, config.WHATSAPP_API_TOKEN)
                if numero not in imagenes:
                    imagenes[numero] = []
                if imagen_path:
                    imagenes[numero].append(imagen_path)
                print(f"Imagen asociada al usuario {numero}: {imagen_path}")
                continue  # No procesamos texto si es una imagen

            # Flujo de denuncias
            if cuerpo_mensaje.strip().lower() == "denuncias o reclamos":
                print("El usuario ha seleccionado 'denuncias o reclamos'")
                envioTemplateTxt(numero, config.COMPLAINT_CLAIMS_TEMPLATE, [])
                esperando_denuncia[numero] = True
                denuncia[numero] = []
                if numero not in imagenes:
                    imagenes[numero] = []
                return jsonify({'status': 'Plantilla enviada'}), 200

            if numero in esperando_denuncia and esperando_denuncia[numero]:
                if cuerpo_mensaje.strip().lower() == "enviar":
                    if numero in denuncia and denuncia[numero]:
                        # Concatenar denuncia y enviar
                        denuncia_texto = "\n".join(denuncia[numero])
                        enviar_queja_anonima(denuncia_texto, imagenes[numero])

                        # Limpiar estado
                        esperando_denuncia.pop(numero, None)
                        denuncia.pop(numero, None)
                        for img in imagenes.pop(numero, []):
                            os.remove(img)  # Eliminar imágenes temporales
                        return jsonify({'status': 'Denuncia enviada'}), 200
                    else:
                        envioTemplateTxt(numero, config.STARTER_MENU_TEMPLATE, [])
                        print("No hay mensajes para enviar como denuncia.")
                else:
                    denuncia[numero].append(cuerpo_mensaje)
                    print(f"Mensaje agregado a la denuncia: {cuerpo_mensaje}")
                return

    return jsonify({'status': 'success'}), 200

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

