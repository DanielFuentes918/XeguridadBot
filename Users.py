from datetime import datetime, timedelta
from Utils import envioTemplateTxt
from Config import Config
from pymongo import MongoClient
import bcrypt

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
                self.usuarios_autenticados[username] = datetime.now()
                return True
        
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

    # def manejar_respuesta_autenticacion(self, numero, cuerpo_mensaje):
    #     print(f"Manejando autenticación para {numero}. Mensaje: {cuerpo_mensaje}")
    #     if numero in self.usuarios_autenticados:
    #         hora_autenticacion = self.usuarios_autenticados[numero]
            
    #         if datetime.now() - hora_autenticacion > timedelta(hours=24):
    #             print("Sesión expirada. El usuario necesita autenticarse de nuevo.")
    #             del self.usuarios_autenticados[numero]
    #             envioTemplateTxt(numero, config.AUTH_TEMPLATE, [])
    #             return False
    #         return True
        
    #     if numero not in self.usuarios_esperando_password:
    #         envioTemplateTxt(numero, config.AUTH_TEMPLATE, [])
    #         self.usuarios_esperando_password[numero] = True
    #         return
    #     else:
    #         if self.autenticar_usuario(numero, cuerpo_mensaje):
    #             print("Autenticación exitosa. Bienvenido.")
    #             envioTemplateTxt(numero, config.MENU_TEMPLATE_NAME, [])
    #             del self.usuarios_esperando_password[numero]
    #         else:
    #             print("Autenticación fallida. Usuario o contraseña incorrectos.")
    #             envioTemplateTxt(numero, config.AUTH_FAILED_TEMPLATE, [])
    #             del self.usuarios_esperando_password[numero]
    #     return False

    def iniciar_autenticacion(self, numero):
        if numero not in self.usuarios_autenticados and numero not in self.usuarios_esperando_password:
            print(f"Enviando solicitud de autenticación para {numero}")
            envioTemplateTxt(numero, config.AUTH_TEMPLATE, [])
            self.usuarios_esperando_password[numero] = True
            return False
        return True
    
    def procesar_credenciales(self, numero, cuerpo_mensaje):
        if numero in self.usuarios_esperando_password:
            if self.autenticar_usuario(numero, cuerpo_mensaje):
                print(f"Autenticación exitosa para {numero}")
                envioTemplateTxt(numero, config.MENU_TEMPLATE_NAME, [])
                del self.usuarios_esperando_password[numero]
                self.usuarios_autenticados[numero] = datetime.now()
                return True
            else:
                print(f"Autenticación fallida para {numero}")
                envioTemplateTxt(numero, config.AUTH_FAILED_TEMPLATE, [])
                del self.usuarios_esperando_password[numero]
        return False

    def buscar_usuario_por_telefono(self, telefono):
        #Busca un usuario en la base de datos por su número de teléfono.
        return self.collection.find_one({'telefono': telefono})

    def usuario_autenticado(self, numero):
        """Verifica si un usuario está autenticado."""
        return numero in self.usuarios_autenticados

    def eliminar_usuario_autenticado(self, numero):
        """Elimina un usuario de la lista de autenticados."""
        if numero in self.usuarios_autenticados:
            del self.usuarios_autenticados[numero]



