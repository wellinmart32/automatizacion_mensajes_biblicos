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
    """Automatización de publicaciones en Facebook"""
    
    def __init__(self, config):
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
        
        self.wait = WebDriverWait(self.driver, 20)
        
        if self.config['maximizar_ventana']:
            self.driver.maximize_window()
        
        print("✅ Navegador iniciado correctamente")
    
    def _iniciar_firefox(self):
        """Inicia Firefox con perfil configurado"""
        opciones = FirefoxOptions()
        
        if self.config['desactivar_notificaciones']:
            opciones.set_preference("dom.webnotifications.enabled", False)
        
        from compartido.gestor_archivos import obtener_ruta_perfil_navegador
        ruta_perfil = obtener_ruta_perfil_navegador()
        
        if ruta_perfil:
            opciones.add_argument("-profile")
            opciones.add_argument(ruta_perfil)
        
        self.driver = webdriver.Firefox(options=opciones)
    
    def _iniciar_chrome(self):
        """Inicia Chrome con perfil configurado"""
        import platform as _platform
        opciones = ChromeOptions()

        if self.config['desactivar_notificaciones']:
            opciones.add_argument("--disable-notifications")

        opciones.add_argument("--disable-blink-features=AutomationControlled")
        opciones.add_experimental_option("excludeSwitches", ["enable-automation"])
        opciones.add_experimental_option('useAutomationExtension', False)

        usar_perfil = self.config.get('usar_perfil_existente', True)

        # Siempre usar perfil dedicado para evitar conflictos con Chrome abierto
        import platform as _platform
        if usar_perfil:
            if _platform.system() == "Windows":
                base = os.path.expanduser("~/AppData/Local/Google/Chrome/User Data")
            else:
                base = os.path.expanduser("~/.config/google-chrome")
            perfil_dedicado = os.path.join(os.path.dirname(os.path.abspath(self.config.get('carpeta_perfil_custom', 'perfiles/facebook_publicador'))), "chrome_mensajes")
        else:
            perfil_dedicado = os.path.abspath(self.config.get('carpeta_perfil_custom', 'perfiles/facebook_publicador'))

        os.makedirs(perfil_dedicado, exist_ok=True)
        opciones.add_argument(f"--user-data-dir={perfil_dedicado}")
        opciones.add_argument("--no-first-run")
        opciones.add_argument("--no-default-browser-check")

        self.driver = webdriver.Chrome(options=opciones)
    
    def verificar_sesion_facebook(self):
        """Verifica si hay sesión activa en Facebook, espera si necesita login"""
        print("🔐 Verificando sesión de Facebook...")
        
        try:
            self.driver.get("https://www.facebook.com")
            time.sleep(3)
            
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
        """Abre el cuadro de publicación - SELECTOR EXACTO DEL HTML DE WELLINGTON"""
        print("📝 Abriendo compositor de publicación...")
        
        # CRÍTICO: Verificar que estamos en Facebook
        url_actual = self.driver.current_url
        
        if "facebook.com" not in url_actual:
            print("   ⚠️  No estás en Facebook. Navegando...")
            self.driver.get("https://www.facebook.com")
            time.sleep(5)
        elif "stories" in url_actual or "watch" in url_actual or "?sk=" in url_actual:
            print("   Navegando a página principal...")
            self.driver.get("https://www.facebook.com")
            time.sleep(5)
        
        # ESTRATEGIA 1: Selector exacto del HTML
        print("   Estrategia 1: Selector exacto del HTML...")
        
        try:
            selector_exacto = "//div[@role='button']//span[@class='x1lliihq x6ikm8r x10wlt62 x1n2onr6' and contains(text(), 'pensando')]"
            
            botones = self.driver.find_elements(By.XPATH, selector_exacto)
            
            if botones:
                for boton_span in botones:
                    try:
                        boton = boton_span.find_element(By.XPATH, "./ancestor::div[@role='button']")
                        
                        if boton.is_displayed():
                            print(f"   ✅ Botón encontrado: {boton_span.text[:50]}")
                            
                            self.driver.execute_script(
                                "arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", 
                                boton
                            )
                            time.sleep(1.5)
                            
                            self.driver.execute_script("arguments[0].click();", boton)
                            time.sleep(3)
                            
                            dialogs = self.driver.find_elements(By.XPATH, "//div[@role='dialog']")
                            if dialogs and len(dialogs) > 0 and dialogs[0].is_displayed():
                                print("   ✅ Modal confirmado - Estrategia 1")
                                
                                tiempo_espera = self.config.get('espera_estabilizacion_modal', 3)
                                print(f"   ⏳ Esperando {tiempo_espera}s...")
                                time.sleep(tiempo_espera)
                                
                                try:
                                    WebDriverWait(self.driver, 10).until(
                                        EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']//div[@contenteditable='true']"))
                                    )
                                    print("   ✅ Área de texto lista")
                                    return True
                                except:
                                    print("   ✅ Modal confirmado")
                                    return True
                    except:
                        continue
        except Exception as e:
            print(f"   ⚠️  Error estrategia 1: {e}")
        
        # ESTRATEGIA 2: Buscar contenedor principal
        print("   Estrategia 2: Contenedor 'Crear una publicación'...")
        
        try:
            contenedor = self.driver.find_element(By.XPATH, 
                "//div[@role='region' and @aria-label='Crear una publicación']")
            
            if contenedor:
                try:
                    boton = contenedor.find_element(By.XPATH, 
                        ".//div[@role='button' and contains(., 'pensando')]")
                    
                    if boton.is_displayed():
                        self.driver.execute_script(
                            "arguments[0].scrollIntoView({block: 'center'});", 
                            boton
                        )
                        time.sleep(1.5)
                        self.driver.execute_script("arguments[0].click();", boton)
                        time.sleep(3)
                        
                        dialogs = self.driver.find_elements(By.XPATH, "//div[@role='dialog']")
                        if dialogs and dialogs[0].is_displayed():
                            print("   ✅ Modal abierto - Estrategia 2")
                            time.sleep(self.config.get('espera_estabilizacion_modal', 3))
                            return True
                except:
                    pass
        except:
            pass
        
        # ESTRATEGIA 3: Buscar span directamente
        print("   Estrategia 3: Buscando span directamente...")
        
        selectores_span = [
            "//span[contains(text(), '¿Qué estás pensando, Wellington?')]",
            "//span[contains(text(), 'pensando, Wellington')]",
            "//span[contains(text(), '¿Qué estás pensando')]"
        ]
        
        for selector in selectores_span:
            try:
                spans = self.driver.find_elements(By.XPATH, selector)
                
                for span in spans:
                    try:
                        if not span.is_displayed():
                            continue
                        
                        boton = span.find_element(By.XPATH, "./ancestor::div[@role='button']")
                        
                        self.driver.execute_script(
                            "arguments[0].scrollIntoView({block: 'center'});", 
                            boton
                        )
                        time.sleep(1)
                        self.driver.execute_script("arguments[0].click();", boton)
                        time.sleep(3)
                        
                        dialogs = self.driver.find_elements(By.XPATH, "//div[@role='dialog']")
                        if dialogs and dialogs[0].is_displayed():
                            print("   ✅ Modal abierto - Estrategia 3")
                            time.sleep(self.config.get('espera_estabilizacion_modal', 3))
                            return True
                    except:
                        continue
            except:
                continue
        
        # ESTRATEGIA 4: Buscar todos los botones y filtrar
        print("   Estrategia 4: Buscando entre todos los botones...")
        
        try:
            todos_botones = self.driver.find_elements(By.XPATH, "//div[@role='button']")
            
            for boton in todos_botones[:30]:
                try:
                    if not boton.is_displayed():
                        continue
                    
                    texto = boton.text.strip().lower()
                    
                    if 'pensando' in texto and len(texto) < 100:
                        self.driver.execute_script(
                            "arguments[0].scrollIntoView({block: 'center'});", 
                            boton
                        )
                        time.sleep(1)
                        self.driver.execute_script("arguments[0].click();", boton)
                        time.sleep(3)
                        
                        dialogs = self.driver.find_elements(By.XPATH, "//div[@role='dialog']")
                        if dialogs:
                            print("   ✅ Modal abierto - Estrategia 4")
                            time.sleep(self.config.get('espera_estabilizacion_modal', 3))
                            return True
                except:
                    continue
        except:
            pass
        
        # ESTRATEGIA 5: Scroll al inicio y buscar
        print("   Estrategia 5: Scroll al inicio...")
        
        try:
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(2)
            
            spans = self.driver.find_elements(By.XPATH, 
                "//span[contains(text(), 'pensando')]")
            
            for span in spans:
                try:
                    if span.is_displayed():
                        boton = span.find_element(By.XPATH, "./ancestor::div[@role='button']")
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", boton)
                        time.sleep(1)
                        self.driver.execute_script("arguments[0].click();", boton)
                        time.sleep(3)
                        
                        dialogs = self.driver.find_elements(By.XPATH, "//div[@role='dialog']")
                        if dialogs:
                            print("   ✅ Modal abierto - Estrategia 5")
                            time.sleep(self.config.get('espera_estabilizacion_modal', 3))
                            return True
                except:
                    continue
        except:
            pass
        
        # ESTRATEGIA 6: Atajo de teclado 'p'
        print("   Estrategia 6: Atajo 'p'...")
        
        try:
            body = self.driver.find_element(By.TAG_NAME, "body")
            body.click()
            time.sleep(1)
            ActionChains(self.driver).send_keys('p').perform()
            time.sleep(3)
            
            dialogs = self.driver.find_elements(By.XPATH, "//div[@role='dialog']")
            if dialogs:
                print("   ✅ Modal abierto - Atajo 'p'")
                time.sleep(self.config.get('espera_estabilizacion_modal', 3))
                return True
        except:
            pass
        
        print("\n   ❌ No se pudo abrir el compositor")
        print("   💡 Intenta: cerrar navegador y ejecutar de nuevo\n")
        return False
    
    def ingresar_texto(self, mensaje):
        """Ingresa el texto en el compositor - Usa portapapeles y fallbacks"""
        print("✍️  Ingresando texto...")
        
        area_texto = self._buscar_area_texto()
        
        if not area_texto:
            print("   ❌ No se encontró área de texto")
            return False
        
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", area_texto)
            time.sleep(0.5)
            self.driver.execute_script("arguments[0].click();", area_texto)
            time.sleep(1)
            self.driver.execute_script("arguments[0].focus();", area_texto)
            time.sleep(1)
        except Exception as e:
            print(f"   ⚠️  Error dando foco: {e}")
        
        # MÉTODO 1: Portapapeles
        print("   Método: Portapapeles...")
        try:
            pyperclip.copy(mensaje)
            ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
            time.sleep(2)
            
            texto_actual = area_texto.text
            if len(texto_actual) >= 10:
                print(f"   ✅ Texto ingresado ({len(texto_actual)} caracteres)")
                return True
        except Exception as e:
            print(f"   ⚠️  Error portapapeles: {e}")
        
        # MÉTODO 2: send_keys
        print("   Método: send_keys...")
        try:
            area_texto.clear()
            time.sleep(0.5)
            area_texto.send_keys(mensaje)
            time.sleep(2)
            
            texto_actual = area_texto.text
            if len(texto_actual) >= 10:
                print(f"   ✅ Texto ingresado ({len(texto_actual)} caracteres)")
                return True
        except Exception as e:
            print(f"   ⚠️  Error send_keys: {e}")
        
        # MÉTODO 3: JavaScript
        print("   Método: JavaScript...")
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
            print(f"   ❌ Error JavaScript: {e}")
            return False
    
    def _buscar_area_texto(self):
        """Busca el área de texto del compositor"""
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
                
                for elemento in elementos:
                    try:
                        if elemento.is_displayed():
                            size = elemento.size
                            if size['height'] > 50:
                                return elemento
                    except:
                        continue
            except:
                continue
        
        try:
            dialog = self.driver.find_element(By.XPATH, "//div[@role='dialog']")
            area_texto = dialog.find_element(By.XPATH, ".//div[@contenteditable='true']")
            return area_texto
        except:
            pass
        
        return None
    
    def publicar_mensaje(self):
        """Hace clic en botón Publicar"""
        print("🚀 Buscando botón 'Publicar'...")
        
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
                                self.driver.execute_script(
                                    "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", 
                                    elemento
                                )
                                time.sleep(1)
                                
                                self.driver.execute_script("arguments[0].click();", elemento)
                                boton_encontrado = True
                                print(f"   ✅ Clic en 'Publicar'")
                                break
                        except:
                            continue
                    if boton_encontrado:
                        break
            except:
                continue
        
        if not boton_encontrado:
            print("   Buscando por texto...")
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
                print(f"   ⚠️  Error: {e}")
        
        if not boton_encontrado:
            try:
                dialog = self.driver.find_element(By.XPATH, "//div[@role='dialog']")
                boton = dialog.find_element(By.XPATH, ".//div[@role='button' and contains(., 'Publicar')]")
                self.driver.execute_script("arguments[0].click();", boton)
                boton_encontrado = True
                print("   ✅ Botón encontrado en dialog")
            except:
                pass
        
        if not boton_encontrado:
            print("   ❌ No se encontró botón 'Publicar'")
            return False
        
        tiempo_espera = self.config['espera_despues_publicar']
        print(f"   ⏳ Esperando {tiempo_espera}s...")
        time.sleep(tiempo_espera)
        
        return True
    
    def verificar_publicacion_exitosa(self):
        """Verifica que la publicación fue exitosa (modal cerrado)"""
        if not self.config['verificar_publicacion_exitosa']:
            return True
        
        print("🔍 Verificando publicación...")
        
        try:
            dialogs = self.driver.find_elements(By.XPATH, "//div[@role='dialog']")
            
            if len(dialogs) == 0:
                print("   ✅ Modal cerrado - Publicación exitosa")
                return True
            else:
                time.sleep(3)
                
                dialogs = self.driver.find_elements(By.XPATH, "//div[@role='dialog']")
                if len(dialogs) == 0:
                    print("   ✅ Modal cerrado - Publicación exitosa")
                    return True
                else:
                    print("   ⚠️  Modal sigue abierto")
                    return False
        except:
            print("   ✅ Asumiendo publicación exitosa")
            return True
    
    
    def publicar_enlace_con_preview_optimizado(self, enlace, texto_introduccion="", hashtags=""):
        """
        Publica un enlace con previsualización optimizada
        NUEVA ESTRATEGIA: Escribir introducción → Pegar enlace → Esperar preview
        """
        print("\n🔗 MODO OPTIMIZADO: Publicación de enlace con previsualización")
        
        # Buscar área de texto
        area_texto = self._buscar_area_texto()
        if not area_texto:
            print("   ❌ No se encontró área de texto")
            return False
        
        try:
            # Dar foco al área
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", area_texto)
            time.sleep(0.5)
            self.driver.execute_script("arguments[0].click();", area_texto)
            time.sleep(1)
            self.driver.execute_script("arguments[0].focus();", area_texto)
            time.sleep(1)
            
            # Limpiar contenido previo
            area_texto.send_keys(Keys.CONTROL + "a")
            time.sleep(0.3)
            area_texto.send_keys(Keys.DELETE)
            time.sleep(0.5)
            
        except Exception as e:
            print(f"   ⚠️  Error dando foco: {e}")
        
        # FASE 1: Escribir introducción PRIMERO (si existe)
        if texto_introduccion:
            print("📝 FASE 1: Escribiendo introducción...")
            print(f"   {texto_introduccion}")
            
            try:
                # Escribir introducción letra por letra (más confiable)
                for caracter in texto_introduccion:
                    area_texto.send_keys(caracter)
                    time.sleep(0.02)
                
                # Agregar 2 saltos de línea
                area_texto.send_keys(Keys.RETURN)
                time.sleep(0.2)
                area_texto.send_keys(Keys.RETURN)
                time.sleep(0.3)
                
                print("   ✅ Introducción escrita")
                
            except Exception as e:
                print(f"   ⚠️  Error escribiendo introducción: {e}")
        
        # FASE 2: Pegar enlace
        print("\n📎 FASE 2: Pegando enlace...")
        print(f"   {enlace[:70]}...")
        
        try:
            # Pegar enlace usando portapapeles
            pyperclip.copy(enlace)
            time.sleep(0.5)
            
            ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
            time.sleep(2)
            
            print("   ✅ Enlace pegado")
            
        except Exception as e:
            print(f"   ❌ Error pegando enlace: {e}")
            return False
        
        # FASE 3: Esperar previsualización
        tiempo_espera = self.config.get('tiempo_espera_previsualizacion', 12)
        print(f"\n⏳ FASE 3: Esperando previsualización ({tiempo_espera}s)...")
        print("   Facebook está generando la miniatura del video...")
        
        for i in range(tiempo_espera, 0, -1):
            if i % 2 == 0:
                print(f"   Esperando... {i}s restantes", end='\r', flush=True)
            time.sleep(1)
        
        print("\n   ✅ Previsualización lista")
        
        # FASE 4: Agregar hashtags al final (si existen)
        if hashtags:
            print("\n📝 FASE 4: Agregando hashtags...")
            
            try:
                time.sleep(1)
                area_texto = self._buscar_area_texto()
                
                if area_texto:
                    # Ir al final del texto
                    ActionChains(self.driver).key_down(Keys.CONTROL).send_keys(Keys.END).key_up(Keys.CONTROL).perform()
                    time.sleep(0.5)
                    
                    # Agregar saltos de línea y hashtags
                    area_texto.send_keys(Keys.RETURN)
                    time.sleep(0.2)
                    area_texto.send_keys(Keys.RETURN)
                    time.sleep(0.2)
                    
                    # Escribir hashtags letra por letra
                    for caracter in hashtags.strip():
                        area_texto.send_keys(caracter)
                        time.sleep(0.05)
                        
                        # Si es #, cerrar menú de sugerencias
                        if caracter == '#':
                            time.sleep(0.3)
                            area_texto.send_keys(Keys.ESCAPE)
                            time.sleep(0.2)
                    
                    print("   ✅ Hashtags agregados")
            
            except Exception as e:
                print(f"   ⚠️  Error agregando hashtags: {e}")
        
        # FASE 5: Publicar
        print("\n🚀 Publicando...")
        
        if not self.publicar_mensaje():
            print("❌ Error al publicar")
            return False
        
        if not self.verificar_publicacion_exitosa():
            print("⚠️  No se pudo verificar publicación")
        
        print("✅ Publicación completada con previsualización")
        return True
    
    def publicar_completo(self, mensaje):
        """Realiza el proceso completo de publicación"""
        try:
            # Verificar sesión (esto navega a Facebook)
            if not self.verificar_sesion_facebook():
                print("❌ No se pudo verificar sesión")
                return False
            
            # Ahora ya estamos en Facebook, abrir compositor
            if not self.abrir_compositor():
                print("❌ No se pudo abrir compositor")
                return False
            
            if not self.ingresar_texto(mensaje):
                print("❌ No se pudo ingresar texto")
                return False
            
            if not self.publicar_mensaje():
                print("❌ No se pudo publicar")
                return False
            
            if not self.verificar_publicacion_exitosa():
                print("⚠️  No se pudo verificar éxito")
            
            print("✅ Publicación completada")
            return True
            
        except Exception as e:
            print(f"❌ Error durante publicación: {e}")
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
