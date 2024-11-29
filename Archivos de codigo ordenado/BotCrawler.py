from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
import time
import os
from dotenv import load_dotenv

load_dotenv()
def execute_crawler(unitnumber):
    # Configuración del webdriver
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--remote-debugging-port=9222')
    options.add_argument('--disable-software-rasterizer')
    options.add_argument('--disable-dev-shm-usage')
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.138 Safari/537.36"
    options.add_argument(f'user-agent={user_agent}')

    # Inicializar el webdriver
    
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 10)
    actions = ActionChains(driver)

    #driver.maximize_window()
    driver.set_window_size(450, 800)
    try:
        # Abrir la página de inicio de sesión
        login_url = os.getenv('MONGOL_API_URL')
        driver.get(login_url)
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
        username = os.getenv('XEGURIDAD_USERNAME')
        password = os.getenv('XEGURIDAD_PASSWORD')
        username_input.send_keys(username)
        password_input.send_keys(password)


        # Enviar el formulario de inicio de sesión
        login_button = driver.find_element(By.CLASS_NAME, 'loginButton')
        login_button.click()
        print("Formulario de inicio de sesión enviado")

        # Esperar hasta que se cargue la página después del inicio de sesión
        wait.until(EC.url_contains('index.php?m=home'))
        print("Inicio de sesión exitoso")

        # Navegar a la página de filtrado
        filtering_url = f'https://mongol.brono.com/mongol/fiona/index.php?filtering=1&f_unitnumber=on&f_vehiclecode=on&f_vehiclemodel=on&f_vehiclecolor=on&f_rxdate=on&f_customstring=on&m=resources_units&subgroup=-1&v={unitnumber}&number=&name=&model=&color=&lastrx=&custom='
        driver.get(filtering_url)
        print(f"Navegando a {filtering_url}")

        # Esperar hasta que la tabla con id 'restable' esté cargada
        wait.until(EC.presence_of_element_located((By.ID, 'restable')))
        print("Tabla con id 'restable' cargada")

        # Ejecutar el div con class 'pointer' dentro de la tabla
        pointer_div = driver.find_element(By.CSS_SELECTOR, 'table#restable div.pointer')
        pointer_div.click()
        print("Div con class 'pointer' ejecutado")

        # Esperar hasta que el div con id 'menu1' esté cargado
        wait.until(EC.presence_of_element_located((By.ID, 'menu1')))
        print("Div con id 'menu1' cargado")

        # Ejecutar el td con onclick dentro del div con id 'menu1'
        td_element = driver.find_element(By.CSS_SELECTOR, 'div#menu1 td[onclick]')
        td_element.click()
        print("Td con onclick ejecutado")

        # Esperar hasta que la página final esté cargada
        wait.until(EC.presence_of_element_located((By.ID, 'c')))
        print("Página final cargada")

        # Verificar si el formulario con id 'c' está presente
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

        time.sleep(60)
        # Tomar captura de pantalla después de los 2 minutos
        screenshot_filename = f"screenshot_{unitnumber}.png"
        driver.save_screenshot(screenshot_filename)
        print(f"Captura de pantalla tomada y guardada como: {screenshot_filename}")

    except Exception as e:
        print(f"Error: {str(e)}")
        # Imprimir la estructura del DOM para depuración
        print(driver.page_source)
    finally:
        driver.quit()
        print("Instancia de WebDriver cerrada")
        return True

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        unitnumber = sys.argv[1]
        execute_crawler(unitnumber)
    else:
        print("No se proporcionó ningún unitnumber.")
