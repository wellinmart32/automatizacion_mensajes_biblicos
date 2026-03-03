import os
import sys
import time
import json
import random
import platform
import configparser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class PublicadorWhatsAppOracion:
    """Envía llamados de oración a grupos/chats de WhatsApp"""

    def __init__(self):
        self.driver = None

        # Determinar carpeta base según si es .exe compilado o script
        if getattr(sys, 'frozen', False):
            self.base_dir = os.path.dirname(sys.executable)
        else:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))
            # Si está en subcarpeta publicadores, subir un nivel
            if os.path.basename(self.base_dir) == 'publicadores':
                self.base_dir = os.path.dirname(self.base_dir)

        self.carpeta_oracion = os.path.join(self.base_dir, "llamados-oracion")
        self.archivo_mensajes = os.path.join(self.carpeta_oracion, "mensajes_oracion.txt")
        self.archivo_grupos = os.path.join(self.carpeta_oracion, "grupos.json")
        self.archivo_config = os.path.join(self.base_dir, "config_global.txt")

        # Tiempos de espera
        self.ESPERA_ENTRE_GRUPOS = 3
        self.ESPERA_MAX_CARGA_WHATSAPP = 90   # Máximo 90s esperando que cargue WhatsApp
        self.ESPERA_BUSQUEDA = 5

        self.mensajes_grupos = []
        self.mensajes_individuales = []

        # Cargar navegador desde config del módulo oraciones
        self.navegador = self._leer_navegador_config()

    def _leer_navegador_config(self):
        """Lee el navegador configurado para el módulo de oraciones"""
        try:
            config = configparser.ConfigParser()
            if os.path.exists(self.archivo_config):
                config.read(self.archivo_config, encoding='utf-8')
                # Primero busca config específica de oraciones
                if config.has_option('ORACIONES', 'navegador'):
                    nav = config['ORACIONES']['navegador'].split('#')[0].strip()
                    if nav in ['firefox', 'chrome']:
                        return nav
                # Fallback a navegador general
                if config.has_option('GENERAL', 'navegador'):
                    nav = config['GENERAL']['navegador'].split('#')[0].strip()
                    if nav in ['firefox', 'chrome']:
                        return nav
        except Exception as e:
            print(f"   ⚠️  Error leyendo config navegador: {e}")
        return 'firefox'  # Default
    
    def _leer_usar_perfil_config(self):
        """Lee si debe usar perfil existente desde config_global.txt"""
        try:
            config = configparser.ConfigParser()
            if os.path.exists(self.archivo_config):
                config.read(self.archivo_config, encoding='utf-8')
                if config.has_option('NAVEGADOR', 'usar_perfil_existente'):
                    val = config['NAVEGADOR']['usar_perfil_existente'].split('#')[0].strip().lower()
                    return val == 'si'
        except Exception as e:
            print(f"   ⚠️  Error leyendo config perfil: {e}")
        return True

    def cargar_mensajes(self):
        """Carga mensajes desde archivo separados por tipo"""
        if not os.path.exists(self.archivo_mensajes):
            raise Exception(f"No se encontró {self.archivo_mensajes}")

        with open(self.archivo_mensajes, 'r', encoding='utf-8') as f:
            contenido = f.read()

        if '[GRUPOS]' in contenido and '[INDIVIDUALES]' in contenido:
            partes = contenido.split('[INDIVIDUALES]')
            seccion_grupos = partes[0].replace('[GRUPOS]', '').strip()
            seccion_individuales = partes[1].strip()
            self.mensajes_grupos = [l.strip() for l in seccion_grupos.split('\n') if l.strip()]
            self.mensajes_individuales = [l.strip() for l in seccion_individuales.split('\n') if l.strip()]
        elif '[GRUPOS]' in contenido:
            seccion_grupos = contenido.replace('[GRUPOS]', '').strip()
            self.mensajes_grupos = [l.strip() for l in seccion_grupos.split('\n') if l.strip()]
            self.mensajes_individuales = self.mensajes_grupos
        else:
            self.mensajes_grupos = [l.strip() for l in contenido.split('\n') if l.strip()]
            self.mensajes_individuales = self.mensajes_grupos

        if not self.mensajes_grupos:
            raise Exception("No hay mensajes configurados en el archivo de oraciones")

        return True

    def cargar_grupos(self):
        """Carga lista de chats seleccionados por defecto en configurador"""
        if not os.path.exists(self.archivo_grupos):
            raise Exception(f"No se encontró {self.archivo_grupos}")

        with open(self.archivo_grupos, 'r', encoding='utf-8') as f:
            datos = json.load(f)

        chats = [g for g in datos.get('grupos', []) if g.get('seleccionado', True) and g.get('activo', True)]

        if not chats:
            raise Exception("No hay destinatarios seleccionados. Configura en Configurador → Oraciones → Seleccionar destinatarios por defecto.")

        return chats

    def seleccionar_mensaje(self, chat):
        """Selecciona mensaje para el chat — usa asignado si existe, aleatorio si no"""
        mensaje_asignado = chat.get('mensaje_asignado', None)
        if mensaje_asignado and mensaje_asignado.strip():
            return mensaje_asignado.strip()

        tipo_chat = chat.get('tipo', 'grupo')
        if tipo_chat == "grupo":
            return random.choice(self.mensajes_grupos)
        elif tipo_chat in ["individual", "contacto"]:
            return random.choice(self.mensajes_individuales)
        else:
            return random.choice(self.mensajes_grupos)

    def iniciar_navegador(self):
        """Inicia el navegador configurado según config_global.txt"""
        print(f"\n🌐 Iniciando {self.navegador.capitalize()} para WhatsApp Web...")

        try:
            usar_perfil = self._leer_usar_perfil_config()

            if self.navegador == 'chrome':
                opciones = ChromeOptions()
                opciones.add_argument("--disable-blink-features=AutomationControlled")
                opciones.add_experimental_option("excludeSwitches", ["enable-automation"])

                perfil_dedicado = os.path.join(self.base_dir, "perfiles", "whatsapp_oracion_chrome")
                os.makedirs(perfil_dedicado, exist_ok=True)
                opciones.add_argument(f"--user-data-dir={perfil_dedicado}")
                print(f"   ✓ Usando perfil Chrome dedicado: {perfil_dedicado}")

                self.driver = webdriver.Chrome(options=opciones)
            else:
                # Firefox (default)
                opciones = FirefoxOptions()
                if platform.system() == "Windows":
                    ruta_perfiles = os.path.expanduser("~/AppData/Roaming/Mozilla/Firefox/Profiles")
                else:
                    ruta_perfiles = os.path.expanduser("~/.mozilla/firefox")

                perfil_path = None
                if os.path.exists(ruta_perfiles):
                    for carpeta in os.listdir(ruta_perfiles):
                        if 'default-release' in carpeta:
                            perfil_path = os.path.join(ruta_perfiles, carpeta)
                            print(f"   ✓ Usando perfil Firefox: {carpeta}")
                            break

                if perfil_path:
                    opciones.add_argument('-profile')
                    opciones.add_argument(perfil_path)
                else:
                    print("   ⚠️  No se encontró perfil default-release")

                self.driver = webdriver.Firefox(options=opciones)

            self.driver.maximize_window()
            print("   ✅ Navegador iniciado")
            return True

        except Exception as e:
            print(f"   ❌ Error iniciando navegador: {e}")
            return False

    def abrir_whatsapp_web(self):
        """Abre WhatsApp Web y espera a que cargue completamente"""
        print("\n📱 Abriendo WhatsApp Web...")

        try:
            self.driver.get("https://web.whatsapp.com")

            print(f"   ⏳ Esperando que WhatsApp cargue (máximo {self.ESPERA_MAX_CARGA_WHATSAPP}s)...")
            print("   ℹ️  Si es la primera vez, puede tardar mientras sincroniza con tu móvil...")

            # Esperar hasta que aparezca el campo de búsqueda de chats
            # Esto confirma que WhatsApp cargó completamente y está listo
            inicio = time.time()
            cargado = False

            while (time.time() - inicio) < self.ESPERA_MAX_CARGA_WHATSAPP:
                try:
                    # Verificar si ya cargó la interfaz principal (campo de búsqueda visible)
                    WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located(
                            (By.XPATH, "//div[@contenteditable='true'][@data-tab='3']")
                        )
                    )
                    cargado = True
                    break
                except TimeoutException:
                    segundos_esperados = int(time.time() - inicio)
                    print(f"   ⏳ Esperando interfaz... {segundos_esperados}s", end='\r')
                    time.sleep(3)

            if cargado:
                print(f"\n   ✅ WhatsApp Web cargado correctamente")
                time.sleep(2)  # Pequeña pausa adicional para estabilizar
                return True
            else:
                print(f"\n   ❌ WhatsApp no cargó en {self.ESPERA_MAX_CARGA_WHATSAPP}s")
                print("   💡 Verifica que tu móvil esté conectado y sincronizado")
                return False

        except Exception as e:
            print(f"   ❌ Error abriendo WhatsApp Web: {e}")
            return False

    def buscar_chat(self, nombre_chat):
        """Busca chat por nombre"""
        print(f"\n🔍 Buscando chat: {nombre_chat}")
        try:
            from selenium.webdriver.common.action_chains import ActionChains

            # Cerrar chat abierto volviendo al panel lateral
            try:
                ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
                time.sleep(0.5)
            except:
                pass

            # Clic en el panel lateral para asegurar foco correcto
            try:
                panel = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//div[@id='pane-side']")
                    )
                )
                panel.click()
                time.sleep(0.5)
            except:
                pass

            campo_busqueda = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[@contenteditable='true'][@data-tab='3']")
                )
            )
            campo_busqueda.click()
            time.sleep(0.8)

            # Limpiar campo con JavaScript + disparo de evento
            self.driver.execute_script("""
                var el = arguments[0];
                el.focus();
                el.innerHTML = '';
                el.dispatchEvent(new Event('input', {bubbles: true}));
                el.dispatchEvent(new InputEvent('input', {bubbles: true}));
            """, campo_busqueda)
            time.sleep(0.5)

            import pyperclip
            pyperclip.copy(nombre_chat)
            ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
            time.sleep(2.5)

            try:
                contacto = WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, f"//span[@title='{nombre_chat}']"))
                )
                contacto.click()
                time.sleep(2)
                print(f"   ✅ Chat '{nombre_chat}' abierto")
                return True
            except:
                try:
                    contacto_alt = WebDriverWait(self.driver, 8).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, f"//span[contains(@title, '{nombre_chat}')]")
                        )
                    )
                    contacto_alt.click()
                    time.sleep(2)
                    print(f"   ✅ Chat '{nombre_chat}' abierto")
                    return True
                except:
                    print(f"   ❌ No se encontró '{nombre_chat}'")
                    return False

        except Exception as e:
            print(f"   ❌ Error buscando chat: {e}")
            return False

    def enviar_mensaje(self, mensaje):
        """Envía mensaje en chat activo"""
        print(f"\n✉️  Enviando mensaje...")
        try:
            from selenium.webdriver.common.action_chains import ActionChains
            time.sleep(1.5)

            campo_mensaje = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//div[@contenteditable='true'][@data-tab='10']")
                )
            )

            self.driver.execute_script("arguments[0].focus();", campo_mensaje)
            time.sleep(0.5)
            campo_mensaje.click()
            time.sleep(0.5)

            import pyperclip
            pyperclip.copy(mensaje)
            time.sleep(0.3)
            ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
            time.sleep(1.0)

            contenido = self.driver.execute_script(
                "return arguments[0].innerText || '';", campo_mensaje)
            if not contenido.strip():
                print("   ⚠️  Campo vacío, reintentando...")
                campo_mensaje.click()
                time.sleep(0.5)
                ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
                time.sleep(1.0)

            ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            time.sleep(2)

            print(f"   ✅ Mensaje enviado: {mensaje[:50]}...")
            return True

        except Exception as e:
            print(f"   ❌ Error enviando mensaje: {e}")
            import traceback
            traceback.print_exc()
            return False

    def publicar_en_todos_los_chats(self):
        """Función principal - publica en todos los chats"""
        print("\n" + "="*70)
        print(" " * 15 + "📱 PUBLICADOR DE LLAMADOS DE ORACIÓN")
        print(" " * 20 + "WhatsApp Web - Chats")
        print("="*70 + "\n")

        print(f"🌐 Navegador configurado: {self.navegador.capitalize()}")

        try:
            self.cargar_mensajes()
            chats = self.cargar_grupos()
        except Exception as e:
            print(f"❌ Error cargando archivos: {e}")
            return False

        grupos_count = sum(1 for c in chats if c.get('tipo') == 'grupo')
        individuales_count = sum(1 for c in chats if c.get('tipo') == 'individual')

        print(f"\n📋 CONFIGURACIÓN:")
        print(f"   📝 Mensajes para grupos: {len(self.mensajes_grupos)}")
        print(f"   📝 Mensajes para individuales: {len(self.mensajes_individuales)}")
        print(f"   👥 Grupos activos: {grupos_count}")
        print(f"   👤 Individuales activos: {individuales_count}")
        print(f"   📈 Total chats: {len(chats)}")

        print(f"\n📋 CHATS A PUBLICAR:")
        for i, chat in enumerate(chats, 1):
            tipo_emoji = "👥" if chat.get('tipo') == 'grupo' else "👤"
            print(f"   {i}. {tipo_emoji} {chat['nombre']} ({chat.get('tipo', 'grupo')})")

        if not self.iniciar_navegador():
            return False

        if not self.abrir_whatsapp_web():
            self.cerrar_navegador()
            return False

        exitos = 0
        fallos = 0

        print("\n" + "="*70)
        print("▶ INICIANDO PUBLICACIONES")
        print("="*70)

        for i, chat in enumerate(chats, 1):
            nombre_chat = chat['nombre']
            tipo_chat = chat.get('tipo', 'grupo')
            tipo_emoji = "👥" if tipo_chat == 'grupo' else "👤"

            print(f"\n{'='*70}")
            print(f"📨 CHAT {i}/{len(chats)}: {tipo_emoji} {nombre_chat} ({tipo_chat})")
            print(f"{'='*70}")

            mensaje = self.seleccionar_mensaje(chat)
            print(f"🎲 Mensaje seleccionado: '{mensaje}'")

            if not self.buscar_chat(nombre_chat):
                print(f"   ⚠️  Saltando chat '{nombre_chat}'")
                fallos += 1
                continue

            if self.enviar_mensaje(mensaje):
                exitos += 1
                print(f"   ✅ Publicación exitosa en '{nombre_chat}'")
            else:
                fallos += 1
                print(f"   ❌ Fallo en '{nombre_chat}'")

            if i < len(chats):
                print(f"\n   ⏳ Esperando {self.ESPERA_ENTRE_GRUPOS}s antes del siguiente chat...")
                time.sleep(self.ESPERA_ENTRE_GRUPOS)

        print("\n" + "="*70)
        print("📈 RESUMEN DE PUBLICACIONES")
        print("="*70)
        print(f"   ✅ Exitosas: {exitos}")
        print(f"   ❌ Fallidas: {fallos}")
        print(f"   📈 Total chats: {len(chats)}")
        if len(chats) > 0:
            print(f"   🎯 Tasa de éxito: {(exitos/len(chats)*100):.1f}%")
        print("="*70)

        self.cerrar_navegador()
        return exitos > 0

    def cerrar_navegador(self):
        """Cierra navegador"""
        if self.driver:
            print("\n🔒 Cerrando navegador...")
            try:
                self.driver.quit()
                print("   ✅ Navegador cerrado")
            except:
                pass


def main():
    """Función principal"""
    publicador = PublicadorWhatsAppOracion()

    try:
        exito = publicador.publicar_en_todos_los_chats()

        if exito:
            print("\n✅ Proceso completado exitosamente")
        else:
            print("\n⚠️  Proceso completado con errores")

    except KeyboardInterrupt:
        print("\n\n❌ Proceso cancelado por el usuario")
        publicador.cerrar_navegador()

    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        publicador.cerrar_navegador()

    finally:
        print("\n👋 Finalizando programa...")
        time.sleep(2)


if __name__ == "__main__":
    main()