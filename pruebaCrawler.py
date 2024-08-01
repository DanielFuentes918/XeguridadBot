import requests
from bs4 import BeautifulSoup

# Crear una sesión
session = requests.Session()

# Configurar los encabezados de la sesión para parecer un navegador real
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
})

# Datos de inicio de sesión
login_data = {
    'username': 'dhnexasa',
    'password': 'dhnexasa2022/487-'
}

# URL de inicio de sesión
login_url = 'https://mongol.brono.com/'

# Enviar la solicitud de inicio de sesión
response = session.post(login_url, data=login_data, allow_redirects=True)

# Verificar si la solicitud de inicio de sesión fue exitosa
if response.status_code != 200:
    print("Error al iniciar sesión")
    print("Código de estado:", response.status_code)
    print("URL después del inicio de sesión:", response.url)
    print("Contenido de la respuesta:", response.text)
else:
    print("Inicio de sesión exitoso")

    # Navegar a la URL específica dentro del sitio
    map_url = 'https://mongol.brono.com/mongol/fiona/index.php?m=map&id=2296640'
    response = session.get(map_url)

    # Verificar si la solicitud de navegación fue exitosa
    if response.status_code != 200:
        print("Error al acceder a la página del mapa")
        print("Código de estado:", response.status_code)
        print("Contenido de la respuesta:", response.text)
    else:
        print("Acceso a la página del mapa exitoso")

        # Analizar el contenido de la página con BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Imprimir el HTML completo para verificar el contenido
        print(soup.prettify())  # Esto imprimirá toda la estructura HTML de la página

        # Encontrar el formulario que contiene el campo <select>
        form = soup.find('form', {'id': 'c'})
        if form is None:
            print("Formulario no encontrado")
        else:
            print("Formulario encontrado")

            # Encontrar el elemento <select> con id 'co'
            select = form.find('select', {'id': 'co'}) if form else None
            if select is None:
                print("Elemento <select> no encontrado")
            else:
                print("Elemento <select> encontrado")

                # Continuar solo si el formulario y el select fueron encontrados
                if form and select:
                    # Seleccionar el valor "Solicitar estado"
                    for option in select.find_all('option'):
                        if option['value'] == 'rs':
                            option['selected'] = 'selected'
                            break

                    # Crear un diccionario con los datos del formulario
                    form_data = {tag['name']: tag.get('value', '') for tag in form.find_all(['input', 'select', 'textarea'])}
                    form_data['co'] = 'rs'  # Asegurar que 'co' tenga el valor 'rs' para "Solicitar estado"

                    # URL para enviar el formulario
                    submit_url = form['action']
                    if not submit_url.startswith('http'):
                        submit_url = 'https://mongol.brono.com' + submit_url  # Asegurar URL completa

                    # Enviar el formulario
                    response = session.post(submit_url, data=form_data)

                    # Verificar si la solicitud de envío del formulario fue exitosa
                    if response.status_code != 200:
                        print("Error al enviar el formulario")
                    else:
                        print("Formulario enviado exitosamente")

                    # Leer y mostrar la respuesta después de enviar el formulario
                    html_response = response.text
                    print(html_response)

                    # Analizar la respuesta con BeautifulSoup
                    soup = BeautifulSoup(html_response, 'html.parser')
                    # Aquí puedes realizar más análisis o extracción de datos según sea necesario




