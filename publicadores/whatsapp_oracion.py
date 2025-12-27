import os
import sys
import time
import json
import random
import platform
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class PublicadorWhatsAppOracion:
    """Envía llamados de oración a grupos/chats de WhatsApp"""
    
    def __init__(self):
        self.driver = None
        self.carpeta_oracion = "llamados-oracion"
        self.archivo_mensajes = os.path.join(self.carpeta_oracion, "mensajes_oracion.txt")
        self.archivo_grupos = os.path.join(self.carpeta_oracion, "grupos.json")
        
        self.ESPERA_ENTRE_GRUPOS = 3
        self.ESPERA_CARGA_WHATSAPP = 15
        self.ESPERA_BUSQUEDA = 5
        
        self.mensajes_grupos = []
        self.mensajes_individuales = []
    
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
            
            self.mensajes_grupos = [linea.strip() for linea in seccion_grupos.split('\n') if linea.strip()]
            self.mensajes_individuales = [linea.strip() for linea in seccion_individuales.split('\n') if linea.strip()]
        else:
            raise Exception("El archivo debe tener las secciones [GRUPOS] e [INDIVIDUALES]")
        
        if not self.mensajes_grupos or not self.mensajes_individuales:
            raise Exception("Debe haber al menos un mensaje en cada sección")
        
        return True
    
    def cargar_grupos(self):
        """Carga lista de chats desde JSON"""
        if not os.path.exists(self.archivo_grupos):
            raise Exception(f"No se encontró {self.archivo_grupos}")
        
        with open(self.archivo_grupos, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        
        chats_activos = [g for g in datos.get('grupos', []) if g.get('activo', False)]
        
        if not chats_activos:
            raise Exception("No hay chats activos en grupos.json")
        
        return chats_activos
    
    def seleccionar_mensaje_aleatorio(self, tipo_chat):
        """Selecciona mensaje aleatorio según tipo de chat"""
        if tipo_chat == "grupo":
            return random.choice(self.mensajes_grupos)
        elif tipo_chat == "individual":
            return random.choice(self.mensajes_individuales)
        else:
            return random.choice(self.mensajes_grupos)
    
    def iniciar_navegador(self):
        """Inicia Firefox con perfil existente"""
        print("\n🌐 Iniciando Firefox para WhatsApp Web...")
        
        try:
            opciones = FirefoxOptions()
            
            # Detectar perfil de Firefox
            if platform.system() == "Windows":
                ruta_perfiles = os.path.expanduser("~/AppData/Roaming/Mozilla/Firefox/Profiles")
            else:
                ruta_perfiles = os.path.expanduser("~/.mozilla/firefox")
            
            # Buscar perfil default-release
            perfil_path = None
            if os.path.exists(ruta_perfiles):
                for carpeta in os.listdir(ruta_perfiles):
                    if 'default-release' in carpeta:
                        perfil_path = os.path.join(ruta_perfiles, carpeta)
                        print(f"   🦊 Usando perfil Firefox: {carpeta}")
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
        """Abre WhatsApp Web y espera carga"""
        print("\n📱 Abriendo WhatsApp Web...")
        
        try:
            self.driver.get("https://web.whatsapp.com")
            
            print(f"   ⏳ Esperando {self.ESPERA_CARGA_WHATSAPP}s a que cargue...")
            time.sleep(self.ESPERA_CARGA_WHATSAPP)
            
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@data-tab='3']"))
                )
                print("   ✅ WhatsApp Web cargado")
                return True
            except TimeoutException:
                print("   ⚠️  No se detectó campo de búsqueda, continuando...")
                return True
                
        except Exception as e:
            print(f"   ❌ Error abriendo WhatsApp Web: {e}")
            return False
    
    def buscar_chat(self, nombre_chat):
        """Busca chat por nombre - ESCRIBE LETRA POR LETRA"""
        print(f"\n🔍 Buscando chat: {nombre_chat}")
        
        try:
            # MISMO XPATH DEL MARKETPLACE: data-tab='3'
            campo_busqueda = self.driver.find_element(By.XPATH, "//div[@contenteditable='true'][@data-tab='3']")
            campo_busqueda.click()
            time.sleep(1)
            
            campo_busqueda.clear()
            time.sleep(0.5)
            
            # ESCRIBIR LETRA POR LETRA (método publicador_facebook)
            for caracter in nombre_chat:
                campo_busqueda.send_keys(caracter)
                time.sleep(0.05)  # 50ms entre letras
            
            time.sleep(2)  # Esperar que filtre resultados
            
            # Buscar resultado - IGUAL AL MARKETPLACE
            try:
                contacto = WebDriverWait(self.driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, f"//span[@title='{nombre_chat}']"))
                )
                contacto.click()
                time.sleep(3)
                print(f"   ✅ Chat '{nombre_chat}' abierto")
                return True
            except:
                contacto_alt = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, f"//span[contains(text(), '{nombre_chat}')]"))
                )
                contacto_alt.click()
                time.sleep(3)
                print(f"   ✅ Chat '{nombre_chat}' abierto")
                return True
                
        except Exception as e:
            print(f"   ❌ Error buscando chat: {e}")
            return False
    
    def enviar_mensaje(self, mensaje):
        """Envía mensaje en chat activo - ESCRIBE LETRA POR LETRA"""
        print(f"\n✍️  Enviando mensaje...")
        
        try:
            time.sleep(2)
            
            # Buscar campo de mensaje
            campo_mensaje = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@data-tab='10']"))
            )
            
            campo_mensaje.click()
            time.sleep(0.5)
            
            # ESCRIBIR LETRA POR LETRA (método publicador_facebook)
            for caracter in mensaje:
                campo_mensaje.send_keys(caracter)
                time.sleep(0.05)  # 50ms entre letras
            
            time.sleep(0.5)
            
            campo_mensaje.send_keys(Keys.ENTER)
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
        
        try:
            self.cargar_mensajes()
            chats = self.cargar_grupos()
        except Exception as e:
            print(f"❌ Error cargando archivos: {e}")
            return False
        
        grupos_count = sum(1 for c in chats if c.get('tipo') == 'grupo')
        individuales_count = sum(1 for c in chats if c.get('tipo') == 'individual')
        
        print(f"📋 CONFIGURACIÓN:")
        print(f"   📝 Mensajes para grupos: {len(self.mensajes_grupos)}")
        print(f"   📝 Mensajes para individuales: {len(self.mensajes_individuales)}")
        print(f"   👥 Grupos activos: {grupos_count}")
        print(f"   👤 Individuales activos: {individuales_count}")
        print(f"   📊 Total chats: {len(chats)}")
        
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
        print("🚀 INICIANDO PUBLICACIONES")
        print("="*70)
        
        for i, chat in enumerate(chats, 1):
            nombre_chat = chat['nombre']
            tipo_chat = chat.get('tipo', 'grupo')
            tipo_emoji = "👥" if tipo_chat == 'grupo' else "👤"
            
            print(f"\n{'='*70}")
            print(f"📤 CHAT {i}/{len(chats)}: {tipo_emoji} {nombre_chat} ({tipo_chat})")
            print(f"{'='*70}")
            
            mensaje = self.seleccionar_mensaje_aleatorio(tipo_chat)
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
        print("📊 RESUMEN DE PUBLICACIONES")
        print("="*70)
        print(f"   ✅ Exitosas: {exitos}")
        print(f"   ❌ Fallidas: {fallos}")
        print(f"   📊 Total chats: {len(chats)}")
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
        input("\nPresiona Enter para salir...")


if __name__ == "__main__":
    main()
