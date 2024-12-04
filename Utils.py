from Config import Config
import requests

config = Config()

def envioTemplateTxt(numero, template_name, components):
    components = [components]  # Añadir los parámetros necesarios si los hay
    response_status = envioMsj(numero, template_name, components)
    print(f"Estado de la respuesta al enviar mensaje: {response_status}")

def envioMsj(numero, template_name, components):
    headers = {
        'Authorization': f'Bearer {config.WHATSAPP_API_TOKEN}',
        'Content-Type': 'application/json'
    }
    data = {
        'messaging_product': 'whatsapp',
        'to': numero,
        'type': 'template',
        'template': {
            'namespace': config.NAMESPACE,
            'name': template_name,
            'language': {
                'policy': 'deterministic',
                'code': 'es'
            },
            'components': components
        }
    }
    response = requests.post(config.WHATSAPP_API_URL, headers=headers, json=data)
    print(f"Estado de la respuesta: {response.status_code}")
    print(f"Contenido de la respuesta: {response.text}")
    return response.status_code