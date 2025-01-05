import os
from datetime import datetime
from Config import Config
from Users import UsuarioManager
from Utils import envioTemplateTxt, buscar_unitnumber_por_placa,buscar_unitnumber_por_genset, obtener_ultima_transmision, descargar_multimedia, enviar_ubicacion_tile_sync
from DenunciasReclamos_SMTP import enviar_queja_anonima
from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from XeguridadCrawler import execute_crawler
config = Config()

ultimos_mensajes = {}

esperando_denuncia = {}

esperando_placa = {}

esperando_unit_type = {}

esperando_plate_request = {}

esperando_genset_request = {}

esperando_genset = {}

esperando_chasis_request = {}

esperando_chasis = {}

user_requests = {}

denuncia = {}

imagenes = {}

empresa = {}

autenticado = {}

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
        esperando_denuncia[numero] = True
        envioTemplateTxt(numero, config.STARTER_MENU_TEMPLATE, [])
        return

    # Manejo de mensajes duplicados
    if numero in ultimos_mensajes and ultimos_mensajes[numero] == message_id:
        print(f"Mensaje duplicado detectado: {message_id}")
        return
    ultimos_mensajes[numero] = message_id

    # Manejar diferentes tipos de mensajes
    if mensaje['type'] == 'text':
        cuerpo_mensaje = mensaje['text']['body'].strip()
    elif mensaje['type'] == 'image':
        media_id = mensaje['image']['id']
        imagen_path = descargar_multimedia(media_id, config.WHATSAPP_API_TOKEN, "imagen")
        if numero not in imagenes:
            imagenes[numero] = []
        if imagen_path:
            imagenes[numero].append(imagen_path)
        print(f"Imagen descargada para {numero}: {imagen_path}")
        return
    elif mensaje['type'] == 'video':
        media_id = mensaje['video']['id']
        video_path = descargar_multimedia(media_id, config.WHATSAPP_API_TOKEN, "video")
        if numero not in imagenes:
            imagenes[numero] = []
        if video_path:
            imagenes[numero].append(video_path)
        print(f"Video descargado para {numero}: {video_path}")
        return

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
        if cuerpo_mensaje.lower() in ["exa s.a.", "conmoxa", "la mega", "trexa", "otra empresa del grupo", "volver a menú principal"]:
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
    
    # Manejar opción de "Xeguridad"
    if cuerpo_mensaje.lower() == "xeguridad" or numero in usuario_manager.usuarios_esperando_password or numero in usuario_manager.usuarios_autenticados or numero in esperando_placa or numero in esperando_unit_type or numero in esperando_plate_request:
        if numero in usuario_manager.usuarios_autenticados:
            print(f"Usuario {numero} ya autenticado. Continuando flujo.")
        elif not usuario_manager.iniciar_autenticacion(numero):
            return  # Ya se envió la plantilla de autenticación, espera respuesta.

        autenticado = usuario_manager.procesar_credenciales(numero, cuerpo_mensaje)
        print(f"Usuario autenticado: {autenticado}")
        print(f"Usuarios autenticados: {usuario_manager.usuarios_autenticados}")

        if usuario_manager.usuarios_autenticados.get(numero):
            print("cuerpo_mensaje.strip():", cuerpo_mensaje.strip())
            if cuerpo_mensaje.strip().lower() == "ubicación de una unidad":
                esperando_unit_type[numero] = True
                print(f"Usuario autenticado: {numero} puede solicitar ubucacion.")
                envioTemplateTxt(numero, config.UNIT_TYPE_TEMPLATE, [])
                print(f"usuarios seleccionando unit type: {esperando_unit_type}")
            elif numero in esperando_unit_type:
                if cuerpo_mensaje.strip().lower() == "vehículo":
                    print(f"Usuario {numero} seleccionó vehículo.")
                    esperando_plate_request[numero] = True
                    del esperando_unit_type[numero]
                    print(f"usuarios seleccionando plate request: {esperando_plate_request}")
                elif cuerpo_mensaje.strip().lower() == "genset":
                    esperando_genset_request[numero] = True
                    del esperando_unit_type[numero]
                elif cuerpo_mensaje.strip().lower() == "chasis":
                    esperando_chasis_request[numero] = True
                    del esperando_unit_type[numero]

            if numero in esperando_plate_request:
                envioTemplateTxt(numero, config.SOLICITUD_UNIDAD_COMANDOS_TEMPLATE_NAME, [])
                esperando_placa[numero] = True
                del esperando_plate_request[numero]
            elif esperando_placa.get(numero):
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
                        obtener_ultima_transmision(unitnumber, numero, user_requests)
                    else:
                        print("Error al ejecutar el crawler.")
                else:
                    print(f"No se encontró el unitnumber para la placa {placa}.")
                    components = [
                        {
                            "type": "body",
                            "parameters": [
                                {
                                    "type": "text",
                                    "text": placa
                                },
                            ]
                        }
                    ]
                    envioTemplateTxt(numero, config.PLACA_NO_ENCONTRADA_TEMPLATE, components)
                del esperando_placa[numero]

            if numero in esperando_genset_request:
                envioTemplateTxt(numero, config.GENSET_REQUEST_TEMPLATE, [])
                esperando_genset[numero] = True
                del esperando_genset_request[numero]
            elif esperando_genset.get(numero):
                genset = cuerpo_mensaje.upper()
                print(f"Genset detectado: {genset}")
                unitnumber = buscar_unitnumber_por_genset(genset)
                if unitnumber:
                    print(f"El unitnumber para el genset {genset} es {unitnumber}.")
                    user_requests[numero] = {
                        "placa": genset,
                        "hora": datetime.now()
                    }
                    envioTemplateTxt(numero, config.CARGANDO_COMANDOS_TEMPLATE_NAME, [])
                    if execute_crawler(unitnumber):
                        print("Crawler ejecutado correctamente.")
                        obtener_ultima_transmision(unitnumber, numero, user_requests)
                    else:
                        print("Error al ejecutar el crawler.")
                else:
                    print(f"No se encontró el unitnumber para el genset {genset}.")
                    components = [
                        {
                            "type": "body",
                            "parameters": [
                                {
                                    "type": "text",
                                    "text": genset
                                },
                            ]
                        }
                    ]
                    envioTemplateTxt(numero, config.PLACA_NO_ENCONTRADA_TEMPLATE, components)
                del esperando_genset[numero]
            
            if numero in esperando_chasis_request:
                envioTemplateTxt(numero, config.CHASIS_REQUEST_TEMPLATE, [])
                esperando_chasis[numero] = True
                del esperando_chasis_request[numero]
            elif esperando_chasis.get(numero):
                chasis= cuerpo_mensaje.upper()
                # Eviar la ubicación
                enviar_ubicacion_tile_sync(chasis, numero, config.TILE_USER, config.TILE_PASSWORD)
            else:
                print(f"Usuario {numero} autenticado correctamente.")
        else:
            print(f"Usuario {numero} en proceso de autenticación o fallido.")
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

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=config.PORT)  # Ejecutar la aplicación en el puerto segun la variable de entorno del ambiente

