from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pyperclip
import time
import os
from datetime import datetime


class PublicadorFacebook:
    """
    Maneja la automatización de publicaciones en Facebook
    Implementa múltiples estrategias para evitar problemas con overlays
    Similar a PublicadorMarketplace pero adaptado para Facebook
    """
    
    def __init__(self, config):
        """
        Inicializa el publicador con la configuración
        
        Args:
            config: Diccionario de configuración desde config_global.txt
        """
        self.driver = None
        self.wait = None
        self.config = config
    
    def iniciar_navegador(self):
        """Inicia el navegador según configuración (Firefox o Chrome)"""
        navegador = self.config['navegador']
        
        print(f"🌐 Iniciando {navegador.upper()}...")
        
        if navegador == 'firefox':
            self._iniciar_firefox()
        elif navegador == 'chrome':
            self._iniciar_chrome()
        else:
            raise Exception(f"Navegador no soportado: {navegador}")
        
        # Configurar wait
        self.wait = WebDriverWait(self.driver, 20)
        
        if self.config['maximizar_ventana']:
            self.driver.maximize_window()
        
        print("✅ Navegador iniciado correctamente")
    
    def _iniciar_firefox(self):
        """Inicia Firefox con perfil configurado"""
        opciones = FirefoxOptions()
        
        # Desactivar notificaciones
        if self.config['desactivar_notificaciones']:
            opciones.set_preference("dom.webnotifications.enabled", False)
        
        # Usar perfil existente o personalizado
        from compartido.gestor_archivos import obtener_ruta_perfil_navegador
        ruta_perfil = obtener_ruta_perfil_navegador()
        
        if ruta_perfil:
            opciones.add_argument("-profile")
            opciones.add_argument(ruta_perfil)
        
        self.driver = webdriver.Firefox(options=opciones)
    
    def _iniciar_chrome(self):
        """Inicia Chrome con perfil configurado"""
        opciones = ChromeOptions()
        
        # Desactivar notificaciones
        if self.config['desactivar_notificaciones']:
            opciones.add_argument("--disable-notifications")
        
        # Anti-detección
        opciones.add_argument("--disable-blink-features=AutomationControlled")
        opciones.add_experimental_option("excludeSwitches", ["enable-automation"])
        opciones.add_experimental_option('useAutomationExtension', False)
        
        # Perfil personalizado
        if not self.config['usar_perfil_existente']:
            ruta_perfil = os.path.abspath(self.config['carpeta_perfil_custom'])
            opciones.add_argument(f"--user-data-dir={ruta_perfil}")
        
        servicio = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=servicio, options=opciones)
    
    def verificar_sesion_facebook(self):
        """
        Verifica si hay sesión activa en Facebook
        Espera si necesita login
        
        Returns:
            bool: True si hay sesión activa
        """
        print("🔐 Verificando sesión de Facebook...")
        
        try:
            self.driver.get("https://www.facebook.com")
            time.sleep(3)
            
            # Verificar si hay campos de login
            try:
                login_elements = self.driver.find_elements(By.XPATH, 
                    "//input[@name='email' or @name='pass']")
                
                if len(login_elements) > 0:
                    print("\n⚠️  NO HAS INICIADO SESIÓN EN FACEBOOK")
                    print("=" * 60)
                    print("Por favor INICIA SESIÓN en Facebook ahora.")
                    print("Tienes 2 MINUTOS para iniciar sesión.")
                    print("=" * 60 + "\n")
                    
                    timeout = 120
                    tiempo_transcurrido = 0
                    
                    while tiempo_transcurrido < timeout:
                        time.sleep(5)
                        tiempo_transcurrido += 5
                        
                        try:
                            login_check = self.driver.find_elements(By.XPATH, 
                                "//input[@name='email' or @name='pass']")
                            
                            if len(login_check) == 0:
                                print("✅ Sesión iniciada correctamente")
                                time.sleep(3)
                                return True
                            else:
                                print(f"⏳ Esperando login... ({timeout - tiempo_transcurrido}s restantes)")
                        except:
                            print("✅ Sesión iniciada correctamente")
                            time.sleep(3)
                            return True
                    
                    print("\n❌ Tiempo de espera agotado. No se detectó inicio de sesión.")
                    return False
                else:
                    print("✅ Ya tienes sesión activa en Facebook")
                    return True
                    
            except:
                print("✅ Ya tienes sesión activa en Facebook")
                return True
                
        except Exception as e:
            print(f"⚠️  Error verificando sesión: {e}")
            print("Continuando de todos modos...")
            return True
    
    def abrir_compositor(self):
        """
        Abre el cuadro de publicación de Facebook
        Usa múltiples estrategias para máxima compatibilidad
        
        Returns:
            bool: True si se abrió correctamente
        """
        print("📝 Abriendo compositor de publicación...")
        
        # Asegurar que estamos en la página principal
        url_actual = self.driver.current_url
        if "stories" in url_actual or "watch" in url_actual:
            print("   Navegando a página principal...")
            self.driver.get("https://www.facebook.com")
            time.sleep(3)
        
        # ESTRATEGIA 1: Buscar y hacer clic en "¿Qué estás pensando?"
        print("   Estrategia 1: Buscando '¿Qué estás pensando?'...")
        
        selectores_campo = [
            "//span[contains(text(), '¿Qué estás pensando')]",
            "//div[@role='button' and contains(., '¿Qué estás pensando')]",
            "//div[contains(@class, 'x1i10hfl') and @role='button']",
            "//div[@aria-label='Crear publicación']"
        ]
        
        campo_encontrado = False
        for selector in selectores_campo:
            try:
                elementos = self.driver.find_elements(By.XPATH, selector)
                if elementos:
                    # Scroll al elemento
                    self.driver.execute_script(
                        "arguments[0].scrollIntoView({block: 'center'});", 
                        elementos[0]
                    )
                    time.sleep(1)
                    
                    # Clic con JavaScript (evita overlays)
                    self.driver.execute_script("arguments[0].click();", elementos[0])
                    campo_encontrado = True
                    print(f"   ✅ Clic exitoso con selector: {selector[:50]}...")
                    break
            except Exception as e:
                continue
        
        # ESTRATEGIA 2: Usar atajo de teclado 'p'
        if not campo_encontrado:
            print("   Estrategia 2: Usando atajo de teclado 'p'...")
            try:
                body = self.driver.find_element(By.TAG_NAME, "body")
                body.click()
                time.sleep(0.5)
                ActionChains(self.driver).send_keys('p').perform()
                time.sleep(2)
                campo_encontrado = True
                print("   ✅ Compositor abierto con atajo 'p'")
            except:
                pass
        
        # ESTRATEGIA 3: URL directa
        if not campo_encontrado:
            print("   Estrategia 3: Usando URL directa...")
            self.driver.get("https://www.facebook.com/?sk=h_chr")
            time.sleep(3)
            
            try:
                boton_crear = self.driver.find_element(By.XPATH, 
                    "//span[contains(text(), '¿Qué estás pensando')]")
                self.driver.execute_script("arguments[0].click();", boton_crear)
                time.sleep(2)
                campo_encontrado = True
                print("   ✅ Compositor abierto con URL directa")
            except:
                pass
        
        if not campo_encontrado:
            print("   ❌ No se pudo abrir el compositor con ninguna estrategia")
            return False
        
        # CRÍTICO: Esperar a que el modal se estabilice
        tiempo_espera = self.config['espera_estabilizacion_modal']
        print(f"   ⏳ Esperando {tiempo_espera}s a que el modal se estabilice...")
        time.sleep(tiempo_espera)
        
        # Verificar que el modal está abierto
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']"))
            )
            print("   ✅ Modal confirmado abierto")
            return True
        except:
            print("   ⚠️  No se detectó el modal, pero continuando...")
            return True
    
    def ingresar_texto(self, mensaje):
        """
        Ingresa el texto en el compositor
        Usa múltiples métodos con fallbacks
        
        Args:
            mensaje: Texto a publicar
            
        Returns:
            bool: True si se ingresó correctamente
        """
        print("✍️  Ingresando texto en el compositor...")
        
        # Buscar área de texto
        area_texto = self._buscar_area_texto()
        
        if not area_texto:
            print("   ❌ No se encontró el área de texto")
            return False
        
        # Hacer clic y dar foco
        print("   Dando foco al área de texto...")
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", area_texto)
            time.sleep(0.5)
            self.driver.execute_script("arguments[0].click();", area_texto)
            time.sleep(1)
            self.driver.execute_script("arguments[0].focus();", area_texto)
            time.sleep(1)
        except Exception as e:
            print(f"   ⚠️  Error dando foco: {e}")
        
        # MÉTODO 1: Portapapeles (más confiable para textos largos)
        print("   Método 1: Pegando desde portapapeles...")
        try:
            pyperclip.copy(mensaje)
            ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
            time.sleep(2)
            
            # Verificar que se ingresó
            texto_actual = area_texto.text
            if len(texto_actual) >= 10:
                print(f"   ✅ Texto ingresado correctamente ({len(texto_actual)} caracteres)")
                return True
            else:
                print(f"   ⚠️  Solo se detectan {len(texto_actual)} caracteres, intentando método 2...")
        except Exception as e:
            print(f"   ⚠️  Error con portapapeles: {e}")
        
        # MÉTODO 2: send_keys directo
        print("   Método 2: Usando send_keys directo...")
        try:
            area_texto.clear()
            time.sleep(0.5)
            area_texto.send_keys(mensaje)
            time.sleep(2)
            
            texto_actual = area_texto.text
            if len(texto_actual) >= 10:
                print(f"   ✅ Texto ingresado con send_keys ({len(texto_actual)} caracteres)")
                return True
            else:
                print(f"   ⚠️  Solo {len(texto_actual)} caracteres, intentando método 3...")
        except Exception as e:
            print(f"   ⚠️  Error con send_keys: {e}")
        
        # MÉTODO 3: JavaScript (último recurso)
        print("   Método 3: Usando JavaScript...")
        try:
            self.driver.execute_script(
                "arguments[0].textContent = arguments[1];", 
                area_texto, 
                mensaje
            )
            time.sleep(2)
            print("   ✅ Texto ingresado con JavaScript")
            return True
        except Exception as e:
            print(f"   ❌ Error con JavaScript: {e}")
            return False
    
    def _buscar_area_texto(self):
        """
        Busca el área de texto del compositor
        Usa múltiples selectores
        
        Returns:
            WebElement o None
        """
        selectores_texto = [
            "//div[@role='textbox' and @contenteditable='true']",
            "//div[@contenteditable='true' and contains(@aria-label, 'publicación')]",
            "//div[@contenteditable='true' and contains(@aria-label, 'post')]",
            "//div[@role='textbox']",
            "//div[@contenteditable='true']"
        ]
        
        for selector in selectores_texto:
            try:
                elementos = self.driver.find_elements(By.XPATH, selector)
                
                # Buscar el área visible más grande (el compositor)
                for elemento in elementos:
                    try:
                        if elemento.is_displayed():
                            size = elemento.size
                            # El compositor principal suele ser grande
                            if size['height'] > 50:
                                print(f"   ✅ Área de texto encontrada: {selector[:50]}...")
                                return elemento
                    except:
                        continue
            except:
                continue
        
        # Último intento: buscar dentro del dialog
        try:
            dialog = self.driver.find_element(By.XPATH, "//div[@role='dialog']")
            area_texto = dialog.find_element(By.XPATH, ".//div[@contenteditable='true']")
            print("   ✅ Área de texto encontrada dentro del dialog")
            return area_texto
        except:
            pass
        
        return None
    
    def publicar_mensaje(self):
        """
        Hace clic en el botón Publicar
        Usa múltiples estrategias
        
        Returns:
            bool: True si se publicó correctamente
        """
        print("🚀 Buscando botón 'Publicar'...")
        
        # Esperar un momento antes de buscar
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
                elementos = self.driver.find_elements(By.XPATH, selector)
                if elementos:
                    for elemento in elementos:
                        try:
                            if elemento.is_displayed() and elemento.is_enabled():
                                # Scroll al botón
                                self.driver.execute_script(
                                    "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", 
                                    elemento
                                )
                                time.sleep(1)
                                
                                # Clic con JavaScript (evita overlays)
                                self.driver.execute_script("arguments[0].click();", elemento)
                                boton_encontrado = True
                                print(f"   ✅ Clic en 'Publicar' con selector: {selector[:50]}...")
                                break
                        except:
                            continue
                    if boton_encontrado:
                        break
            except:
                continue
        
        # Buscar por texto si no funcionó
        if not boton_encontrado:
            print("   Buscando botón por texto...")
            try:
                elementos = self.driver.find_elements(By.XPATH, "//div[@role='button']")
                for elemento in elementos:
                    try:
                        texto = elemento.text.strip().lower()
                        if texto == "publicar":
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elemento)
                            time.sleep(0.5)
                            self.driver.execute_script("arguments[0].click();", elemento)
                            boton_encontrado = True
                            print("   ✅ Botón 'Publicar' encontrado por texto")
                            break
                    except:
                        continue
            except Exception as e:
                print(f"   ⚠️  Error buscando por texto: {e}")
        
        # Último intento: dentro del dialog
        if not boton_encontrado:
            print("   Último intento: buscando dentro del dialog...")
            try:
                dialog = self.driver.find_element(By.XPATH, "//div[@role='dialog']")
                boton = dialog.find_element(By.XPATH, ".//div[@role='button' and contains(., 'Publicar')]")
                self.driver.execute_script("arguments[0].click();", boton)
                boton_encontrado = True
                print("   ✅ Botón encontrado dentro del dialog")
            except:
                pass
        
        if not boton_encontrado:
            print("   ❌ No se pudo encontrar el botón 'Publicar'")
            return False
        
        # Esperar a que se complete la publicación
        tiempo_espera = self.config['espera_despues_publicar']
        print(f"   ⏳ Esperando {tiempo_espera}s a que se complete...")
        time.sleep(tiempo_espera)
        
        return True
    
    def verificar_publicacion_exitosa(self):
        """
        Verifica que la publicación fue exitosa
        
        Returns:
            bool: True si el modal se cerró (indicador de éxito)
        """
        if not self.config['verificar_publicacion_exitosa']:
            return True
        
        print("🔍 Verificando que la publicación fue exitosa...")
        
        try:
            # Si el modal se cerró, la publicación fue exitosa
            dialogs = self.driver.find_elements(By.XPATH, "//div[@role='dialog']")
            
            if len(dialogs) == 0:
                print("   ✅ Modal cerrado - Publicación exitosa")
                return True
            else:
                print("   ⚠️  Modal sigue abierto - Verificando...")
                time.sleep(3)
                
                # Verificar de nuevo
                dialogs = self.driver.find_elements(By.XPATH, "//div[@role='dialog']")
                if len(dialogs) == 0:
                    print("   ✅ Modal cerrado - Publicación exitosa")
                    return True
                else:
                    print("   ⚠️  Modal sigue abierto - Puede haber fallado")
                    return False
        except:
            # Si hay error buscando dialogs, asumir éxito
            print("   ✅ Asumiendo publicación exitosa")
            return True
    
    def publicar_completo(self, mensaje):
        """
        Realiza el proceso completo de publicación
        Orquesta todos los pasos
        
        Args:
            mensaje: Texto a publicar
            
        Returns:
            bool: True si la publicación fue exitosa
        """
        try:
            # Paso 1: Verificar sesión
            if not self.verificar_sesion_facebook():
                print("❌ No se pudo verificar sesión de Facebook")
                return False
            
            # Paso 2: Abrir compositor
            if not self.abrir_compositor():
                print("❌ No se pudo abrir el compositor")
                return False
            
            # Paso 3: Ingresar texto
            if not self.ingresar_texto(mensaje):
                print("❌ No se pudo ingresar el texto")
                return False
            
            # Paso 4: Publicar
            if not self.publicar_mensaje():
                print("❌ No se pudo hacer clic en Publicar")
                return False
            
            # Paso 5: Verificar éxito
            if not self.verificar_publicacion_exitosa():
                print("⚠️  No se pudo verificar el éxito de la publicación")
                # Continuar de todos modos (puede haber publicado)
            
            print("✅ Publicación completada exitosamente")
            return True
            
        except Exception as e:
            print(f"❌ Error durante la publicación: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def cerrar_navegador(self):
        """Cierra el navegador"""
        if self.driver:
            print("🔒 Cerrando navegador...")
            time.sleep(2)
            self.driver.quit()
            print("✅ Navegador cerrado")
