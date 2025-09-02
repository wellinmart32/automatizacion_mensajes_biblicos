import os
import time
import random
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Configuración
MENSAJES_DIR = "C:\\Users\\welli\\OneDrive\\Documents\\Repositorios\\facebook_auto\\publicaciones"
CAPTURAS_DIR = "capturas"
TIEMPO_ESPERA = 5  # Segundos para esperar elementos

def crear_directorio_capturas():
    """Crea el directorio para guardar capturas si no existe"""
    if not os.path.exists(CAPTURAS_DIR):
        os.makedirs(CAPTURAS_DIR)

def crear_directorio_publicaciones():
    """Crea el directorio para almacenar los mensajes si no existe"""
    if not os.path.exists(MENSAJES_DIR):
        os.makedirs(MENSAJES_DIR)
        # Crear un mensaje de ejemplo si es la primera vez
        with open(os.path.join(MENSAJES_DIR, "mensaje_ejemplo.txt"), 'w', encoding='utf-8') as f:
            f.write("Este es un mensaje de ejemplo creado automáticamente.\n\n¡Puedes agregar más archivos .txt a esta carpeta para tener mensajes variados!")

def obtener_mensaje_aleatorio():
    """Obtiene un mensaje aleatorio de la carpeta de publicaciones"""
    try:
        # Verificar que exista el directorio
        if not os.path.exists(MENSAJES_DIR):
            print(f"Creando directorio de publicaciones: {MENSAJES_DIR}")
            crear_directorio_publicaciones()
            
        # Obtener todos los archivos de texto
        archivos_txt = [f for f in os.listdir(MENSAJES_DIR) if f.endswith('.txt')]
        
        if not archivos_txt:
            print("No se encontraron archivos de texto en la carpeta de publicaciones.")
            return "No hay mensajes disponibles. Por favor, agrega archivos .txt a la carpeta de publicaciones."
            
        # Elegir un archivo aleatorio
        archivo_elegido = random.choice(archivos_txt)
        ruta_completa = os.path.join(MENSAJES_DIR, archivo_elegido)
        
        print(f"Archivo de mensaje elegido: {archivo_elegido}")
        
        # Leer el contenido del archivo
        with open(ruta_completa, 'r', encoding='utf-8') as archivo:
            mensaje = archivo.read().strip()
            
        print(f"Mensaje leído (primeros 50 caracteres): {mensaje[:50]}...")
        return mensaje
        
    except Exception as e:
        print(f"Error al obtener mensaje aleatorio: {e}")
        return "Error al leer mensaje. Usando mensaje predeterminado."

def guardar_captura(driver, nombre):
    """Guarda una captura de pantalla"""
    try:
        ruta_completa = os.path.join(CAPTURAS_DIR, nombre)
        driver.save_screenshot(ruta_completa)
        print(f"Captura guardada: {nombre}")
    except Exception as e:
        print(f"Error al guardar captura {nombre}: {e}")

def iniciar_navegador():
    """Inicia el navegador con el perfil de usuario existente"""
    print("Inicializando Chrome con perfil existente...")
    options = Options()
    options.add_argument("--disable-notifications")  # Desactivar notificaciones
    options.add_argument("--start-maximized")  # Maximizar ventana
    
    # Usar el perfil de Chrome existente para aprovechar sesión guardada
    options.add_argument("--user-data-dir=C:\\Users\\welli\\AppData\\Local\\Google\\Chrome\\User Data")
    options.add_argument("--profile-directory=Default")  # Usa el perfil predeterminado
    
    try:
        driver = webdriver.Chrome(options=options)
        return driver
    except Exception as e:
        print(f"Error al iniciar Chrome: {e}")
        raise

