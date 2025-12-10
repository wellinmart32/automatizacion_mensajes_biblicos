import os
import configparser
from compartido.gestor_archivos import leer_config_global


class ConfiguradorInteractivo:
    """Configurador interactivo para el sistema de publicación en Facebook"""
    
    def __init__(self):
        self.archivo_config = "config_global.txt"
        self.config = configparser.ConfigParser()
        self.cambios_realizados = False
        
        # Cargar configuración actual
        if os.path.exists(self.archivo_config):
            self.config.read(self.archivo_config, encoding='utf-8')
        else:
            print("⚠️  No existe config_global.txt")
            return
    
    def limpiar_pantalla(self):
        """Limpia la consola"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def mostrar_header(self):
        """Muestra el encabezado"""
        print("=" * 70)
        print(" " * 15 + "⚙️  CONFIGURADOR DEL SISTEMA")
        print(" " * 12 + "Publicador Automático Facebook")
        print("=" * 70)
        print()
    
    def mostrar_config_actual(self):
        """Muestra la configuración actual"""
        print("📋 CONFIGURACIÓN ACTUAL:\n")
        
        for seccion in self.config.sections():
            print(f"[{seccion}]")
            for clave, valor in self.config[seccion].items():
                # Limpiar comentarios
                valor_limpio = valor.split('#')[0].strip()
                print(f"  {clave} = {valor_limpio}")
            print()
    
    def guardar_config(self):
        """Guarda la configuración en el archivo"""
        try:
            with open(self.archivo_config, 'w', encoding='utf-8') as f:
                f.write("# ============================================================\n")
                f.write("# CONFIGURACIÓN GLOBAL - PUBLICADOR AUTOMÁTICO FACEBOOK\n")
                f.write("# ============================================================\n\n")
                self.config.write(f)
            print("\n✅ Configuración guardada exitosamente")
            self.cambios_realizados = False
            return True
        except Exception as e:
            print(f"\n❌ Error guardando configuración: {e}")
            return False
    
    def validar_si_no(self, valor):
        """Valida que sea 'si' o 'no'"""
        valor_lower = valor.lower().strip()
        if valor_lower in ['si', 'sí', 's', 'yes', 'y']:
            return True, 'si'
        elif valor_lower in ['no', 'n']:
            return True, 'no'
        else:
            return False, "❌ Debe ser 'si' o 'no'"
    
    def validar_numero_positivo(self, valor, min_val=1, max_val=None):
        """Valida que sea un número positivo"""
        try:
            num = int(valor)
            if num < min_val:
                return False, f"❌ Debe ser >= {min_val}"
            if max_val and num > max_val:
                return False, f"❌ Debe ser <= {max_val}"
            return True, num
        except ValueError:
            return False, "❌ Debe ser un número válido"
    
    def validar_navegador(self, valor):
        """Valida que sea firefox o chrome"""
        valor_lower = valor.lower().strip()
        if valor_lower in ['firefox', 'chrome']:
            return True, valor_lower
        else:
            return False, "❌ Debe ser 'firefox' o 'chrome'"
    
    def validar_seleccion(self, valor):
        """Valida método de selección"""
        valor_lower = valor.lower().strip()
        if valor_lower in ['aleatoria', 'secuencial']:
            return True, valor_lower
        else:
            return False, "❌ Debe ser 'aleatoria' o 'secuencial'"
    
    def menu_principal(self):
        """Muestra el menú principal"""
        while True:
            self.limpiar_pantalla()
            self.mostrar_header()
            self.mostrar_config_actual()
            
            print("=" * 70)
            print("\n🔧 OPCIONES:\n")
            print("  1. ⚙️  Configuración General")
            print("  2. 📱 Configuración de Mensajes")
            print("  3. 🚀 Configuración de Publicación")
            print("  4. ⏱️  Configuración de Límites")
            print("  5. 🌐 Configuración de Navegador")
            print("  6. 💾 Guardar y salir")
            print("  7. ❌ Salir sin guardar")
            print("\n" + "=" * 70)
            
            opcion = input("\n👉 Selecciona opción (1-7): ").strip()
            
            if opcion == '1':
                self.menu_general()
            elif opcion == '2':
                self.menu_mensajes()
            elif opcion == '3':
                self.menu_publicacion()
            elif opcion == '4':
                self.menu_limites()
            elif opcion == '5':
                self.menu_navegador()
            elif opcion == '6':
                if self.cambios_realizados:
                    self.guardar_config()
                print("\n✅ Saliendo...")
                input("Presiona Enter...")
                break
            elif opcion == '7':
                if self.cambios_realizados:
                    conf = input("\n⚠️  Hay cambios sin guardar. ¿Salir? (si/no): ")
                    if conf.lower() in ['si', 'sí', 's']:
                        break
                else:
                    break
    
    def menu_general(self):
        """Menú de configuración general"""
        self.limpiar_pantalla()
        self.mostrar_header()
        print("⚙️  CONFIGURACIÓN GENERAL\n")
        
        # Carpeta mensajes
        print("📁 Carpeta de mensajes")
        print(f"   Actual: {self.config['GENERAL']['carpeta_mensajes']}")
        nuevo = input("   Nueva carpeta (Enter para mantener): ").strip()
        if nuevo:
            self.config['GENERAL']['carpeta_mensajes'] = nuevo
            self.cambios_realizados = True
            print("   ✅ Cambiado")
        
        # Navegador
        print("\n🌐 Navegador (firefox o chrome)")
        print(f"   Actual: {self.config['GENERAL']['navegador']}")
        nuevo = input("   Nuevo navegador (Enter para mantener): ").strip()
        if nuevo:
            valido, resultado = self.validar_navegador(nuevo)
            if valido:
                self.config['GENERAL']['navegador'] = resultado
                self.cambios_realizados = True
                print("   ✅ Cambiado")
            else:
                print(f"   {resultado}")
        
        input("\n✅ Presiona Enter para volver...")
    
    def menu_mensajes(self):
        """Menú de configuración de mensajes"""
        self.limpiar_pantalla()
        self.mostrar_header()
        print("📱 CONFIGURACIÓN DE MENSAJES\n")
        
        # Método de selección
        print("🎲 Método de selección (aleatoria o secuencial)")
        print(f"   Actual: {self.config['MENSAJES']['seleccion']}")
        nuevo = input("   Nuevo método (Enter para mantener): ").strip()
        if nuevo:
            valido, resultado = self.validar_seleccion(nuevo)
            if valido:
                self.config['MENSAJES']['seleccion'] = resultado
                self.cambios_realizados = True
                print("   ✅ Cambiado")
            else:
                print(f"   {resultado}")
        
        # Historial evitar repetir
        print("\n💾 Memoria: Últimos N mensajes a evitar")
        print(f"   Actual: {self.config['MENSAJES']['historial_evitar_repetir']}")
        print("   (Con 21 mensajes, recomendado: 5)")
        nuevo = input("   Nuevo valor (Enter para mantener): ").strip()
        if nuevo:
            valido, resultado = self.validar_numero_positivo(nuevo, min_val=0, max_val=20)
            if valido:
                self.config['MENSAJES']['historial_evitar_repetir'] = str(resultado)
                self.cambios_realizados = True
                print("   ✅ Cambiado")
            else:
                print(f"   {resultado}")
        
        # Agregar hashtags
        print("\n#️⃣  Agregar hashtags automáticamente")
        print(f"   Actual: {self.config['MENSAJES']['agregar_hashtags']}")
        nuevo = input("   Nuevo valor (si/no, Enter para mantener): ").strip()
        if nuevo:
            valido, resultado = self.validar_si_no(nuevo)
            if valido:
                self.config['MENSAJES']['agregar_hashtags'] = resultado
                self.cambios_realizados = True
                print("   ✅ Cambiado")
            else:
                print(f"   {resultado}")
        
        # Hashtags
        if self.config['MENSAJES']['agregar_hashtags'] == 'si':
            print("\n📝 Hashtags (separados por comas)")
            print(f"   Actual: {self.config['MENSAJES']['hashtags']}")
            nuevo = input("   Nuevos hashtags (Enter para mantener): ").strip()
            if nuevo:
                self.config['MENSAJES']['hashtags'] = nuevo
                self.cambios_realizados = True
                print("   ✅ Cambiado")
        
        input("\n✅ Presiona Enter para volver...")
    
    def menu_publicacion(self):
        """Menú de configuración de publicación"""
        self.limpiar_pantalla()
        self.mostrar_header()
        print("🚀 CONFIGURACIÓN DE PUBLICACIÓN\n")
        
        # Tiempo entre intentos
        print("⏱️  Tiempo entre intentos (segundos)")
        print(f"   Actual: {self.config['PUBLICACION']['tiempo_entre_intentos']}")
        nuevo = input("   Nuevo valor (Enter para mantener): ").strip()
        if nuevo:
            valido, resultado = self.validar_numero_positivo(nuevo, min_val=1, max_val=30)
            if valido:
                self.config['PUBLICACION']['tiempo_entre_intentos'] = str(resultado)
                self.cambios_realizados = True
                print("   ✅ Cambiado")
            else:
                print(f"   {resultado}")
        
        # Máximo de intentos
        print("\n🔄 Máximo de intentos por publicación")
        print(f"   Actual: {self.config['PUBLICACION']['max_intentos_por_publicacion']}")
        nuevo = input("   Nuevo valor (Enter para mantener): ").strip()
        if nuevo:
            valido, resultado = self.validar_numero_positivo(nuevo, min_val=1, max_val=10)
            if valido:
                self.config['PUBLICACION']['max_intentos_por_publicacion'] = str(resultado)
                self.cambios_realizados = True
                print("   ✅ Cambiado")
            else:
                print(f"   {resultado}")
        
        # Espera después de publicar
        print("\n⏳ Espera después de publicar (segundos)")
        print(f"   Actual: {self.config['PUBLICACION']['espera_despues_publicar']}")
        nuevo = input("   Nuevo valor (Enter para mantener): ").strip()
        if nuevo:
            valido, resultado = self.validar_numero_positivo(nuevo, min_val=1, max_val=30)
            if valido:
                self.config['PUBLICACION']['espera_despues_publicar'] = str(resultado)
                self.cambios_realizados = True
                print("   ✅ Cambiado")
            else:
                print(f"   {resultado}")
        
        input("\n✅ Presiona Enter para volver...")
    
    def menu_limites(self):
        """Menú de configuración de límites"""
        self.limpiar_pantalla()
        self.mostrar_header()
        print("⏱️  CONFIGURACIÓN DE LÍMITES\n")
        
        # Tiempo mínimo entre publicaciones
        print("⏰ Tiempo mínimo entre publicaciones (segundos)")
        print(f"   Actual: {self.config['LIMITES']['tiempo_minimo_entre_publicaciones_segundos']}")
        print("   (Evita duplicados si se ejecuta 2 veces)")
        nuevo = input("   Nuevo valor (Enter para mantener): ").strip()
        if nuevo:
            valido, resultado = self.validar_numero_positivo(nuevo, min_val=30, max_val=600)
            if valido:
                self.config['LIMITES']['tiempo_minimo_entre_publicaciones_segundos'] = str(resultado)
                self.cambios_realizados = True
                print("   ✅ Cambiado")
            else:
                print(f"   {resultado}")
        
        # Permitir forzar manual
        print("\n🖱️  Permitir forzar publicación manual")
        print(f"   Actual: {self.config['LIMITES']['permitir_forzar_publicacion_manual']}")
        print("   (Si = permite saltarse el tiempo mínimo en ejecución manual)")
        nuevo = input("   Nuevo valor (si/no, Enter para mantener): ").strip()
        if nuevo:
            valido, resultado = self.validar_si_no(nuevo)
            if valido:
                self.config['LIMITES']['permitir_forzar_publicacion_manual'] = resultado
                self.cambios_realizados = True
                print("   ✅ Cambiado")
            else:
                print(f"   {resultado}")
        
        input("\n✅ Presiona Enter para volver...")
    
    def menu_navegador(self):
        """Menú de configuración del navegador"""
        self.limpiar_pantalla()
        self.mostrar_header()
        print("🌐 CONFIGURACIÓN DEL NAVEGADOR\n")
        
        # Usar perfil existente
        print("👤 Usar perfil existente del navegador")
        print(f"   Actual: {self.config['NAVEGADOR']['usar_perfil_existente']}")
        print("   (Si = usa tu sesión de Facebook guardada)")
        nuevo = input("   Nuevo valor (si/no, Enter para mantener): ").strip()
        if nuevo:
            valido, resultado = self.validar_si_no(nuevo)
            if valido:
                self.config['NAVEGADOR']['usar_perfil_existente'] = resultado
                self.cambios_realizados = True
                print("   ✅ Cambiado")
            else:
                print(f"   {resultado}")
        
        # Maximizar ventana
        print("\n🖥️  Maximizar ventana al iniciar")
        print(f"   Actual: {self.config['NAVEGADOR']['maximizar_ventana']}")
        nuevo = input("   Nuevo valor (si/no, Enter para mantener): ").strip()
        if nuevo:
            valido, resultado = self.validar_si_no(nuevo)
            if valido:
                self.config['NAVEGADOR']['maximizar_ventana'] = resultado
                self.cambios_realizados = True
                print("   ✅ Cambiado")
            else:
                print(f"   {resultado}")
        
        input("\n✅ Presiona Enter para volver...")
    
    def ejecutar(self):
        """Ejecuta el configurador"""
        try:
            self.menu_principal()
        except KeyboardInterrupt:
            print("\n\n❌ Configuración cancelada")
        except Exception as e:
            print(f"\n❌ Error: {e}")


def main():
    """Función principal"""
    configurador = ConfiguradorInteractivo()
    configurador.ejecutar()


if __name__ == "__main__":
    main()
