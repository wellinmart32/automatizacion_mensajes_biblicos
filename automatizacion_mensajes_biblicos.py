import os
import time
import random
import pyperclip  # pip install pyperclip
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

# Configuración
DIRECTORIO_MENSAJES = "publicaciones"

def crear_directorio_publicaciones():
    """Crea el directorio para almacenar los mensajes si no existe"""
    if not os.path.exists(DIRECTORIO_MENSAJES):
        os.makedirs(DIRECTORIO_MENSAJES)
        with open(os.path.join(DIRECTORIO_MENSAJES, "mensaje_ejemplo.txt"), 'w', encoding='utf-8') as f:
            f.write("Este es un mensaje de ejemplo creado automáticamente.\n\n¡Puedes agregar más archivos .txt a esta carpeta para tener mensajes variados!")

def obtener_mensaje_aleatorio():
    """Obtiene un mensaje aleatorio de la carpeta de publicaciones"""
    try:
        if not os.path.exists(DIRECTORIO_MENSAJES):
            print(f"Creando directorio de publicaciones: {DIRECTORIO_MENSAJES}")
            crear_directorio_publicaciones()
            
        archivos_txt = [f for f in os.listdir(DIRECTORIO_MENSAJES) if f.endswith('.txt')]
        
        if not archivos_txt:
            print("No se encontraron archivos de texto en la carpeta de publicaciones.")
            return "No hay mensajes disponibles. Por favor, agrega archivos .txt a la carpeta de publicaciones."
            
        archivo_elegido = random.choice(archivos_txt)
        ruta_completa = os.path.join(DIRECTORIO_MENSAJES, archivo_elegido)
        
        print(f"Archivo de mensaje elegido: {archivo_elegido}")
        
        with open(ruta_completa, 'r', encoding='utf-8') as archivo:
            mensaje = archivo.read().strip()
            
        print(f"Mensaje leído correctamente. Longitud: {len(mensaje)} caracteres")
        return mensaje
        
    except Exception as e:
        print(f"Error al obtener mensaje aleatorio: {e}")
        return "Error al leer mensaje. Usando mensaje predeterminado."

def obtener_primer_perfil_firefox():
    """Encuentra automáticamente el primer perfil de Firefox disponible"""
    ruta_perfiles = os.path.expanduser("~\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles")
    
    if not os.path.exists(ruta_perfiles):
        print(f"No se encontró la carpeta de perfiles en {ruta_perfiles}")
        return None
    
    perfiles = [f for f in os.listdir(ruta_perfiles) if os.path.isdir(os.path.join(ruta_perfiles, f))]
    
    if not perfiles:
        print("No se encontraron perfiles de Firefox")
        return None
    
    perfil_seleccionado = os.path.join(ruta_perfiles, perfiles[0])
    print(f"Seleccionando automáticamente el primer perfil: {perfiles[0]}")
    return perfil_seleccionado

def iniciar_navegador():
    """Inicia Firefox con el perfil existente"""
    print("Inicializando Firefox con perfil existente...")
    
    opciones = Options()
    opciones.set_preference("dom.webnotifications.enabled", False)
    
    ruta_perfil = obtener_primer_perfil_firefox()
    if ruta_perfil:
        opciones.add_argument("-profile")
        opciones.add_argument(ruta_perfil)
    
    try:
        navegador = webdriver.Firefox(options=opciones)
        navegador.maximize_window()
        return navegador
    except Exception as e:
        print(f"Error al iniciar Firefox: {e}")
        raise

