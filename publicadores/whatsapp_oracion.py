import os
import sys
import time
import json
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class PublicadorWhatsAppOracion:
    """
    Publicador de llamados de oración en grupos de WhatsApp
    - Lee mensajes aleatorios desde mensajes_oracion.txt
    - Lee grupos desde grupos.json
    - Publica en cada grupo activo
    """
    
    def __init__(self):
        self.driver = None
        self.carpeta_oracion = "llamados-oracion"
        self.archivo_mensajes = os.path.join(self.carpeta_oracion, "mensajes_oracion.txt")
        self.archivo_grupos = os.path.join(self.carpeta_oracion, "grupos.json")
        self.carpeta_perfil = "perfiles/whatsapp_oracion"
        
        # Configuración
        self.ESPERA_ENTRE_GRUPOS = 3  # Segundos entre cada grupo
        self.ESPERA_CARGA_WHATSAPP = 15  # Segundos para que cargue WhatsApp
        self.ESPERA_BUSQUEDA = 5  # Segundos para buscar grupo
    
    def cargar_mensajes(self):
        """Carga los mensajes de oración desde el archivo"""
        if not os.path.exists(self.archivo_mensajes):
            raise Exception(f"No se encontró {self.archivo_mensajes}")
        
        with open(self.archivo_mensajes, 'r', encoding='utf-8') as f:
            mensajes = [linea.strip() for linea in f if linea.strip()]
        
        if not mensajes:
            raise Exception("El archivo de mensajes está vacío")
        
        return mensajes
    
    def cargar_grupos(self):
        """Carga la lista de grupos desde el archivo JSON"""
        if not os.path.exists(self.archivo_grupos):
            raise Exception(f"No se encontró {self.archivo_grupos}")
        
        with open(self.archivo_grupos, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        
        # Filtrar solo grupos activos
        grupos_activos = [g for g in datos.get('grupos', []) if g.get('activo', False)]
        
        if not grupos_activos:
            raise Exception("No hay grupos activos en grupos.json")
        
        return grupos_activos
    
    def seleccionar_mensaje_aleatorio(self, mensajes):
        """Selecciona un mensaje aleatorio de la lista"""
        return random.choice(mensajes)
    
    def iniciar_navegador(self):
        """Inicia Firefox con perfil personalizado para WhatsApp"""
        print("\n🌐 Iniciando Firefox para WhatsApp Web...")
        
        try:
            # Crear carpeta de perfil si no existe
            os.makedirs(self.carpeta_perfil, exist_ok=True)
            
            # Configurar opciones de Firefox
            opciones = FirefoxOptions()
            opciones.set_preference("dom.webnotifications.enabled", False)
            opciones.set_preference("permissions.default.desktop-notification", 2)
            
            # Crear perfil
            self.driver = webdriver.Firefox(options=opciones)
            self.driver.maximize_window()
            
            print("   ✅ Navegador iniciado")
            return True
            
        except Exception as e:
            print(f"   ❌ Error iniciando navegador: {e}")
            return False
    
    def abrir_whatsapp_web(self):
        """Abre WhatsApp Web y espera a que esté listo"""
        print("\n📱 Abriendo WhatsApp Web...")
        
        try:
            self.driver.get("https://web.whatsapp.com")
            
            print(f"   ⏳ Esperando {self.ESPERA_CARGA_WHATSAPP}s a que cargue WhatsApp...")
            print("   💡 Si es la primera vez, escanea el código QR")
            
            time.sleep(self.ESPERA_CARGA_WHATSAPP)
            
            # Verificar que cargó (buscar el campo de búsqueda)
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@data-tab='3']"))
                )
                print("   ✅ WhatsApp Web cargado correctamente")
                return True
            except TimeoutException:
                print("   ⚠️  No se detectó el campo de búsqueda, pero continuando...")
                return True
                
        except Exception as e:
            print(f"   ❌ Error abriendo WhatsApp Web: {e}")
            return False
    
    def buscar_grupo(self, nombre_grupo):
        """Busca un grupo por nombre"""
        print(f"\n🔍 Buscando grupo: {nombre_grupo}")
        
        try:
            # Buscar el campo de búsqueda
            campo_busqueda = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@data-tab='3']"))
            )
            
            # Limpiar búsqueda anterior
            campo_busqueda.click()
            time.sleep(1)
            campo_busqueda.send_keys(Keys.CONTROL + "a")
            campo_busqueda.send_keys(Keys.DELETE)
            time.sleep(1)
            
            # Escribir nombre del grupo
            campo_busqueda.send_keys(nombre_grupo)
            time.sleep(self.ESPERA_BUSQUEDA)
            
            # Hacer clic en el primer resultado
            try:
                primer_resultado = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, f"//span[@title='{nombre_grupo}']"))
                )
                primer_resultado.click()
                time.sleep(2)
                
                print(f"   ✅ Grupo encontrado y abierto")
                return True
                
            except TimeoutException:
                print(f"   ❌ No se encontró el grupo '{nombre_grupo}'")
                return False
                
        except Exception as e:
            print(f"   ❌ Error buscando grupo: {e}")
            return False
    
    def enviar_mensaje(self, mensaje):
        """Envía un mensaje en el chat activo"""
        print(f"\n✍️  Enviando mensaje...")
        
        try:
            # Buscar el campo de texto
            campo_mensaje = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@data-tab='10']"))
            )
            
            # Escribir mensaje
            campo_mensaje.click()
            time.sleep(1)
            campo_mensaje.send_keys(mensaje)
            time.sleep(1)
            
            # Enviar (presionar Enter)
            campo_mensaje.send_keys(Keys.ENTER)
            time.sleep(2)
            
            print(f"   ✅ Mensaje enviado: {mensaje[:50]}...")
            return True
            
        except Exception as e:
            print(f"   ❌ Error enviando mensaje: {e}")
            return False
    
    def publicar_en_todos_los_grupos(self):
        """
        Función principal que publica en todos los grupos
        """
        print("\n" + "="*70)
        print(" " * 15 + "📱 PUBLICADOR DE LLAMADOS DE ORACIÓN")
        print(" " * 20 + "WhatsApp Web - Grupos")
        print("="*70 + "\n")
        
        # Cargar datos
        try:
            mensajes = self.cargar_mensajes()
            grupos = self.cargar_grupos()
        except Exception as e:
            print(f"❌ Error cargando archivos: {e}")
            return False
        
        print(f"📋 CONFIGURACIÓN:")
        print(f"   📝 Mensajes disponibles: {len(mensajes)}")
        print(f"   👥 Grupos activos: {len(grupos)}")
        print(f"   📁 Archivo mensajes: {self.archivo_mensajes}")
        print(f"   📁 Archivo grupos: {self.archivo_grupos}")
        
        # Mostrar grupos
        print(f"\n👥 GRUPOS A PUBLICAR:")
        for i, grupo in enumerate(grupos, 1):
            print(f"   {i}. {grupo['nombre']}")
        
        # Iniciar navegador
        if not self.iniciar_navegador():
            return False
        
        # Abrir WhatsApp Web
        if not self.abrir_whatsapp_web():
            self.cerrar_navegador()
            return False
        
        # Publicar en cada grupo
        exitos = 0
        fallos = 0
        
        print("\n" + "="*70)
        print("🚀 INICIANDO PUBLICACIONES")
        print("="*70)
        
        for i, grupo in enumerate(grupos, 1):
            nombre_grupo = grupo['nombre']
            
            print(f"\n{'='*70}")
            print(f"📤 GRUPO {i}/{len(grupos)}: {nombre_grupo}")
            print(f"{'='*70}")
            
            # Seleccionar mensaje aleatorio
            mensaje = self.seleccionar_mensaje_aleatorio(mensajes)
            print(f"🎲 Mensaje seleccionado: {mensaje[:50]}...")
            
            # Buscar grupo
            if not self.buscar_grupo(nombre_grupo):
                print(f"   ⚠️  Saltando grupo '{nombre_grupo}'")
                fallos += 1
                continue
            
            # Enviar mensaje
            if self.enviar_mensaje(mensaje):
                exitos += 1
                print(f"   ✅ Publicación exitosa en '{nombre_grupo}'")
            else:
                fallos += 1
                print(f"   ❌ Fallo en '{nombre_grupo}'")
            
            # Esperar entre grupos (excepto en el último)
            if i < len(grupos):
                print(f"\n   ⏳ Esperando {self.ESPERA_ENTRE_GRUPOS}s antes del siguiente grupo...")
                time.sleep(self.ESPERA_ENTRE_GRUPOS)
        
        # Resumen final
        print("\n" + "="*70)
        print("📊 RESUMEN DE PUBLICACIONES")
        print("="*70)
        print(f"   ✅ Exitosas: {exitos}")
        print(f"   ❌ Fallidas: {fallos}")
        print(f"   📊 Total grupos: {len(grupos)}")
        print(f"   🎯 Tasa de éxito: {(exitos/len(grupos)*100):.1f}%")
        print("="*70)
        
        # Cerrar navegador
        self.cerrar_navegador()
        
        return exitos > 0
    
    def cerrar_navegador(self):
        """Cierra el navegador"""
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
        exito = publicador.publicar_en_todos_los_grupos()
        
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
