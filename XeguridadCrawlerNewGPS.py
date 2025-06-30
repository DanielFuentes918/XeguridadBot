from Config import Config
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
import time

config = Config()

def execute_crawler_new_gps(unitnumber, unitname, typeunit, phonenumber, subdivision, icon):
    print("Iniciando ejecución del WebScraper...")

    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    options.add_argument('--headless=new')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.138 Safari/537.36"
    options.add_argument(f'user-agent={user_agent}')

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 20)
    actions = ActionChains(driver)

    try:
        driver.get('https://mongol.brono.com/mongol/fiona/index.php')
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'loginwindow')))
        driver.find_element(By.ID, 'user2').send_keys(config.XEGURIDAD_USERNAME)
        driver.find_element(By.ID, 'p2').send_keys(config.XEGURIDAD_PASSWORD)
        driver.find_element(By.CLASS_NAME, 'loginButton').click()
        wait.until(EC.url_contains('index.php?m=home'))
        print("✔ Login exitoso")

        driver.get('https://mongol.brono.com/mongol/fiona/index.php?m=resources_units_form')
        print("⏳ Esperando que el formulario esté visible...")

        try:
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.tabcontents.tab1.active")))
            wait.until(EC.visibility_of_element_located((By.NAME, "u")))

            print("✔ Formulario cargado correctamente")
        except TimeoutException:
            print("❌ Formulario no detectado. Guardando HTML para debug...")
            with open("formulario_no_encontrado.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            return

        except TimeoutException:
            print("❌ El campo 'u' no apareció tras el clic en btncs")
            with open("error_u_missing.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            return

        def fill_input(name, value, retries=5, delay=1):
            for attempt in range(retries):
                try:
                    el = wait.until(EC.presence_of_element_located((By.NAME, name)))
                    driver.execute_script("arguments[0].focus();", el)
                    el.clear()
                    el.send_keys(value)
                    driver.execute_script("""
                        arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                        arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                        arguments[0].dispatchEvent(new Event('blur'));
                    """, el)
                    print(f"✔ Campo '{name}' lleno con '{value}'")
                    return
                except Exception as e:
                    print(f"⏳ Intentando llenar '{name}' (intento {attempt+1}/{retries})...")
                    time.sleep(delay)
            print(f"❌ No se pudo llenar el campo '{name}': no encontrado o inaccesible tras {retries} intentos.")

        def select_dropdown(name, value):
            sel = Select(wait.until(EC.presence_of_element_located((By.NAME, name))))
            sel.select_by_value(str(value))
            driver.execute_script("""
                arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            """, sel._el)
            print(f"✔ Dropdown '{name}' seleccionado con valor '{value}'")


        print("➡️ Llenando campo 'u' (Número de unidad)")
        fill_input("u", str(unitnumber))

        print("➡️ Llenando campo 'c' (Nombre de unidad)")
        fill_input("c", unitname)

        print("➡️ Llenando campo 'ad' (Número de teléfono)")
        fill_input("ad", phonenumber)

        print("➡️ Seleccionando dropdown 'um' (Tipo de unidad)")
        select_dropdown("um", typeunit)

        print(f"➡️ Seleccionando ícono con rel='{icon}'")
        try:
            icon_selector = f"//img[@class='icon_select' and @rel='{icon}']"
            icon_img = wait.until(EC.element_to_be_clickable((By.XPATH, icon_selector)))
            driver.execute_script("arguments[0].scrollIntoView(true);", icon_img)
            actions.move_to_element(icon_img).click().perform()
            print(f"✔ Ícono con rel='{icon}' seleccionado correctamente")
        except TimeoutException:
            print(f"❌ No se pudo hacer clic en el ícono con rel='{icon}'")


        print("➡️ Haciendo clic en el botón '+' para mostrar el input #addusers")
        try:
            plus_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.plus[rel="users"]')))
            driver.execute_script("arguments[0].scrollIntoView(true);", plus_button)
            actions.move_to_element(plus_button).click().perform()
            print("✔ Botón '+' clickeado")
        except TimeoutException:
            print("❌ No se pudo hacer clic en el botón '+' (a.plus[rel='users'])")
            return

        print("➡️ Esperando que el input #addusers sea visible...")
        try:
            wait.until(EC.visibility_of_element_located((By.ID, "addusers")))
            print("✔ Input #addusers visible")
        except TimeoutException:
            print("❌ Input #addusers no se volvió visible a tiempo")
            return

        def inject_adduser(text):
            try:
                input_user = wait.until(EC.presence_of_element_located((By.ID, "addusers")))
                driver.execute_script("arguments[0].scrollIntoView(true);", input_user)
                input_user.clear()
                input_user.send_keys(text)
                print(f"⌨️ Escribiendo '{text}' en #addusers...")
                time.sleep(1.2)  # tiempo para que se cargue la sugerencia

                # Buscar el item de sugerencia que contiene el texto buscado
                suggestion = wait.until(EC.element_to_be_clickable((
                    By.XPATH, f"//ul[contains(@class, 'ui-autocomplete')]//div[text()='{text}']"
                )))

                suggestion.click()
                print(f"✔ Usuario '{text}' seleccionado de la lista")
            except Exception as e:
                print(f"❌ Error al seleccionar usuario '{text}' de la lista: {e}")

        def inject_addgroup(text):
            try:
                print("➡️ Haciendo clic en el botón '+' para mostrar el input #addgroups")
                plus_group_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.plus[rel="groups"]')))
                driver.execute_script("arguments[0].scrollIntoView(true);", plus_group_btn)
                actions.move_to_element(plus_group_btn).click().perform()
                print("✔ Botón '+' (grupos) clickeado")

                print("➡️ Esperando que el input #addgroups sea visible...")
                input_group = wait.until(EC.presence_of_element_located((By.ID, "addgroups")))
                driver.execute_script("arguments[0].scrollIntoView(true);", input_group)
                input_group.clear()
                input_group.send_keys(text)
                print(f"⌨️ Escribiendo '{text}' en #addgroups...")
                time.sleep(1.2)

                # Seleccionar sugerencia exacta en lista
                suggestion = wait.until(EC.element_to_be_clickable((
                    By.XPATH, f"//ul[contains(@class, 'ui-autocomplete')]//div[text()='{text}']"
                )))
                driver.execute_script("arguments[0].scrollIntoView(true);", suggestion)
                actions.move_to_element(suggestion).click().perform()
                print(f"✔ Grupo '{text}' seleccionado de la lista")

            except Exception as e:
                print(f"❌ Error al seleccionar grupo '{text}' de la lista: {e}")


        print("➡️ Inyectando usuarios al input #addusers...")
        inject_adduser("mecanico1cmxa")
        time.sleep(1)  # espera breve para autocompletado si aplica
        inject_adduser("tec1@conmoxa.com")

        print("➡️ Inyectando grupos al input #addgroups...")
        inject_addgroup(subdivision)

        # Campos analógicos
        # Hacer clic para desplegar sección de campos analógicos
        print("➡️ Mostrando sección de Campos Analógicos...")

        try:
            titulo_analogos = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//div[@class='divtitle' and contains(text(), 'Títulos')]")))
            driver.execute_script("arguments[0].scrollIntoView(true);", titulo_analogos)
            actions.move_to_element(titulo_analogos).click().perform()
            print("✔ Sección de Campos Analógicos expandida")

            # Scroll adicional hacia abajo para asegurar visibilidad
            time.sleep(0.5)
            driver.execute_script("window.scrollBy(0, 500);")
            print("↕ Scroll hacia abajo realizado tras expandir campos analógicos")

        except TimeoutException:
            print("❌ No se pudo hacer clic en el título 'Títulos' para mostrar campos analógicos")

        print("➡️ Llenando campos analógicos individuales...")

        print("➡️ c_analoginput1u")
        fill_input("c_analoginput1u", "-")

        print("➡️ c_analoginput2u")
        fill_input("c_analoginput2u", "-")

        print("➡️ c_analoginput3u")
        fill_input("c_analoginput3u", "-")

        print("➡️ c_analoginput1a")
        fill_input("c_analoginput1a", "0")

        print("➡️ c_analoginput2a")
        fill_input("c_analoginput2a", "0")

        print("➡️ c_analoginput3a")
        fill_input("c_analoginput3a", "0")

        print("➡️ c_analoginput1b")
        fill_input("c_analoginput1b", "0")

        print("➡️ c_analoginput2b")
        fill_input("c_analoginput2b", "0")

        print("➡️ c_analoginput3b")
        fill_input("c_analoginput3b", "0")


        # Verificación de valores llenados antes de enviar el formulario
        for name in ["u", "c", "ad"]:
            val = driver.find_element(By.NAME, name).get_attribute("value")
            print(f"[Verificación] {name}: {val}")

        try:
            save_btn = wait.until(EC.element_to_be_clickable((By.NAME, "a")))
            driver.execute_script("arguments[0].scrollIntoView(true);", save_btn)
            actions.move_to_element(save_btn).click().perform()
            print("✔ Formulario enviado (click en 'Guardar')")
        except TimeoutException:
            print("❌ Botón 'Guardar' no fue encontrado.")


        time.sleep(5)

    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        with open("error_final.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)


    finally:
        driver.quit()
        print("✔ WebDriver cerrado correctamente")

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 7:
        unitnumber, unitname, typeunit, phonenumber, subdivision, icon = sys.argv
        execute_crawler_new_gps(
            unitnumber,
            unitname,
            typeunit,
            phonenumber,
            subdivision,
            icon
        )
    else:
        print("Uso: python webscraper.py <unitnumber> <unitname> <typeunit> <phonenumber> <subdivision> <icon>")