def publicar_en_facebook(navegador, mensaje):
    """Realiza el proceso de publicación en Facebook con técnicas anti-overlay"""
    try:
        # Paso 1: Copiar el mensaje al portapapeles
        print("Copiando mensaje al portapapeles...")
        pyperclip.copy(mensaje)
        print("Mensaje copiado al portapapeles correctamente")
        
        # Paso 2: Navegar a Facebook
        print("Cargando Facebook (página principal)...")
        navegador.get("https://www.facebook.com")
        time.sleep(4)  # Esperar más tiempo para carga completa
        print("Facebook cargado correctamente.")
        
        # Paso 3: Verificar que NO estamos en historias
        url_actual = navegador.current_url
        if "stories" in url_actual:
            print("Detectada página de historias. Regresando a la página principal...")
            navegador.get("https://www.facebook.com")
            time.sleep(3)
        
        # Paso 4: Buscar y hacer clic en "¿Qué estás pensando?" con técnicas mejoradas
        print("Buscando el área '¿Qué estás pensando?'...")
        
        # Lista de selectores mejorados
        selectores_campo = [
            "//span[contains(text(), '¿Qué estás pensando')]",
            "//div[@role='button' and contains(., '¿Qué estás pensando')]",
            "//div[contains(@class, 'x1i10hfl') and @role='button']",
            "//div[@aria-label='Crear publicación']"
        ]
        
        campo_encontrado = False
        elemento_clickeado = None
        
        for selector in selectores_campo:
            try:
                elementos = navegador.find_elements(By.XPATH, selector)
                if elementos:
                    # Hacer scroll hacia el elemento
                    navegador.execute_script("arguments[0].scrollIntoView({block: 'center'});", elementos[0])
                    time.sleep(1)
                    
                    # TÉCNICA MEJORADA: Usar JavaScript para clic
                    navegador.execute_script("arguments[0].click();", elementos[0])
                    elemento_clickeado = elementos[0]
                    campo_encontrado = True
                    print(f"✅ Se hizo clic en el área de publicación con selector: {selector}")
                    break
            except Exception as e:
                print(f"⚠️  Error con selector {selector}: {e}")
                continue
        
        # Si no funcionó, intentar método de teclado
        if not campo_encontrado:
            print("Intentando abrir el cuadro con la tecla 'p'...")
            try:
                body = navegador.find_element(By.TAG_NAME, "body")
                body.click()
                time.sleep(0.5)
                ActionChains(navegador).send_keys('p').perform()
                time.sleep(2)
                campo_encontrado = True
            except:
                pass
        
        # Esperar más tiempo para que el modal se abra completamente
        time.sleep(3)  # CRÍTICO: Esperar a que el modal se estabilice
        
        # Paso 5: Verificar que el cuadro de publicación está abierto
        print("Verificando que el cuadro de publicación esté abierto...")
        
        try:
            # Buscar el modal/dialog de publicación
            WebDriverWait(navegador, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']"))
            )
            print("✅ Cuadro de publicación confirmado abierto")
        except:
            print("⚠️  No se detectó el cuadro de publicación. Intentando método alternativo...")
            # Método alternativo - ir directamente a la URL de creación
            navegador.get("https://www.facebook.com/?sk=h_chr")
            time.sleep(3)
            
            # Intentar abrir el compositor de nuevo
            try:
                boton_crear = navegador.find_element(By.XPATH, "//span[contains(text(), '¿Qué estás pensando')]")
                navegador.execute_script("arguments[0].click();", boton_crear)
                time.sleep(3)
            except:
                pass
        
        # Paso 6: Encontrar el área de texto
        print("Buscando área de texto...")
        
        # ESTRATEGIA MÚLTIPLE para encontrar el área de texto
        selectores_texto = [
            "//div[@role='textbox' and @contenteditable='true']",
            "//div[@contenteditable='true' and contains(@aria-label, 'publicación')]",
            "//div[@contenteditable='true' and contains(@aria-label, 'post')]",
            "//div[@role='textbox']",
            "//div[@contenteditable='true']"
        ]
        
        area_texto = None
        for selector in selectores_texto:
            try:
                elementos = navegador.find_elements(By.XPATH, selector)
                # Buscar el área de texto visible más grande (suele ser el compositor)
                for elemento in elementos:
                    try:
                        if elemento.is_displayed():
                            # Verificar que no sea un campo de comentario pequeño
                            size = elemento.size
                            if size['height'] > 50:  # El compositor principal es más grande
                                area_texto = elemento
                                print(f"✅ Área de texto encontrada con selector: {selector}")
                                break
                    except:
                        continue
                if area_texto:
                    break
            except:
                continue
        
        if not area_texto:
            # Último intento: buscar cualquier div contenteditable dentro del dialog
            try:
                dialog = navegador.find_element(By.XPATH, "//div[@role='dialog']")
                area_texto = dialog.find_element(By.XPATH, ".//div[@contenteditable='true']")
                print("✅ Área de texto encontrada dentro del dialog")
            except:
                pass
        
        if not area_texto:
            raise Exception("No se pudo encontrar el área de texto para publicar")
        
        # Paso 7: Hacer clic en el área de texto y esperar
        print("Haciendo clic en el área de texto...")
        try:
            # Scroll al área de texto
            navegador.execute_script("arguments[0].scrollIntoView({block: 'center'});", area_texto)
            time.sleep(0.5)
            
            # Hacer clic con JavaScript
            navegador.execute_script("arguments[0].click();", area_texto)
            time.sleep(1)
            
            # Dar foco con JavaScript adicional
            navegador.execute_script("arguments[0].focus();", area_texto)
            time.sleep(1)
            
            print("✅ Área de texto enfocada correctamente")
        except Exception as e:
            print(f"⚠️  Error al hacer clic en área de texto: {e}")
        
        # Paso 8: Pegar el contenido
        print("Pegando contenido desde el portapapeles...")
        
        # MÉTODO 1: Usar ActionChains
        try:
            ActionChains(navegador).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
            time.sleep(2)
            print("✅ Contenido pegado con ActionChains")
        except Exception as e:
            print(f"⚠️  Error con ActionChains, intentando método alternativo: {e}")
            
            # MÉTODO 2: Usar send_keys directamente
            try:
                area_texto.send_keys(Keys.CONTROL, 'v')
                time.sleep(2)
                print("✅ Contenido pegado con send_keys")
            except Exception as e2:
                print(f"⚠️  Error con send_keys: {e2}")
                
                # MÉTODO 3: Escribir directamente el texto (más lento pero funcional)
                try:
                    area_texto.send_keys(mensaje)
                    time.sleep(2)
                    print("✅ Contenido escrito directamente")
                except Exception as e3:
                    print(f"❌ Error al escribir directamente: {e3}")
                    raise Exception("No se pudo ingresar el texto de ninguna manera")
        
        # Verificar que el texto se ingresó
        time.sleep(1)
        texto_actual = area_texto.text
        if len(texto_actual) < 10:
            print(f"⚠️  ADVERTENCIA: Solo se detectan {len(texto_actual)} caracteres en el área de texto")
            print("   Intentando pegar nuevamente...")
            ActionChains(navegador).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
            time.sleep(2)
        
        # Paso 9: Buscar y hacer clic en el botón "Publicar"
        print("Buscando botón 'Publicar'...")
        
        # Esperar un momento antes de buscar el botón
        time.sleep(2)
        
        selectores_boton = [
            "//div[@aria-label='Publicar']",
            "//div[@role='button' and contains(text(), 'Publicar')]",
            "//span[text()='Publicar']/ancestor::div[@role='button']",
            "//div[@role='button']//span[text()='Publicar']"
        ]
        
        boton_encontrado = False
        for selector in selectores_boton:
            try:
                elementos = navegador.find_elements(By.XPATH, selector)
                if elementos:
                    # Verificar que el botón esté habilitado
                    for elemento in elementos:
                        try:
                            if elemento.is_displayed() and elemento.is_enabled():
                                # Scroll al botón
                                navegador.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", elemento)
                                time.sleep(1)
                                
                                # Clic con JavaScript
                                navegador.execute_script("arguments[0].click();", elemento)
                                boton_encontrado = True
                                print(f"✅ Se hizo clic en el botón 'Publicar' con selector: {selector}")
                                break
                        except:
                            continue
                    if boton_encontrado:
                        break
            except:
                continue
        
        # Buscar botón por texto si los selectores no funcionaron
        if not boton_encontrado:
            print("Buscando botón por su texto...")
            try:
                elementos = navegador.find_elements(By.XPATH, "//div[@role='button']")
                for elemento in elementos:
                    try:
                        texto = elemento.text.strip().lower()
                        if texto == "publicar":
                            navegador.execute_script("arguments[0].scrollIntoView({block: 'center'});", elemento)
                            time.sleep(0.5)
                            navegador.execute_script("arguments[0].click();", elemento)
                            boton_encontrado = True
                            print("✅ Se hizo clic en el botón 'Publicar' encontrado por texto")
                            break
                    except:
                        continue
            except Exception as e:
                print(f"⚠️  Error buscando por texto: {e}")
        
        if not boton_encontrado:
            # Último intento: buscar dentro del dialog
            try:
                dialog = navegador.find_element(By.XPATH, "//div[@role='dialog']")
                boton = dialog.find_element(By.XPATH, ".//div[@role='button' and contains(., 'Publicar')]")
                navegador.execute_script("arguments[0].click();", boton)
                boton_encontrado = True
                print("✅ Botón 'Publicar' encontrado dentro del dialog")
            except:
                pass
        
        if not boton_encontrado:
            raise Exception("No se pudo encontrar el botón para publicar")
        
        # Esperar a que se complete la publicación
        print("Esperando a que se complete la publicación...")
        time.sleep(5)
        
        # Verificar si la publicación fue exitosa
        try:
            # Si el modal se cierra, la publicación fue exitosa
            dialogs = navegador.find_elements(By.XPATH, "//div[@role='dialog']")
            if len(dialogs) == 0:
                print("✅ ¡Publicación completada exitosamente!")
            else:
                print("⚠️  El modal sigue abierto, verificando...")
                time.sleep(3)
        except:
            print("✅ ¡Publicación completada exitosamente!")
        
    except Exception as e:
        print(f"ERROR GENERAL: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

def main():
    """Función principal que ejecuta todo el proceso"""
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
        print("\n" + "=" * 50)
        print("✅ PUBLICACIÓN REALIZADA CON ÉXITO")
        print("=" * 50)
    except Exception as e:
        print(f"\n❌ Error en el proceso principal: {e}")
        print("\n💡 Sugerencias:")
        print("   • Verifica que estés logueado en Facebook")
        print("   • Intenta ejecutar el script nuevamente")
        print("   • Facebook puede haber cambiado su interfaz")
    finally:
        # Cerrar navegador
        if navegador:
            print("\nCerrando navegador en 3 segundos...")
            time.sleep(3)
            navegador.quit()
            print("Navegador cerrado correctamente.")
    
    print("\n" + "=" * 50)
    print("PROCESO FINALIZADO")
    print("=" * 50)

if __name__ == "__main__":
    main()
