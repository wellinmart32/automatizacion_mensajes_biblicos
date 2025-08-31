import os
import time
import random
import pyperclip  # Necesitarás instalar esto: pip install pyperclip
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

# Configuración
DIRECTORIO_MENSAJES = "publicaciones"  # Carpeta en el mismo directorio que el script

def crear_directorio_publicaciones():
    """
    Crea el directorio para almacenar los mensajes si no existe
    """
    if not os.path.exists(DIRECTORIO_MENSAJES):
        os.makedirs(DIRECTORIO_MENSAJES)
        # Crear un mensaje de ejemplo si es la primera vez
        with open(os.path.join(DIRECTORIO_MENSAJES, "mensaje_ejemplo.txt"), 'w', encoding='utf-8') as f:
            f.write("Este es un mensaje de ejemplo creado automáticamente.\n\n¡Puedes agregar más archivos .txt a esta carpeta para tener mensajes variados!")

def obtener_mensaje_aleatorio():
    """
    Obtiene un mensaje aleatorio de la carpeta de publicaciones
    """
    try:
        # Verificar que exista el directorio
        if not os.path.exists(DIRECTORIO_MENSAJES):
            print(f"Creando directorio de publicaciones: {DIRECTORIO_MENSAJES}")
            crear_directorio_publicaciones()
            
        # Obtener todos los archivos de texto
        archivos_txt = [f for f in os.listdir(DIRECTORIO_MENSAJES) if f.endswith('.txt')]
        
        if not archivos_txt:
            print("No se encontraron archivos de texto en la carpeta de publicaciones.")
            return "No hay mensajes disponibles. Por favor, agrega archivos .txt a la carpeta de publicaciones."
            
        # Elegir un archivo aleatorio
        archivo_elegido = random.choice(archivos_txt)
        ruta_completa = os.path.join(DIRECTORIO_MENSAJES, archivo_elegido)
        
        print(f"Archivo de mensaje elegido: {archivo_elegido}")
        
        # Leer el contenido del archivo
        with open(ruta_completa, 'r', encoding='utf-8') as archivo:
            mensaje = archivo.read().strip()
            
        print(f"Mensaje leído correctamente. Longitud: {len(mensaje)} caracteres")
        return mensaje
        
    except Exception as e:
        print(f"Error al obtener mensaje aleatorio: {e}")
        return "Error al leer mensaje. Usando mensaje predeterminado."

def obtener_primer_perfil_firefox():
    """
    Encuentra automáticamente el primer perfil de Firefox disponible
    """
    # Ruta a los perfiles de Firefox
    ruta_perfiles = os.path.expanduser("~\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles")
    
    if not os.path.exists(ruta_perfiles):
        print(f"No se encontró la carpeta de perfiles en {ruta_perfiles}")
        return None
    
    perfiles = [f for f in os.listdir(ruta_perfiles) if os.path.isdir(os.path.join(ruta_perfiles, f))]
    
    if not perfiles:
        print("No se encontraron perfiles de Firefox")
        return None
    
    # Seleccionar automáticamente el primer perfil
    perfil_seleccionado = os.path.join(ruta_perfiles, perfiles[0])
    print(f"Seleccionando automáticamente el primer perfil: {perfiles[0]}")
    return perfil_seleccionado

def iniciar_navegador():
    """
    Inicia Firefox con el perfil existente
    """
    print("Inicializando Firefox con perfil existente...")
    
    opciones = Options()
    opciones.set_preference("dom.webnotifications.enabled", False)  # Desactivar notificaciones
    
    # Obtener y usar el primer perfil de Firefox
    ruta_perfil = obtener_primer_perfil_firefox()
    if ruta_perfil:
        opciones.add_argument("-profile")
        opciones.add_argument(ruta_perfil)
    
    try:
        navegador = webdriver.Firefox(options=opciones)
        navegador.maximize_window()  # Maximizar ventana
        return navegador
    except Exception as e:
        print(f"Error al iniciar Firefox: {e}")
        raise

