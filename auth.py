import bcrypt
from datetime import datetime, timedelta
from mongodb import collectionUsuarios, usuarios_autenticados

def check_password(stored_hash: bytes, provided_password: str) -> bool:
    if isinstance(stored_hash, str):
        stored_hash = stored_hash.encode('utf-8')
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_hash)


def autenticar_usuario(username: str, password: str) -> bool:
    # Busca el usuario por el número de teléfono
    usuario = collectionUsuarios.find_one({'telefono': username})
    
    # Verifica si se encontró el usuario
    if usuario:
        stored_hash = usuario['password']
        print(f"Contraseña en mongo: {stored_hash}, contraseña ingresada: {password}")
        
        # Verifica si la contraseña ingresada coincide con el hash almacenado
        if check_password(stored_hash, password):
            usuarios_autenticados[username] = datetime.now()
            return True
    
    # Si el usuario no se encuentra o la contraseña no coincide, retorna False
    return False

def verificar_sesion_activa(numero):
    hora_autenticacion = usuarios_autenticados.get(numero)
    if hora_autenticacion and datetime.now() - hora_autenticacion <= timedelta(hours=24):
        return True
    return False