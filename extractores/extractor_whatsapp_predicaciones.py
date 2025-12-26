import os
import time
import json
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options as FirefoxOptions


class ExtractorWhatsAppPredicaciones:
    """
    Extractor de predicaciones desde WhatsApp Web - VERSIÓN FINAL
    - Extrae de más nuevo a más viejo con scroll inteligente
    - Detecta predicaciones ya publicadas (historial JSON)
    - Se detiene al tener 5 pendientes o al llegar al inicio del grupo
    """
    
    def __init__(self):
        self.driver = None
        self.carpeta_pendientes = "cola-facebook/pendientes"
        self.carpeta_publicados = "cola-facebook/publicados"
        self.archivo_historial = "cola-facebook/historial_publicados.json"
        
        # Configuración
        self.PREDICACIONES_OBJETIVO = 5  # Mantener 5 predicaciones pendientes
        self.MAX_SCROLLS = 200  # Máximo de scrolls (seguridad)
        self.SCROLLS_SIN_CAMBIO_LIMITE = 15  # Parar si 15 scrolls no encuentran nuevas
        
        # Crear carpetas
        os.makedirs(self.carpeta_pendientes, exist_ok=True)
        os.makedirs(self.carpeta_publicados, exist_ok=True)
    
    def cargar_historial(self):
        """Carga el historial de predicaciones publicadas"""
        if os.path.exists(self.archivo_historial):
            try:
                with open(self.archivo_historial, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return self._crear_historial_vacio()
        return self._crear_historial_vacio()
    
    def _crear_historial_vacio(self):
        """Crea estructura de historial vacío"""
        return {
            "urls_publicadas": [],
            "total_publicadas": 0,
            "ultima_actualizacion": None
        }
    
    def contar_pendientes(self):
        """Cuenta cuántas predicaciones hay pendientes"""
        if not os.path.exists(self.carpeta_pendientes):
            return 0
        
        archivos = [f for f in os.listdir(self.carpeta_pendientes) 
                   if f.startswith('predica-') and f.endswith('.txt')]
        return len(archivos)
    
    def obtener_siguiente_numero(self):
        """Obtiene el siguiente número de predicación disponible"""
        todos = []
        
        for carpeta in [self.carpeta_pendientes, self.carpeta_publicados]:
            if os.path.exists(carpeta):
                for archivo in os.listdir(carpeta):
                    if archivo.startswith('predica-') and archivo.endswith('.txt'):
                        try:
                            num = int(archivo.replace('predica-', '').replace('.txt', ''))
                            todos.append(num)
                        except:
                            pass
        
        return max(todos) + 1 if todos else 1
    
    def iniciar_navegador(self):
        """Inicializa Firefox con perfil existente"""
        print("🌐 Iniciando Firefox para WhatsApp Web...")
        
        try:
            opciones = FirefoxOptions()
            
            # Detectar perfil de Firefox
            import platform
            
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
                        print(f"🦊 Usando perfil Firefox: {carpeta}")
                        break
            
            if perfil_path:
                opciones.add_argument('-profile')
                opciones.add_argument(perfil_path)
            
            self.driver = webdriver.Firefox(options=opciones)
            self.driver.maximize_window()
            print("✅ Navegador iniciado")
            
            # Ir a WhatsApp Web
            print("📱 Abriendo WhatsApp Web...")
            self.driver.get("https://web.whatsapp.com")
            
            return True
            
        except Exception as e:
            print(f"❌ Error iniciando navegador: {e}")
            return False
    
    def esperar_whatsapp_cargado(self, timeout=60):
        """Espera a que WhatsApp Web esté completamente cargado"""
        print("⏳ Esperando que WhatsApp Web cargue...")
        print("   (Si no has iniciado sesión, escanea el código QR)")
        
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@data-tab='3']"))
            )
            print("\n✅ WhatsApp Web cargado correctamente\n")
            return True
            
        except Exception as e:
            print(f"\n❌ Error esperando carga de WhatsApp: {e}")
            return False
    
    def buscar_grupo(self, nombre_grupo):
        """Busca y abre un grupo específico"""
        print(f"🔍 Buscando grupo: '{nombre_grupo}'")
        
        try:
            # Limpiar barra de búsqueda
            barra_busqueda = self.driver.find_element(
                By.XPATH, "//div[@contenteditable='true'][@data-tab='3']"
            )
            barra_busqueda.click()
            time.sleep(0.5)
            
            barra_busqueda.send_keys(Keys.CONTROL + "a")
            barra_busqueda.send_keys(Keys.BACKSPACE)
            time.sleep(0.5)
            
            # Escribir nombre completo del grupo
            barra_busqueda.send_keys(nombre_grupo)
            time.sleep(3)
            
            # Hacer clic en el primer resultado
            resultado = self.driver.find_element(
                By.XPATH, f"//span[@title='{nombre_grupo}']"
            )
            resultado.click()
            time.sleep(3)
            
            print(f"✅ Grupo '{nombre_grupo}' abierto\n")
            return True
            
        except Exception as e:
            print(f"❌ Error buscando grupo: {e}")
            return False
    
    def extraer_siguiente_lote(self, cantidad=None, indice_inicio=0, solo_propios=True):
        """
        NUEVA ESTRATEGIA INTELIGENTE:
        Extrae predicaciones con scroll progresivo y detección de publicadas
        Se detiene al tener 5 pendientes o al llegar al inicio del grupo
        """
        if cantidad is None:
            cantidad = self.PREDICACIONES_OBJETIVO
        
        print(f"\n{'='*80}")
        print(f"🎯 EXTRACCIÓN INTELIGENTE DE PREDICACIONES")
        print(f"{'='*80}")
        print(f"   🎯 Objetivo: {self.PREDICACIONES_OBJETIVO} predicaciones pendientes")
        print(f"   📊 Actualmente pendientes: {self.contar_pendientes()}")
        print(f"{'='*80}\n")
        
        # Cargar historial de publicadas
        historial = self.cargar_historial()
        urls_publicadas = set(historial["urls_publicadas"])
        print(f"📚 Historial cargado: {len(urls_publicadas)} predicaciones ya publicadas\n")
        
        try:
            contenedor_chat = self.driver.find_element(By.ID, "main")
            
            predicaciones_extraidas = []
            numero_siguiente = self.obtener_siguiente_numero()
            scrolls_realizados = 0
            scrolls_sin_nuevos = 0
            
            print("🔄 Iniciando extracción...\n")
            
            while True:
                # Verificar si ya tenemos suficientes pendientes
                total_pendientes = self.contar_pendientes() + len(predicaciones_extraidas)
                
                if total_pendientes >= self.PREDICACIONES_OBJETIVO:
                    print(f"\n✅ OBJETIVO ALCANZADO: {total_pendientes} predicaciones pendientes")
                    break
                
                # Seguridad: límite de scrolls
                if scrolls_realizados >= self.MAX_SCROLLS:
                    print(f"\n⚠️  Límite de scrolls alcanzado ({self.MAX_SCROLLS})")
                    break
                
                # Seguridad: muchos scrolls sin encontrar nuevas
                if scrolls_sin_nuevos >= self.SCROLLS_SIN_CAMBIO_LIMITE:
                    print(f"\n⛔ {self.SCROLLS_SIN_CAMBIO_LIMITE} scrolls sin encontrar predicaciones nuevas")
                    print("   Probablemente llegamos al inicio del grupo")
                    break
                
                # Obtener mensajes actuales del DOM (solo mensajes propios)
                mensajes_dom = self.driver.find_elements(
                    By.XPATH, "//div[contains(@class, 'message-out')]"
                )
                
                print(f"{'─'*60}")
                print(f"📊 Iteración #{scrolls_realizados + 1}")
                print(f"{'─'*60}")
                print(f"   Mensajes en DOM: {len(mensajes_dom)}")
                print(f"   Pendientes actuales: {total_pendientes}/{self.PREDICACIONES_OBJETIVO}")
                
                # Extraer URLs de los mensajes actuales
                nuevas_extraidas = 0
                
                for mensaje in mensajes_dom:
                    url = self._extraer_predicacion_de_mensaje(mensaje)
                    
                    if not url:
                        continue
                    
                    # ¿Ya está publicada?
                    if url in urls_publicadas:
                        continue
                    
                    # ¿Ya la extrajimos en esta sesión?
                    if any(p['contenido'] == url for p in predicaciones_extraidas):
                        continue
                    
                    # ✅ Es nueva, extraer
                    predicaciones_extraidas.append({
                        'tipo': 'enlace',
                        'contenido': url,
                        'numero': numero_siguiente
                    })
                    
                    print(f"   ✅ Nueva: predica-{numero_siguiente:03d}.txt")
                    print(f"      URL: {url[:60]}...")
                    
                    numero_siguiente += 1
                    nuevas_extraidas += 1
                    
                    # Verificar si ya tenemos suficientes
                    if self.contar_pendientes() + len(predicaciones_extraidas) >= self.PREDICACIONES_OBJETIVO:
                        break
                
                if nuevas_extraidas > 0:
                    print(f"   📦 Extraídas en esta iteración: {nuevas_extraidas}")
                    scrolls_sin_nuevos = 0
                else:
                    scrolls_sin_nuevos += 1
                    print(f"   ⏭️  Sin nuevas ({scrolls_sin_nuevos}/{self.SCROLLS_SIN_CAMBIO_LIMITE})")
                
                # Si ya tenemos suficientes, parar
                if self.contar_pendientes() + len(predicaciones_extraidas) >= self.PREDICACIONES_OBJETIVO:
                    break
                
                # Hacer scroll hacia arriba para cargar mensajes más antiguos
                print(f"   🔄 Haciendo scroll para cargar mensajes más antiguos...")
                self._hacer_scroll_arriba(contenedor_chat)
                scrolls_realizados += 1
                
                # Esperar a que WhatsApp cargue mensajes
                time.sleep(5)
            
            print(f"\n{'='*80}")
            print(f"📊 RESUMEN DE EXTRACCIÓN")
            print(f"{'='*80}")
            print(f"   Total extraídas: {len(predicaciones_extraidas)}")
            print(f"   Scrolls realizados: {scrolls_realizados}")
            print(f"   Pendientes finales: {self.contar_pendientes() + len(predicaciones_extraidas)}")
            print(f"{'='*80}\n")
            
            return predicaciones_extraidas
            
        except Exception as e:
            print(f"\n❌ ERROR durante extracción: {e}")
            import traceback
            traceback.print_exc()
            return predicaciones_extraidas
    
    def _hacer_scroll_arriba(self, contenedor_chat):
        """Hace scroll hacia arriba usando múltiples estrategias"""
        try:
            # Estrategia 1: scrollTop
            current_scroll = self.driver.execute_script(
                "return arguments[0].scrollTop;", 
                contenedor_chat
            )
            new_position = max(0, current_scroll - 3000)
            self.driver.execute_script(
                f"arguments[0].scrollTop = {new_position};", 
                contenedor_chat
            )
            time.sleep(0.5)
            
            # Estrategia 2: scrollIntoView del primer mensaje
            try:
                primer_mensaje = self.driver.find_element(
                    By.XPATH, 
                    "(//div[contains(@class, 'message-out')])[1]"
                )
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'start', behavior: 'smooth'});", 
                    primer_mensaje
                )
                time.sleep(0.5)
            except:
                pass
                
        except Exception as e:
            print(f"   ⚠️  Error en scroll: {e}")
    
    def _extraer_predicacion_de_mensaje(self, elemento_mensaje):
        """
        Extrae el contenido (URL) de un mensaje individual
        Retorna la URL o None si no encuentra nada válido
        """
        try:
            # Estrategia 1: Buscar enlaces con clase copyable-text
            try:
                enlaces_copyable = elemento_mensaje.find_elements(
                    By.XPATH, ".//a[contains(@class, 'copyable-text')]"
                )
                
                for enlace in enlaces_copyable:
                    href = enlace.get_attribute('href')
                    if href and self._es_url_valida(href):
                        return href
            except:
                pass
            
            # Estrategia 2: Buscar en texto con regex
            try:
                texto_elemento = elemento_mensaje.find_element(
                    By.XPATH, ".//span[contains(@class, 'copyable-text')]"
                )
                texto = texto_elemento.text
                
                import re
                patron_url = r'https?://(?:www\.)?(?:instagram\.com|youtube\.com|youtu\.be|facebook\.com|fb\.watch|tiktok\.com)[^\s]+'
                match = re.search(patron_url, texto)
                
                if match:
                    return match.group(0)
            except:
                pass
            
            # Estrategia 3: Método tradicional
            try:
                enlaces = elemento_mensaje.find_elements(
                    By.XPATH, ".//a[contains(@href, 'youtube.com') or "
                             "contains(@href, 'youtu.be') or "
                             "contains(@href, 'instagram.com') or "
                             "contains(@href, 'facebook.com') or "
                             "contains(@href, 'fb.watch') or "
                             "contains(@href, 'tiktok.com')]"
                )
                
                if enlaces:
                    return enlaces[0].get_attribute('href')
            except:
                pass
            
            return None
            
        except:
            return None
    
    def _es_url_valida(self, url):
        """Verifica si la URL es de una plataforma válida"""
        dominios_validos = ['instagram.com', 'youtube.com', 'youtu.be', 'facebook.com', 'fb.watch', 'tiktok.com']
        return any(dominio in url for dominio in dominios_validos)
    
    def guardar_predicaciones(self, predicaciones):
        """Guarda las predicaciones en archivos individuales"""
        if not predicaciones:
            print("⚠️  No hay predicaciones para guardar")
            return
        
        print(f"\n💾 Guardando {len(predicaciones)} predicaciones...")
        
        for pred in predicaciones:
            numero = pred['numero']
            tipo = pred['tipo']
            contenido = pred['contenido']
            
            if tipo == 'enlace':
                nombre_archivo = f"predica-{numero:03d}.txt"
                ruta_archivo = os.path.join(self.carpeta_pendientes, nombre_archivo)
                
                with open(ruta_archivo, 'w', encoding='utf-8') as f:
                    f.write(contenido)
                
                print(f"  ✅ {nombre_archivo}")
        
        print(f"✅ Predicaciones guardadas en: {self.carpeta_pendientes}/\n")
    
    def ejecutar(self, nombre_grupo, cantidad=None, indice_inicio=0, solo_propios=True):
        """
        Método principal de ejecución
        Compatible con el sistema existente
        """
        if cantidad is None:
            cantidad = self.PREDICACIONES_OBJETIVO
        
        print("\n" + "="*80)
        print("📱 EXTRACTOR DE PREDICACIONES - VERSIÓN FINAL")
        print("="*80 + "\n")
        
        try:
            if not self.iniciar_navegador():
                return []
            
            if not self.esperar_whatsapp_cargado():
                return []
            
            if not self.buscar_grupo(nombre_grupo):
                return []
            
            predicaciones = self.extraer_siguiente_lote(
                cantidad=cantidad,
                indice_inicio=indice_inicio,
                solo_propios=solo_propios
            )
            
            if predicaciones:
                self.guardar_predicaciones(predicaciones)
            
            return predicaciones
            
        finally:
            self.cerrar()
    
    def cerrar(self):
        """Cierra el navegador"""
        if self.driver:
            print("\n⏳ Cerrando navegador en 5 segundos...")
            time.sleep(5)
            self.driver.quit()
            print("✅ Navegador cerrado")


if __name__ == "__main__":
    extractor = ExtractorWhatsAppPredicaciones()
    extractor.ejecutar("Prédicas")