def publicar_en_facebook(driver, mensaje):
    """Realiza el proceso de publicación en Facebook"""
    try:
        print("Cargando Facebook...")
        driver.get("https://www.facebook.com")
        time.sleep(5)  # Esperar un poco más para que cargue completamente
        print("Facebook cargado correctamente.")
        guardar_captura(driver, "facebook_inicio.png")
        
        # Verificar si estamos en la página principal
        print("Verificando página principal...")
        current_url = driver.current_url
        if "login" in current_url or "checkpoint" in current_url:
            print("ERROR: Parece que no hay sesión guardada. Se requiere login manual.")
            guardar_captura(driver, "error_requiere_login.png")
            raise Exception("Se requiere inicio de sesión")
        
        # Buscar área para crear publicación
        print("Buscando área para crear publicación...")
        
        # Lista de selectores para intentar (en orden de prioridad)
        selectores_crear_post = [
            "//div[@role='button' and contains(@aria-label, 'Crear')]",
            "//div[@role='button' and contains(text(), '¿Qué estás pensando')]",
            "//span[contains(text(), '¿Qué estás pensando')]",
            "//div[contains(@aria-label, 'Crear publicación')]",
            "//div[contains(@class, 'x1lliihq')]//div[@role='button']",
            "//div[@role='button' and contains(@aria-label, 'Crear')]",
            "//div[contains(@class, 'xh8yej3')]//div[@role='button']"
        ]
        
        # Intentar cada selector
        post_area = None
        for selector in selectores_crear_post:
            print(f"Probando selector: {selector}")
            try:
                post_area = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                print(f"¡Selector encontrado!: {selector}")
                break
            except:
                continue
                
        if not post_area:
            # Si no encontramos ninguno, intentar buscar por JS
            print("Intentando localizar el área de publicación usando JavaScript...")
            try:
                # Buscar cualquier elemento que tenga texto como "¿Qué estás pensando?"
                js_script = """
                return Array.from(document.querySelectorAll('div[role="button"]')).find(
                    el => el.textContent.includes('¿Qué estás pensando') || 
                          el.textContent.includes('What') ||
                          (el.getAttribute('aria-label') && 
                           el.getAttribute('aria-label').includes('Crear'))
                );
                """
                post_area = driver.execute_script(js_script)
                if post_area:
                    print("Área de publicación encontrada mediante JavaScript.")
            except Exception as js_error:
                print(f"Error en búsqueda por JavaScript: {js_error}")
                
        if not post_area:
            print("ERROR: No se pudo encontrar el área para crear publicación.")
            guardar_captura(driver, "error_area_publicacion.png")
            raise Exception("No se encontró el área para crear publicación")
            
        # Hacer clic en el área para crear publicación
        driver.execute_script("arguments[0].click();", post_area)
        print("Área de publicación clickeada.")
        time.sleep(3)
        guardar_captura(driver, "despues_click_area.png")
        
        # Buscar el área de texto para escribir
        selectores_texto = [
            "//div[@contenteditable='true' and @role='textbox']",
            "//div[@data-contents='true']//div[@contenteditable='true']",
            "//div[contains(@aria-label, 'publicación')]",
            "//div[@role='textbox']"
        ]
        
        # Intentar cada selector para el área de texto
        text_area = None
        for selector in selectores_texto:
            print(f"Probando selector de área de texto: {selector}")
            try:
                text_area = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                print(f"Área de texto encontrada: {selector}")
                break
            except:
                continue
                
        if not text_area:
            # Intentar usando JavaScript
            print("Intentando encontrar área de texto usando JavaScript...")
            try:
                js_script = """
                return document.querySelector('div[contenteditable="true"][role="textbox"]') || 
                       document.querySelector('div[role="textbox"]') ||
                       Array.from(document.querySelectorAll('div[contenteditable="true"]')).find(
                           el => el.getAttribute('aria-label') && 
                                (el.getAttribute('aria-label').includes('publicación') ||
                                 el.getAttribute('aria-label').includes('post'))
                       );
                """
                text_area = driver.execute_script(js_script)
                if text_area:
                    print("Área de texto encontrada mediante JavaScript.")
            except Exception as js_error:
                print(f"Error en búsqueda por JavaScript: {js_error}")
                
        if not text_area:
            print("ERROR: No se pudo encontrar el área de texto.")
            guardar_captura(driver, "error_area_texto.png")
            raise Exception("No se encontró el área de texto para escribir")
            
        # Escribir el mensaje
        driver.execute_script("arguments[0].focus();", text_area)
        text_area.send_keys(mensaje)
        print("Mensaje escrito en el área de texto.")
        time.sleep(2)
        guardar_captura(driver, "mensaje_escrito.png")
        
        # Buscar y hacer clic en el botón de publicar
        selectores_publicar = [
            "//div[@role='button' and contains(text(), 'Publicar')]",
            "//span[text()='Publicar']",
            "//div[@aria-label='Publicar']",
            "//div[contains(@aria-label, 'post') and @role='button']"
        ]
        
        publish_button = None
        for selector in selectores_publicar:
            print(f"Probando selector para botón publicar: {selector}")
            try:
                publish_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                print(f"Botón de publicar encontrado: {selector}")
                break
            except:
                continue
                
        if not publish_button:
            # Intentar encontrar por JavaScript
            print("Intentando encontrar botón de publicar usando JavaScript...")
            try:
                js_script = """
                return Array.from(document.querySelectorAll('div[role="button"]')).find(
                    el => el.textContent.includes('Publicar') || 
                          el.textContent.includes('Post') ||
                          (el.getAttribute('aria-label') && 
                           (el.getAttribute('aria-label').includes('Publicar') ||
                            el.getAttribute('aria-label').includes('Post')))
                );
                """
                publish_button = driver.execute_script(js_script)
                if publish_button:
                    print("Botón de publicar encontrado mediante JavaScript.")
            except Exception as js_error:
                print(f"Error en búsqueda por JavaScript: {js_error}")
                
        if not publish_button:
            print("ERROR: No se pudo encontrar el botón de publicar.")
            guardar_captura(driver, "error_boton_publicar.png")
            raise Exception("No se encontró el botón de publicar")
            
        # Hacer clic en publicar
        driver.execute_script("arguments[0].click();", publish_button)
        print("Botón de publicar clickeado.")
        
        # Esperar confirmación de publicación
        time.sleep(5)
        print("Publicación completada exitosamente.")
        guardar_captura(driver, "publicacion_exitosa.png")
        
    except Exception as e:
        print(f"ERROR GENERAL: {str(e)}")
        print("Detalles del error:")
        traceback.print_exc()
        guardar_captura(driver, "error_general.png")
        raise

def main():
    """Función principal que ejecuta todo el proceso"""
    print("=" * 50)
    print("INICIANDO PROCESO DE PUBLICACIÓN")
    print("=" * 50)
    
    # Obtener directorio actual
    directorio_actual = os.getcwd()
    print(f"Directorio actual: {directorio_actual}")
    
    # Crear directorio para capturas
    crear_directorio_capturas()
    
    # Verificar directorio de publicaciones
    crear_directorio_publicaciones()
    
    # Obtener mensaje aleatorio
    mensaje = obtener_mensaje_aleatorio()
    
    # Iniciar navegador
    driver = None
    try:
        driver = iniciar_navegador()
        # Publicar en Facebook
        publicar_en_facebook(driver, mensaje)
    except Exception as e:
        print(f"Error en el proceso principal: {e}")
    finally:
        # Cerrar navegador
        if driver:
            print("Cerrando navegador en 5 segundos...")
            time.sleep(5)
            driver.quit()
            print("Navegador cerrado correctamente.")
    
    print("=" * 50)
    print("PROCESO FINALIZADO")
    print("=" * 50)

if __name__ == "__main__":
    main()