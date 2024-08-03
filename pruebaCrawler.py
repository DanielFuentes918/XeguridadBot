from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains

# Configuración del webdriver
options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# Inicializar el webdriver
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 10)
actions = ActionChains(driver)

try:
    # Abrir la página de inicio de sesión
    driver.get('https://mongol.brono.com/mongol/fiona/index.php')
    print("Página de inicio de sesión abierta")

    # Esperar hasta que el formulario de inicio de sesión esté presente
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'loginwindow')))

    # Limpiar los campos de inicio de sesión
    username_input = driver.find_element(By.ID, 'user2')
    password_input = driver.find_element(By.ID, 'p2')
    username_input.clear()
    password_input.clear()
    print("Campos de inicio de sesión limpiados")

    # Ingresar las credenciales de inicio de sesión
    username = 'dhnexasa'
    password = 'dhnexasa2022/487-'
    username_input.send_keys(username)
    password_input.send_keys(password)
    print(f"Usuario ingresado: {username}")
    print(f"Contraseña ingresada: {password}")

    # Enviar el formulario de inicio de sesión
    login_button = driver.find_element(By.CLASS_NAME, 'loginButton')
    login_button.click()
    print("Formulario de inicio de sesión enviado")

    # Esperar hasta que se cargue la página después del inicio de sesión
    wait.until(EC.url_contains('index.php?m=home'))
    print("Inicio de sesión exitoso")

    # Navegar a la nueva URL después del inicio de sesión
    target_url = 'https://mongol.brono.com/mongol/fiona/index.php?m=map&id=2296640'
    driver.get(target_url)
    print(f"Navegando a {target_url}")

    # Esperar hasta que la página de destino esté cargada
    wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
    print("Página de destino cargada")

    # Verificar si el formulario con id `c` está presente
    form = wait.until(EC.presence_of_element_located((By.ID, 'c')))
    print("Formulario con id 'c' encontrado")

    # Verificar si el `select` con id `co` está presente dentro del `form`
    select_element = form.find_element(By.ID, 'co')
    print("Elemento select con id 'co' encontrado")

    # Seleccionar el `option` con value="rs"
    select = Select(select_element)
    select.select_by_value('rs')
    print("Opción con value='rs' seleccionada")

    # Ejecutar el `span` con class="btngo" dentro del `div` con class="mapcmds commandsSection"
    try:
        mapcmds_div = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.mapcmds.commandsSection')))
        btngo_span = mapcmds_div.find_element(By.CSS_SELECTOR, 'span.btngo#btncs')

        # Asegurarse de que el elemento es visible desplazándose hasta él
        driver.execute_script("arguments[0].scrollIntoView(true);", btngo_span)
        wait.until(EC.visibility_of(btngo_span))

        # Imprimir más información sobre el elemento `btngo_span`
        print(f"Texto del elemento: {btngo_span.text}")
        print(f"Atributo class: {btngo_span.get_attribute('class')}")
        print(f"ID del elemento: {btngo_span.get_attribute('id')}")
        print(f"Name del elemento: {btngo_span.get_attribute('name')}")
        print(f"Type del elemento: {btngo_span.get_attribute('type')}")
        print(f"HTML completo del elemento: {btngo_span.get_attribute('outerHTML')}")
        print(f"HTML interno del elemento: {btngo_span.get_attribute('innerHTML')}")
        print(f"Elemento está habilitado: {btngo_span.is_enabled()}")
        print(f"Elemento está visible: {btngo_span.is_displayed()}")

        # Hacer clic en el elemento `btngo_span` si es interactuable
        if btngo_span.is_displayed() and btngo_span.is_enabled():
            actions.move_to_element(btngo_span).click().perform()
            print("Span con id='btncs' ejecutado")
        else:
            print("El span con id='btncs' no es interactuable")
    except Exception as e:
        print(f"Error al encontrar o ejecutar el span: {str(e)}")
        # Imprimir la estructura del DOM para depuración
        print(driver.page_source)
    
    driver.quit()

except Exception as e:
    print(f"Error: {str(e)}")
    # Imprimir la estructura del DOM para depuración
    print(driver.page_source)
