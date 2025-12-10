from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
import time
import os
import requests
from datetime import datetime


class ExtractorWhatsAppPredicaciones:
    """
    Extrae predicaciones (enlaces e imágenes) del grupo de WhatsApp
    Similar a ExtractorWhatsApp de Marketplace pero adaptado para predicaciones
    """
    
    def __init__(self):
        self.driver = None
        self.wait = None
        self.carpeta_pendientes = "cola-facebook/pendientes"
        self.carpeta_publicados = "cola-facebook/publicados"
    
    def iniciar_navegador(self):
        """Inicia Firefox con perfil existente"""
        print("🌐 Iniciando Firefox para WhatsApp Web...")
        
        opciones = Options()
        opciones.set_preference("dom.webnotifications.enabled", False)
        
        # Usar primer perfil de Firefox disponible
        ruta_perfil = self._obtener_primer_perfil_firefox()
        if ruta_perfil:
            opciones.add_argument("-profile")
            opciones.add_argument(ruta_perfil)
        
        self.driver = webdriver.Firefox(options=opciones)
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 60)
        
        print("✅ Navegador iniciado")
        print("📱 Abriendo WhatsApp Web...")
        self.driver.get("https://web.whatsapp.com")
        time.sleep(3)
    
    def _obtener_primer_perfil_firefox(self):
        """Encuentra el primer perfil de Firefox disponible"""
        ruta_perfiles = os.path.expanduser("~\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles")
        
        if not os.path.exists(ruta_perfiles):
            return None
        
        perfiles = [f for f in os.listdir(ruta_perfiles) 
                   if os.path.isdir(os.path.join(ruta_perfiles, f))]
        
        if not perfiles:
            return None
        
        perfil = os.path.join(ruta_perfiles, perfiles[0])
        print(f"🦊 Usando perfil Firefox: {perfiles[0]}")
        return perfil
    
    def esperar_whatsapp_cargado(self):
        """Espera a que WhatsApp Web cargue completamente"""
        try:
            print("⏳ Esperando que WhatsApp Web cargue...")
            print("   (Si no has iniciado sesión, escanea el código QR)\n")
            
            # Esperar el buscador de chats
            self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@data-tab='3']"))
            )
            print("✅ WhatsApp Web cargado correctamente")
            time.sleep(3)
            return True
        except Exception as e:
            print(f"❌ Error: WhatsApp Web no cargó: {e}")
            return False
    
    def buscar_grupo(self, nombre_grupo):
        """Busca y abre el grupo de predicaciones"""
        print(f"\n🔍 Buscando grupo: '{nombre_grupo}'")
        
        try:
            # Buscar campo de búsqueda
            campo_busqueda = self.driver.find_element(
                By.XPATH, "//div[@contenteditable='true'][@data-tab='3']"
            )
            campo_busqueda.click()
            time.sleep(1)
            
            # Limpiar y buscar
            campo_busqueda.clear()
            time.sleep(0.5)
            campo_busqueda.send_keys(nombre_grupo)
            time.sleep(5)
            
            # Hacer clic en el grupo
            try:
                grupo = WebDriverWait(self.driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, f"//span[@title='{nombre_grupo}']"))
                )
                grupo.click()
                time.sleep(3)
                print(f"✅ Grupo '{nombre_grupo}' abierto")
                return True
            except:
                # Intento alternativo
                grupo = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, f"//span[contains(text(), '{nombre_grupo}')]"))
                )
                grupo.click()
                time.sleep(3)
                print(f"✅ Grupo '{nombre_grupo}' abierto")
                return True
                
        except Exception as e:
            print(f"❌ Error buscando grupo: {e}")
            return False
    
    def contar_mensajes_grupo(self):
        """Cuenta aproximadamente cuántos mensajes hay en el grupo"""
        try:
            # Hacer scroll hacia arriba varias veces para cargar más mensajes
            print("\n📊 Contando mensajes en el grupo...")
            
            for _ in range(5):
                self.driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(1)
            
            # Contar elementos de mensaje
            mensajes = self.driver.find_elements(
                By.XPATH, "//div[@data-id and contains(@class, 'message-')]"
            )
            
            total = len(mensajes)
            print(f"✅ Mensajes detectados: ~{total}")
            return total
            
        except Exception as e:
            print(f"⚠️  Error contando mensajes: {e}")
            return 0
    
    def extraer_siguiente_lote(self, cantidad=10, indice_inicio=0):
        """
        Extrae el siguiente lote de predicaciones desde indice_inicio
        Similar al sistema de Marketplace con indice_catalogo
        
        Args:
            cantidad: Cuántas predicaciones extraer
            indice_inicio: Desde qué posición empezar (0 = primera extracción)
            
        Returns:
            list: Lista de predicaciones extraídas
        """
        print(f"\n{'='*60}")
        print(f"🎯 EXTRAYENDO PREDICACIONES")
        print(f"{'='*60}")
        print(f"   Desde posición: {indice_inicio + 1}")
        print(f"   Cantidad a extraer: {cantidad}")
        print(f"   Rango: [{indice_inicio + 1} - {indice_inicio + cantidad}]")
        print(f"{'='*60}\n")
        
        predicaciones_extraidas = []
        
        try:
            # Hacer scroll hacia abajo para cargar mensajes recientes
            print("📜 Cargando mensajes del grupo...")
            for i in range(3):
                self.driver.execute_script(
                    "arguments[0].scrollTop = arguments[0].scrollHeight;",
                    self.driver.find_element(By.ID, "main")
                )
                time.sleep(2)
            
            # Obtener todos los mensajes
            mensajes = self.driver.find_elements(
                By.XPATH, "//div[contains(@class, 'message-in') or contains(@class, 'message-out')]"
            )
            
            print(f"📦 Total de mensajes en grupo: {len(mensajes)}")
            
            # Filtrar solo NUESTROS mensajes (message-out)
            mensajes_propios = [m for m in mensajes if 'message-out' in m.get_attribute('class')]
            print(f"📤 Mensajes propios (tuyos): {len(mensajes_propios)}")
            
            # Extraer el lote específico
            inicio = indice_inicio
            fin = indice_inicio + cantidad
            
            if inicio >= len(mensajes_propios):
                print("\n⚠️  No hay más mensajes nuevos para extraer")
                print(f"   Última posición extraída: {indice_inicio}")
                print(f"   Total de mensajes disponibles: {len(mensajes_propios)}")
                return []
            
            lote = mensajes_propios[inicio:fin]
            print(f"\n📋 Extrayendo mensajes [{inicio + 1} - {min(fin, len(mensajes_propios))}]")
            
            for idx, mensaje in enumerate(lote, start=inicio + 1):
                print(f"\n{'─'*60}")
                print(f"📦 MENSAJE {idx}/{len(mensajes_propios)}")
                print(f"{'─'*60}")
                
                predicacion = self._extraer_predicacion_de_mensaje(mensaje, idx)
                
                if predicacion:
                    predicaciones_extraidas.append(predicacion)
                    print(f"✅ Predicación {idx} extraída")
                else:
                    print(f"⏭️  Mensaje {idx} omitido (texto bíblico o sin contenido)")
            
            print(f"\n{'='*60}")
            print(f"✅ EXTRACCIÓN COMPLETADA")
            print(f"{'='*60}")
            print(f"📊 Predicaciones extraídas: {len(predicaciones_extraidas)}")
            print(f"📍 Nueva posición: {fin}")
            print(f"{'='*60}\n")
            
            return predicaciones_extraidas
            
        except Exception as e:
            print(f"\n❌ Error durante extracción: {e}")
            import traceback
            traceback.print_exc()
            return predicaciones_extraidas
    
    def _extraer_predicacion_de_mensaje(self, elemento_mensaje, numero):
        """
        Extrae el contenido de un mensaje individual
        
        Returns:
            dict o None: {'tipo': 'enlace'/'imagen', 'contenido': '...', 'numero': N}
        """
        try:
            # Buscar enlaces (YouTube, Instagram, Facebook, TikTok)
            enlaces = elemento_mensaje.find_elements(
                By.XPATH, ".//a[contains(@href, 'youtube.com') or "
                         "contains(@href, 'youtu.be') or "
                         "contains(@href, 'instagram.com') or "
                         "contains(@href, 'facebook.com') or "
                         "contains(@href, 'fb.watch') or "
                         "contains(@href, 'tiktok.com')]"
            )
            
            if enlaces:
                enlace_url = enlaces[0].get_attribute('href')
                print(f"🔗 Enlace detectado: {enlace_url[:50]}...")
                
                return {
                    'tipo': 'enlace',
                    'contenido': enlace_url,
                    'numero': numero
                }
            
            # Buscar imágenes
            imagenes = elemento_mensaje.find_elements(By.XPATH, ".//img[@src]")
            
            if imagenes:
                img_url = imagenes[0].get_attribute('src')
                
                # Filtrar iconos y emojis
                if 'emoji' not in img_url.lower() and len(img_url) > 50:
                    print(f"🖼️  Imagen detectada")
                    
                    return {
                        'tipo': 'imagen',
                        'contenido': img_url,
                        'numero': numero
                    }
            
            # Si llegamos aquí, es texto (lo ignoramos)
            return None
            
        except Exception as e:
            print(f"⚠️  Error extrayendo mensaje: {e}")
            return None
    
    def guardar_predicaciones(self, predicaciones):
        """Guarda las predicaciones en archivos individuales"""
        print(f"\n💾 Guardando {len(predicaciones)} predicaciones...")
        
        # Crear carpeta si no existe
        os.makedirs(self.carpeta_pendientes, exist_ok=True)
        
        for pred in predicaciones:
            numero = pred['numero']
            tipo = pred['tipo']
            contenido = pred['contenido']
            
            # Nombre de archivo
            if tipo == 'enlace':
                nombre_archivo = f"predica-{numero:03d}.txt"
                ruta_archivo = os.path.join(self.carpeta_pendientes, nombre_archivo)
                
                # Guardar enlace
                with open(ruta_archivo, 'w', encoding='utf-8') as f:
                    f.write(contenido)
                
                print(f"  ✅ {nombre_archivo} (enlace)")
                
            elif tipo == 'imagen':
                nombre_archivo = f"predica-{numero:03d}.txt"
                nombre_imagen = f"predica-{numero:03d}.jpg"
                ruta_archivo = os.path.join(self.carpeta_pendientes, nombre_archivo)
                ruta_imagen = os.path.join(self.carpeta_pendientes, nombre_imagen)
                
                # Descargar imagen
                try:
                    response = requests.get(contenido, timeout=10)
                    with open(ruta_imagen, 'wb') as f:
                        f.write(response.content)
                    
                    # Guardar referencia
                    with open(ruta_archivo, 'w', encoding='utf-8') as f:
                        f.write(f"[IMAGEN]\n{nombre_imagen}")
                    
                    print(f"  ✅ {nombre_archivo} (imagen)")
                except Exception as e:
                    print(f"  ⚠️  Error descargando imagen: {e}")
        
        print(f"✅ {len(predicaciones)} predicaciones guardadas en: {self.carpeta_pendientes}/")
    
    def ejecutar(self, nombre_grupo, cantidad=10, indice_inicio=0):
        """
        Ejecuta el proceso completo de extracción
        
        Args:
            nombre_grupo: Nombre del grupo de WhatsApp
            cantidad: Cuántas predicaciones extraer
            indice_inicio: Desde qué posición empezar
            
        Returns:
            list: Lista de predicaciones extraídas
        """
        print("\n" + "="*60)
        print("📱 EXTRACTOR DE PREDICACIONES DE WHATSAPP")
        print("="*60 + "\n")
        
        try:
            # Iniciar navegador
            self.iniciar_navegador()
            
            # Esperar carga
            if not self.esperar_whatsapp_cargado():
                return []
            
            # Buscar grupo
            if not self.buscar_grupo(nombre_grupo):
                return []
            
            # Extraer lote
            predicaciones = self.extraer_siguiente_lote(cantidad, indice_inicio)
            
            if predicaciones:
                # Guardar archivos
                self.guardar_predicaciones(predicaciones)
            
            return predicaciones
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return []
        
        finally:
            if self.driver:
                print("\n⏳ Cerrando navegador en 5 segundos...")
                time.sleep(5)
                self.driver.quit()
                print("✅ Navegador cerrado")
    
    def cerrar_navegador(self):
        """Cierra el navegador"""
        if self.driver:
            self.driver.quit()
