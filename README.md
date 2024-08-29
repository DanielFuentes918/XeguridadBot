# Xeguridad Bot Flask

Este proyecto es una aplicación web desarrollada en Flask que se integra con la API de WhatsApp y MongoDB. El bot proporciona autenticación de usuarios y consulta de datos a través de comandos enviados por WhatsApp.

## Funcionalidades

- **Autenticación de usuarios**: Los usuarios deben autenticarse utilizando su número de teléfono y una contraseña.
- **Integración con WhatsApp**: El bot recibe y responde a mensajes a través de la API de WhatsApp.
- **Consulta de datos en MongoDB**: Permite consultar información de usuarios en la base de datos MongoDB.
- **Envio de comandos a GPS**: El bot puede enviar comandos específicos y responder con datos consultados a través de APIs externas.

## Tecnologías Utilizadas

- **Flask**: Framework web utilizado para desarrollar la aplicación.
- **MongoDB**: Base de datos NoSQL utilizada para almacenar la información de los usuarios.
- **Pymongo**: Cliente de MongoDB para interactuar con la base de datos.
- **Requests**: Biblioteca utilizada para realizar solicitudes HTTP a APIs externas.
- **Bcrypt**: Biblioteca utilizada para la encriptación de contraseñas.
- **python-dotenv**: Herramienta utilizada para cargar variables de entorno desde un archivo `.env`.
- **WhatsApp API**: Integración con la API de WhatsApp para manejar los mensajes.

## Requisitos Previos

- Python 3.8+
- MongoDB
- Entorno virtual de Python (recomendado)

## Instalación

1. **Clonar el repositorio**:

    ```bash
    git clone https://github.com/tuusuario/xeguridad-bot-flask.git
    cd xeguridad-bot-flask
    ```

2. **Crear y activar un entorno virtual**:

    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    ```

3. **Instalar las dependencias**:

    ```bash
    pip install -r requirements.txt
    ```

4. **Configurar las variables de entorno**:

    Crea un archivo `.env` en la raíz del proyecto con el siguiente contenido:

    ```dotenv
    MONGO_DB_USERNAME=tu_usuario_mongo
    MONGO_DB_PASSWORD=tu_contraseña_mongo
    WHATSAPP_API_TOKEN=tu_api_token_de_whatsapp
    XEGURIDAD_USERNAME=tu_usuario_xeguridad
    XEGURIDAD_PASSWORD=tu_contraseña_xeguridad
    VERIFY_TOKEN=tu_token_de_verificación
    ```

5. **Ejecutar la aplicación**:

    ```bash
    python app.py
    ```

6. **Acceso a la aplicación**:

    La aplicación estará disponible en `http://localhost:5000`.

## Uso

### Autenticación y Consulta en MongoDB

1. **Autenticación**:

   Envia un mensaje de WhatsApp con tu número de teléfono y contraseña para autenticarse.

2. **Consulta de Datos**:

   Una vez autenticado, puedes enviar comandos para consultar datos específicos. Por ejemplo, puedes consultar el estado de una unidad o su última transmisión.

### Rutas Disponibles

- **`/webhook`**: Maneja los mensajes entrantes desde WhatsApp.
- **`/test_mongodb`**: Ruta para probar la conexión a MongoDB (requiere autenticación).
- **`/politica_privacidad`**: Muestra la política de privacidad.

## Estructura del Proyecto