def publicar_en_facebook(navegador, mensaje):
    """
    Realiza el proceso de publicación en Facebook usando método directo
    """
    try:
        # Paso 1: Copiar el mensaje al portapapeles
        print("Copiando mensaje al portapapeles...")
        pyperclip.copy(mensaje)
        print("Mensaje copiado al portapapeles correctamente")
        
        # Paso 2: Navegar a Facebook página principal
        print("Cargando Facebook (página principal)...")
        navegador.get("https://www.facebook.com")
        time.sleep(3)  # Esperar a que cargue completamente
        print("Facebook cargado correctamente.")
        
        # Paso 3: Verificar que estamos en la página principal y no en historias
        url_actual = navegador.current_url
        if "stories" in url_actual:
            print("Detectada página de historias. Regresando a la página principal...")
            navegador.get("https://www.facebook.com")
            time.sleep(3)
        
        # Paso 4: Hacer clic directamente en "¿Qué estás pensando?"
        print("Buscando el área '¿Qué estás pensando?'...")
        
        # Lista de selectores para el área "¿Qué estás pensando?"
        selectores_campo = [
            "//span[contains(text(), '¿Qué estás pensando')]",
            "//div[contains(@class, 'x1i10hfl') and @role='button']",
            "//div[@aria-label='Crear publicación']",
            "//div[contains(@class, 'xzsf02u')]"
        ]
        
        campo_encontrado = False
        for selector in selectores_campo:
            try:
                elementos = navegador.find_elements(By.XPATH, selector)
                if elementos:
                    # Hacer scroll hacia el elemento
                    navegador.execute_script("arguments[0].scrollIntoView({block: 'center'});", elementos[0])
                    time.sleep(1)
                    # Hacer clic en el elemento
                    navegador.execute_script("arguments[0].click();", elementos[0])
                    campo_encontrado = True
                    print(f"Se hizo clic en el área de publicación con selector: {selector}")
                    break
            except Exception as e:
                print(f"Error con selector {selector}: {e}")
                continue
        
        # Si no se pudo hacer clic con los selectores, intentar el método de 'p'
        if not campo_encontrado:
            print("Intentando abrir el cuadro con la tecla 'p'...")
            body = navegador.find_element(By.TAG_NAME, "body")
            body.click()  # Asegurarse de que la página tiene el foco
            time.sleep(1)
            ActionChains(navegador).send_keys('p').perform()
            time.sleep(3)
        
        # Verificar si se abrió el cuadro de publicación
        dialogos = navegador.find_elements(By.XPATH, "//div[@role='dialog']")
        if not dialogos:
            print("ERROR: No se pudo abrir el cuadro de publicación. Intentando método alternativo...")
            # Método alternativo - ir directamente a la URL de creación
            navegador.get("https://www.facebook.com/?composer=true")
            time.sleep(3)
        
        # Paso 5: Encontrar el área de texto y pegar el contenido
        print("Buscando área de texto...")
        
        # Esperar a que aparezca el área de texto (máximo 10 segundos)
        try:
            area_texto = WebDriverWait(navegador, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@role='textbox']"))
            )
            print("Área de texto encontrada.")
            
            # Hacer clic en el área de texto
            navegador.execute_script("arguments[0].click();", area_texto)
            time.sleep(1)
            
            # Pegar el contenido desde el portapapeles
            print("Pegando contenido desde el portapapeles...")
            ActionChains(navegador).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
            time.sleep(2)
        except Exception as e:
            print(f"Error al encontrar área de texto: {e}")
            raise Exception("No se pudo encontrar el área de texto para publicar")
        
        # Paso 6: Buscar y hacer clic en el botón "Publicar"
        print("Buscando botón 'Publicar'...")
        
        # Esperar a que aparezca el botón Publicar (máximo 10 segundos)
        try:
            # Intentar con varios selectores para mayor seguridad
            selectores_boton = [
                "//div[@role='button' and text()='Publicar']",
                "//div[@aria-label='Publicar']",
                "//span[text()='Publicar']/ancestor::div[@role='button']",
                "//div[contains(@class, 'x1n2onr6') and text()='Publicar']"
            ]
            
            boton_encontrado = False
            for selector in selectores_boton:
                elementos = navegador.find_elements(By.XPATH, selector)
                if elementos:
                    # Hacer scroll para asegurar que el botón sea visible
                    navegador.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", elementos[0])
                    time.sleep(1)
                    # Hacer clic en el botón
                    navegador.execute_script("arguments[0].click();", elementos[0])
                    boton_encontrado = True
                    print(f"Se hizo clic en el botón 'Publicar' con selector: {selector}")
                    break
            
            # Si no se encontró el botón con selectores, intentar encontrarlo por texto
            if not boton_encontrado:
                print("Buscando botón por su texto...")
                # Buscar todos los elementos que podrían ser botones
                elementos = navegador.find_elements(By.XPATH, "//div[@role='button']")
                for elemento in elementos:
                    try:
                        texto = elemento.text.strip().lower()
                        if texto == "publicar":
                            navegador.execute_script("arguments[0].click();", elemento)
                            boton_encontrado = True
                            print("Se hizo clic en el botón 'Publicar' encontrado por texto")
                            break
                    except:
                        continue
            
            # Si aún no se encuentra, buscar por el botón azul (que suele ser el de publicar)
            if not boton_encontrado:
                print("Buscando botón azul (típicamente el de Publicar)...")
                botones_azules = navegador.find_elements(By.XPATH, "//div[contains(@class, 'x1n2onr6')]")
                if botones_azules:
                    navegador.execute_script("arguments[0].click();", botones_azules[0])
                    boton_encontrado = True
                    print("Se hizo clic en el botón azul que podría ser 'Publicar'")
            
            if not boton_encontrado:
                raise Exception("No se pudo encontrar el botón para publicar")
                
        except Exception as e:
            print(f"Error al buscar botón 'Publicar': {e}")
            raise
        
        # Esperar a que se complete la publicación
        print("Esperando a que se complete la publicación...")
        time.sleep(5)
        print("¡Publicación completada exitosamente!")
        
    except Exception as e:
        print(f"ERROR GENERAL: {str(e)}")
        raise

def main():
    """
    Función principal que ejecuta todo el proceso
    """
    print("=" * 50)
    print("INICIANDO PROCESO DE PUBLICACIÓN")
    print("=" * 50)
    
    # Verificar directorio de publicaciones
    crear_directorio_publicaciones()
    
    # Obtener mensaje aleatorio
    mensaje = obtener_mensaje_aleatorio()
    
    # Iniciar navegador
    navegador = None
    try:
        navegador = iniciar_navegador()
        # Publicar en Facebook
        publicar_en_facebook(navegador, mensaje)
        print("Publicación realizada con éxito.")
    except Exception as e:
        print(f"Error en el proceso principal: {e}")
    finally:
        # Cerrar navegador
        if navegador:
            print("Cerrando navegador...")
            navegador.quit()
            print("Navegador cerrado correctamente.")
    
    print("=" * 50)
    print("PROCESO FINALIZADO")
    print("=" * 50)

if __name__ == "__main__":
    main()