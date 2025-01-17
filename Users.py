from datetime import datetime, timedelta
from Utils import envioTemplateTxt
from Config import Config
import bcrypt
from Config import Config


config = Config()

class UsuarioManager:
    def __init__(self, db):
        self.db = db
        self.collection = self.db['usuarios']
        self.user_requests = {}
        self.usuarios_autenticados = {}
        self.usuarios_esperando_password = {}
        self.usuarios_en_starter_menu = {}

    def autenticar_usuario(self, username: str, password: str) -> bool:
        print(f"Autenticando usuario {username}...")
        # Busca el usuario por el número de teléfono
        usuario = self.collection.find_one({'telefono': username})
        # Verifica si se encontró el usuario
        if usuario:
            stored_hash = usuario['password']
            print(f"Contraseña en mongo: {stored_hash}, contraseña ingresada: {password}")
            
            # Verifica si la contraseña ingresada coincide con el hash almacenado
            if self.check_password(stored_hash, password):
                return True  # Solo retorna True si la contraseña es correcta
            
        # Si el usuario no se encuentra o la contraseña no coincide, retorna False
        return False


    @staticmethod
    def check_password(stored_hash: bytes, provided_password: str) -> bool:
        if isinstance(stored_hash, str):
            stored_hash = stored_hash.encode('utf-8')
        return bcrypt.checkpw(provided_password.encode('utf-8'), stored_hash)

    def manejar_inicio(self, numero):
        print(f"Manejando inicio para {numero}")
        print(self.usuarios_autenticados, self.usuarios_esperando_password, self.usuarios_en_starter_menu)
        #Gestiona el flujo inicial para usuarios no autenticados.
        if numero not in self.usuarios_autenticados and \
        numero not in self.usuarios_esperando_password and \
        numero not in self.usuarios_en_starter_menu:
            envioTemplateTxt(numero, config.STARTER_MENU_TEMPLATE, [])
            print("Usuario no autenticado. Enviando menú inicial.")
            print(self.usuarios_autenticados, self.usuarios_esperando_password, self.usuarios_en_starter_menu)
            self.usuarios_en_starter_menu[numero] = True
            return True
        return False

    def iniciar_autenticacion(self, numero):
        if numero not in self.usuarios_autenticados and numero not in self.usuarios_esperando_password:
            print(f"Enviando solicitud de autenticación para {numero}")
            envioTemplateTxt(numero, config.AUTH_TEMPLATE, [])
            self.usuarios_esperando_password[numero] = True
            return False
        return True
    
    def procesar_credenciales(self, numero, cuerpo_mensaje):
        if numero in self.usuarios_esperando_password:
            if self.autenticar_usuario(numero, cuerpo_mensaje):  # Verifica las credenciales
                print(f"Autenticación exitosa para {numero}")
                self.usuarios_autenticados[numero] = datetime.now()  # Actualiza estado correctamente
                print(f"Usuarios autenticados: {self.usuarios_autenticados}")  # Depuración
                envioTemplateTxt(numero, config.MENU_TEMPLATE_NAME, [])
                del self.usuarios_esperando_password[numero]
                return True
            else:
                print(f"Autenticación fallida para {numero}")
                envioTemplateTxt(numero, config.AUTH_FAILED_TEMPLATE, [])
                del self.usuarios_esperando_password[numero]
        return False

    def usuario_autenticado(self, numero):
        """Verifica si un usuario está autenticado."""
        return numero in self.usuarios_autenticados

    def eliminar_usuario_autenticado(self, numero):
        """Elimina un usuario de la lista de autenticados."""
        if numero in self.usuarios_autenticados:
            del self.usuarios_autenticados[numero]

    def rol_usuario(self, numero):
        """Obtiene el rol de un usuario."""
        usuario = self.collection.find_one({'telefono': numero})
        return usuario['rol']



