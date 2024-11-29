from pymongo import MongoClient
from config import Config
from utils import check_password, extraer_placa
import requests

class MongoService:
    def __init__(self):
        self.uri = f"mongodb://{Config.USUARIO_MONGO}:{Config.PASSWORD_MONGO}@localhost:27017/{Config.BASE_DATOS_MONGO}?authSource={Config.AUTH_DB}"
        try:
            self.client = MongoClient(self.uri)
            self.db = self.client[Config.BASE_DATOS_MONGO]
            self.collectionUsuarios = self.db['usuarios']
        except Exception as e:
            raise ConnectionError(f"Error al conectar a MongoDB: {e}")

    def find_user_by_phone(self, phone):
        return self.collectionUsuarios.find_one({'telefono': phone})

    def authenticate_user(self, username, password):
        user = self.find_user_by_phone(username)
        if user and check_password(user['password'], password):
            return True
        return False

class WhatsAppService:
    @staticmethod
    def send_message(numero, template_name, components=[]):
        headers = {
            'Authorization': f'Bearer {Config.WHATSAPP_API_TOKEN}',
            'Content-Type': 'application/json'
        }
        data = {
            'messaging_product': 'whatsapp',
            'to': numero,
            'type': 'template',
            'template': {
                'namespace': Config.NAMESPACE,
                'name': template_name,
                'language': {'policy': 'deterministic', 'code': 'es'},
                'components': components
            }
        }
        response = requests.post(Config.WHATSAPP_API_URL, headers=headers, json=data)
        return response.status_code, response.text

    @staticmethod
    def send_plate_not_found(numero, template_name, placa):
        components = [{"type": "text", "text": placa}]
        return WhatsAppService.send_message(numero, template_name, components)

class UnitService:
    @staticmethod
    def buscar_unitnumber_por_placa(placa):
        params = {
            'commandname': 'get_units',
            'user': Config.XEGURIDAD_USERNAME,
            'pass': Config.XEGURIDAD_PASSWORD,
            'format': 'json1'
        }
        response = requests.get(Config.XEGURIDAD_API_URL, params=params)
        if response.status_code == 200:
            unidades = response.json()
            for unidad in unidades:
                nombre_placa = extraer_placa(unidad['name'])
                if nombre_placa == placa:
                    return unidad['unitnumber']
        return None
