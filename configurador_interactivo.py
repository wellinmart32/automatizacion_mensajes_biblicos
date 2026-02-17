import os
import configparser
from compartido.gestor_archivos import leer_config_global


class ConfiguradorInteractivo:
    """Configurador interactivo para el sistema de publicación en Facebook"""

    def __init__(self):
        self.archivo_config = "config_global.txt"
        self.config = configparser.ConfigParser()
        self.cambios_realizados = False

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
        print(" " * 12 + "Publicador Automático - Mensajes Bíblicos")
        print("=" * 70)
        print()

    def mostrar_config_actual(self):
        """Muestra la configuración actual"""
        print("📋 CONFIGURACIÓN ACTUAL:\n")

        for seccion in self.config.sections():
            print(f"[{seccion}]")
            for clave, valor in self.config[seccion].items():
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

    def mostrar_ayuda(self):
        """Muestra explicación de cada opción del menú"""
        self.limpiar_pantalla()
        self.mostrar_header()
        print("❓ AYUDA - ¿QUÉ HACE CADA OPCIÓN?\n")
        print("=" * 70)

        print("\n  0. 🔄 REINICIAR SISTEMA")
        print("     Borra todo el historial y configuración.")
        print("     Útil si quieres empezar desde cero.")

        print("\n  1. ⚙️  CONFIGURACIÓN GENERAL")
        print("     Cambia la carpeta donde están tus mensajes .txt")
        print("     y el navegador a usar (Firefox o Chrome).")

        print("\n  2. 📝 CONFIGURACIÓN DE MENSAJES")
        print("     Define si los mensajes se publican en orden")
        print("     o de forma aleatoria, y cuántos evitar repetir.")

        print("\n  3. 🚀 CONFIGURACIÓN DE PUBLICACIÓN")
        print("     Tiempo de espera entre intentos y")
        print("     máximo de reintentos si falla algo.")

        print("\n  4. 📱 CONFIGURACIÓN DE WHATSAPP")
        print("     Nombre del grupo de WhatsApp de predicaciones,")
        print("     cantidad a extraer y si alternar con mensajes bíblicos.")

        print("\n  5. 🌐 CONFIGURACIÓN DE NAVEGADOR")
        print("     Si usar tu perfil guardado de Facebook")
        print("     o abrir una sesión nueva.")

        print("\n  6. 🔒 CONFIGURACIÓN DE LÍMITES")
        print("     Tiempo mínimo entre publicaciones para")
        print("     evitar duplicados si se ejecuta dos veces.")

        print("\n  7. 📋 VER CONFIGURACIÓN COMPLETA")
        print("     Muestra todos los valores actuales")
        print("     sin modificar nada.")

        print("\n  8. 🗓️  GESTIÓN DE TAREAS AUTOMÁTICAS  [FULL]")
        print("     Crea o elimina las tareas programadas de Windows")
        print("     para que la app se ejecute automáticamente.")

        print("\n  9. 💾 GUARDAR Y SALIR")
        print("     Guarda todos los cambios realizados.")

        print("\n  10. ❌ SALIR SIN GUARDAR")
        print("      Sale sin aplicar ningún cambio.")

        print("\n" + "=" * 70)
        input("\nPresiona Enter para volver al menú...")

    def menu_principal(self):
        """Muestra el menú principal"""
        while True:
            self.limpiar_pantalla()
            self.mostrar_header()
            self.mostrar_config_actual()

            print("=" * 70)
            print("\n🔧 OPCIONES:\n")
            print("  0.  🔄 Reiniciar sistema desde cero")
            print("  1.  ⚙️  Configuración General")
            print("  2.  📝 Configuración de Mensajes")
            print("  3.  🚀 Configuración de Publicación")
            print("  4.  📱 Configuración de WhatsApp (Predicaciones)")
            print("  5.  🌐 Configuración de Navegador")
            print("  6.  🔒 Configuración de Límites")
            print("  7.  📋 Ver configuración completa")
            print("  8.  🗓️  Gestión de Tareas Automáticas [FULL]")
            print("  9.  💾 Guardar y salir")
            print("  10. ❌ Salir sin guardar")
            print("  ?   ❓ Ayuda - ¿Qué hace cada opción?")
            print("\n" + "=" * 70)

            opcion = input("\n👉 Selecciona opción: ").strip()

            if opcion == '0':
                self.reiniciar_sistema()
            elif opcion == '1':
                self.menu_general()
            elif opcion == '2':
                self.menu_mensajes()
            elif opcion == '3':
                self.menu_publicacion()
            elif opcion == '4':
                self.menu_whatsapp()
            elif opcion == '5':
                self.menu_navegador()
            elif opcion == '6':
                self.menu_limites()
            elif opcion == '7':
                self.mostrar_config_actual()
                input("\nPresiona Enter para volver...")
            elif opcion == '8':
                self.menu_tareas_automaticas()
            elif opcion == '9':
                if self.cambios_realizados:
                    self.guardar_config()
                else:
                    print("\n✅ No hay cambios para guardar.")
                input("\nPresiona Enter para salir...")
                break
            elif opcion == '10':
                if self.cambios_realizados:
                    conf = input("\n⚠️  Hay cambios sin guardar. ¿Salir? (si/no): ")
                    if conf.lower() in ['si', 'sí', 's']:
                        break
                else:
                    break
            elif opcion == '?':
                self.mostrar_ayuda()
            else:
                print("\n❌ Opción inválida")
                input("Presiona Enter para continuar...")

    def reiniciar_sistema(self):
        """Reinicia el sistema desde cero"""
        self.limpiar_pantalla()
        self.mostrar_header()
        print("🔄 REINICIAR SISTEMA DESDE CERO\n")
        print("⚠️  ADVERTENCIA: Esto borrará TODO el historial de publicaciones")
        print("   Los mensajes .txt NO se borrarán\n")

        confirmar = input("¿Estás seguro? Escribe 'CONFIRMAR' para continuar: ").strip()

        if confirmar == 'CONFIRMAR':
            try:
                import json
                if os.path.exists('registro_publicaciones.json'):
                    os.remove('registro_publicaciones.json')
                print("\n✅ Sistema reiniciado correctamente")
                print("   El historial de publicaciones fue borrado")
            except Exception as e:
                print(f"\n❌ Error al reiniciar: {e}")
        else:
            print("\n❌ Reinicio cancelado")

        input("\nPresiona Enter para volver...")

    def menu_general(self):
        """Menú de configuración general"""
        self.limpiar_pantalla()
        self.mostrar_header()
        print("⚙️  CONFIGURACIÓN GENERAL\n")

        print("📁 Carpeta de mensajes")
        print(f"   Actual: {self.config['GENERAL']['carpeta_mensajes']}")
        nuevo = input("   Nueva carpeta (Enter para mantener): ").strip()
        if nuevo:
            self.config['GENERAL']['carpeta_mensajes'] = nuevo
            self.cambios_realizados = True
            print("   ✅ Cambiado")

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
        print("📝 CONFIGURACIÓN DE MENSAJES\n")

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

        print("\n# Agregar hashtags automáticamente")
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

        if self.config['MENSAJES']['agregar_hashtags'] == 'si':
            print("\n📌 Hashtags (separados por comas)")
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

    def menu_whatsapp(self):
        """Menú de configuración de WhatsApp (predicaciones)"""
        self.limpiar_pantalla()
        self.mostrar_header()
        print("📱 CONFIGURACIÓN DE WHATSAPP (Predicaciones)\n")

        nombre_actual = self.config.get('PREDICACIONES', 'nombre_grupo_whatsapp', fallback='Prédicas')
        print("👥 Nombre del grupo de WhatsApp")
        print(f"   Actual: {nombre_actual}")
        print("   ⚠️  Debe ser EXACTAMENTE igual a como aparece en WhatsApp")
        nuevo = input("   Nuevo nombre (Enter para mantener): ").strip()
        if nuevo:
            if not self.config.has_section('PREDICACIONES'):
                self.config.add_section('PREDICACIONES')
            self.config.set('PREDICACIONES', 'nombre_grupo_whatsapp', nuevo)
            self.cambios_realizados = True
            print("   ✅ Cambiado")

        cantidad_actual = self.config.get('PREDICACIONES', 'mensajes_por_extraccion', fallback='10')
        print("\n📦 Cantidad de predicaciones a extraer por vez")
        print(f"   Actual: {cantidad_actual}")
        nuevo = input("   Nuevo valor (Enter para mantener): ").strip()
        if nuevo:
            valido, resultado = self.validar_numero_positivo(nuevo, min_val=1, max_val=50)
            if valido:
                if not self.config.has_section('PREDICACIONES'):
                    self.config.add_section('PREDICACIONES')
                self.config.set('PREDICACIONES', 'mensajes_por_extraccion', str(resultado))
                self.cambios_realizados = True
                print("   ✅ Cambiado")
            else:
                print(f"   {resultado}")

        alternar_actual = self.config.get('PREDICACIONES', 'alternar_con_predicaciones', fallback='si')
        print("\n🔀 Alternar mensajes bíblicos con predicaciones")
        print(f"   Actual: {alternar_actual}")
        print("   (si = publica 1 bíblico, 1 predicación, 1 bíblico...)")
        nuevo = input("   Nuevo valor (si/no, Enter para mantener): ").strip()
        if nuevo:
            valido, resultado = self.validar_si_no(nuevo)
            if valido:
                if not self.config.has_section('PREDICACIONES'):
                    self.config.add_section('PREDICACIONES')
                self.config.set('PREDICACIONES', 'alternar_con_predicaciones', resultado)
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

        print("👤 Usar perfil existente del navegador")
        print(f"   Actual: {self.config['NAVEGADOR']['usar_perfil_existente']}")
        print("   (si = usa tu sesión de Facebook guardada)")
        nuevo = input("   Nuevo valor (si/no, Enter para mantener): ").strip()
        if nuevo:
            valido, resultado = self.validar_si_no(nuevo)
            if valido:
                self.config['NAVEGADOR']['usar_perfil_existente'] = resultado
                self.cambios_realizados = True
                print("   ✅ Cambiado")
            else:
                print(f"   {resultado}")

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

    def menu_limites(self):
        """Menú de configuración de límites"""
        self.limpiar_pantalla()
        self.mostrar_header()
        print("🔒 CONFIGURACIÓN DE LÍMITES\n")

        print("⏰ Tiempo mínimo entre publicaciones (segundos)")
        print(f"   Actual: {self.config['LIMITES']['tiempo_minimo_entre_publicaciones_segundos']}")
        print("   (Evita duplicados si se ejecuta 2 veces seguidas)")
        nuevo = input("   Nuevo valor (Enter para mantener): ").strip()
        if nuevo:
            valido, resultado = self.validar_numero_positivo(nuevo, min_val=30, max_val=600)
            if valido:
                self.config['LIMITES']['tiempo_minimo_entre_publicaciones_segundos'] = str(resultado)
                self.cambios_realizados = True
                print("   ✅ Cambiado")
            else:
                print(f"   {resultado}")

        print("\n🔓 Permitir forzar publicación manual")
        print(f"   Actual: {self.config['LIMITES']['permitir_forzar_publicacion_manual']}")
        print("   (si = permite saltarse el tiempo mínimo en ejecución manual)")
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

    def menu_tareas_automaticas(self):
        """Menú de gestión de tareas automáticas [FULL]"""
        self.limpiar_pantalla()
        self.mostrar_header()
        print("🗓️  GESTIÓN DE TAREAS AUTOMÁTICAS\n")
        print("⚠️  Esta función requiere licencia FULL\n")
        print("   Permite crear tareas programadas en Windows para que")
        print("   la aplicación se ejecute automáticamente cada día.\n")
        print("   💡 Próximamente disponible en versión FULL")
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