import os
import configparser
from compartido.gestor_archivos import leer_config_global


class ConfiguradorInteractivo:
    """Configurador interactivo para el sistema de Marketplace"""

    def __init__(self):
        self.archivo_config = "config_global.txt"
        self.config = configparser.ConfigParser()
        self.cambios_realizados = False

        self.defaults = {
            'GENERAL': {
                'cantidad_productos': '5',
                'modo': 'completo'
            },
            'EXTRACCION': {
                'contacto_whatsapp': 'Trabajo John',
                'auto_scroll': '5',
                'productos_por_extraccion': '5'
            },
            'PUBLICACION': {
                'auto_publicar': 'si',
                'tiempo_entre_publicaciones': '10',
                'max_publicaciones_por_dia': '20',
                'publicar_todos': 'si'
            },
            'SEGURIDAD': {
                'confirmacion_borrado': 'si',
                'backup_antes_borrar': 'si'
            }
        }

    def limpiar_pantalla(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def mostrar_header(self):
        print("=" * 70)
        print(" " * 15 + "⚙️  CONFIGURADOR DEL SISTEMA")
        print(" " * 12 + "Publicador Automático - Marketplace")
        print("=" * 70)
        print()

    def mostrar_config_actual(self):
        print("📋 CONFIGURACIÓN ACTUAL:\n")
        for seccion in self.config.sections():
            print(f"[{seccion}]")
            for clave, valor in self.config[seccion].items():
                print(f"  {clave} = {valor}")
            print()

    def cargar_config(self):
        if os.path.exists(self.archivo_config):
            self.config.read(self.archivo_config, encoding='utf-8')
        else:
            print("⚠️  No existe config_global.txt. Creando configuración por defecto...\n")
            self.crear_config_defecto()

    def crear_config_defecto(self):
        for seccion, valores in self.defaults.items():
            self.config[seccion] = valores
        self.guardar_config()

    def guardar_config(self):
        try:
            with open(self.archivo_config, 'w', encoding='utf-8') as f:
                f.write("# ============================================================\n")
                f.write("# CONFIGURACIÓN GLOBAL DEL SISTEMA - MARKETPLACE\n")
                f.write("# ============================================================\n\n")
                self.config.write(f)
            print("\n✅ Configuración guardada exitosamente")
            self.cambios_realizados = False
            return True
        except Exception as e:
            print(f"\n❌ Error guardando configuración: {e}")
            return False

    def validar_numero_positivo(self, valor, min_val=1, max_val=None):
        try:
            num = int(valor)
            if num < min_val:
                return False, f"❌ Debe ser >= {min_val}"
            if max_val and num > max_val:
                return False, f"❌ Debe ser <= {max_val}"
            return True, num
        except ValueError:
            return False, "❌ Debe ser un número válido"

    def validar_si_no(self, valor):
        valor_lower = valor.lower().strip()
        if valor_lower in ['si', 'sí', 's', 'yes', 'y']:
            return True, 'si'
        elif valor_lower in ['no', 'n']:
            return True, 'no'
        else:
            return False, "❌ Debe ser 'si' o 'no'"

    def validar_modo(self, valor):
        modos_validos = ['completo', 'solo_extraer', 'solo_publicar']
        valor_lower = valor.lower().strip()
        if valor_lower in modos_validos:
            return True, valor_lower
        else:
            return False, f"❌ Debe ser uno de: {', '.join(modos_validos)}"

    def validar_contacto(self, valor):
        if len(valor.strip()) < 3:
            return False, "❌ El nombre debe tener al menos 3 caracteres"
        if len(valor.strip()) > 50:
            return False, "❌ El nombre no puede exceder 50 caracteres"
        return True, valor.strip()

    def mostrar_ayuda(self):
        self.limpiar_pantalla()
        self.mostrar_header()
        print("❓ AYUDA - ¿QUÉ HACE CADA OPCIÓN?\n")
        print("=" * 70)

        print("\n  0. 🔄 REINICIAR SISTEMA")
        print("     Borra todos los productos, historial y perfiles.")
        print("     Útil si quieres empezar desde cero.")

        print("\n  1. ⚙️  CONFIGURACIÓN GENERAL")
        print("     Cantidad de carpetas de productos y")
        print("     modo de operación (completo, solo extraer, solo publicar).")

        print("\n  2. 📝 CONFIGURACIÓN DE CONTENIDO")
        print("     Datos del artículo a publicar:")
        print("     título, precio, categoría, descripción, etc.")

        print("\n  3. 🚀 CONFIGURACIÓN DE PUBLICACIÓN")
        print("     Tiempo entre publicaciones, máximo por día")
        print("     y si publicar todos los productos o solo el siguiente.")

        print("\n  4. 📱 CONFIGURACIÓN DE WHATSAPP")
        print("     Nombre del contacto en WhatsApp Business")
        print("     del cual se extraen los productos del catálogo.")

        print("\n  5. 🌐 CONFIGURACIÓN DE NAVEGADOR")
        print("     Navegador a usar y configuración")
        print("     del perfil de sesión de Facebook.")

        print("\n  6. 🔒 CONFIGURACIÓN DE SEGURIDAD")
        print("     Confirmación antes de borrar carpetas")
        print("     y si crear backups automáticos.")

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
            print("\n" + "─" * 70)
            print("  🖥️  INTERFACES GRÁFICAS:\n")
            print("  G.  🎨 Abrir Configurador Gráfico")
            print("  M.  📄 Abrir Gestor de Mensajes")
            print("\n" + "=" * 70)
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
            elif opcion.upper() == 'G':
                self.abrir_configurador_grafico()
            elif opcion.upper() == 'M':
                self.abrir_gestor_mensajes()
            elif opcion == '?':
                self.mostrar_ayuda()
            else:
                print("\n❌ Opción inválida")
                input("Presiona Enter para continuar...")

    def reiniciar_sistema_completo(self):
        self.limpiar_pantalla()
        self.mostrar_header()
        print("🔄 REINICIAR SISTEMA DESDE CERO\n")
        print("⚠️  ADVERTENCIA: Esta acción eliminará:\n")
        print("   ❌ Carpeta ArticulosMarketplace/ (todos los productos)")
        print("   ❌ Archivo registro_publicaciones.json")
        print("   ❌ Carpeta perfiles/ (sesiones del navegador)")
        print("   ❌ Carpeta backups/")
        print("\n   ✅ Se mantendrá: config_global.txt\n")
        print("=" * 70)

        confirmacion = input("\n¿SEGURO que quieres REINICIAR TODO? (escribe 'SI' en mayúsculas): ")

        if confirmacion == "SI":
            print("\n🗑️  Eliminando datos del sistema...\n")
            eliminados = 0

            for elemento in ["ArticulosMarketplace", "perfiles", "backups"]:
                if os.path.exists(elemento):
                    try:
                        shutil.rmtree(elemento)
                        print(f"  ✔ {elemento}/ eliminado")
                        eliminados += 1
                    except Exception as e:
                        print(f"  ✘ Error eliminando {elemento}/: {e}")

            if os.path.exists("registro_publicaciones.json"):
                try:
                    os.remove("registro_publicaciones.json")
                    print("  ✔ registro_publicaciones.json eliminado")
                    eliminados += 1
                except Exception as e:
                    print(f"  ✘ Error eliminando registro: {e}")

            print(f"\n✅ Sistema reiniciado: {eliminados} elemento(s) eliminado(s)")
        else:
            print("\n❌ Reinicio cancelado")

        input("\nPresiona Enter para continuar...")

    def menu_general(self):
        self.limpiar_pantalla()
        self.mostrar_header()
        print("⚙️  CONFIGURACIÓN GENERAL\n")

        print("📦 Cantidad de productos (carpetas Articulo_X)")
        carpetas_actuales = contar_articulos()
        print(f"   Actual: {self.config['GENERAL']['cantidad_productos']}")
        if carpetas_actuales > 0:
            print(f"   ℹ️  Carpetas existentes: {carpetas_actuales}")

        nuevo_valor = input("   Nuevo valor (Enter para mantener): ").strip()
        if nuevo_valor:
            valido, resultado = self.validar_numero_positivo(nuevo_valor, min_val=1, max_val=50)
            if valido:
                if carpetas_actuales > 0 and resultado < carpetas_actuales:
                    print(f"\n   ⚠️  ADVERTENCIA: Reducirás de {carpetas_actuales} a {resultado} carpetas")
                    confirmar = input("   ¿Continuar? (si/no): ")
                    if confirmar.lower() in ['si', 'sí', 's']:
                        self.config['GENERAL']['cantidad_productos'] = str(resultado)
                        self.cambios_realizados = True
                        print("   ✅ Cambiado")
                    else:
                        print("   ❌ Cancelado")
                else:
                    self.config['GENERAL']['cantidad_productos'] = str(resultado)
                    self.cambios_realizados = True
                    print("   ✅ Cambiado")
            else:
                print(f"   {resultado}")

        print("\n🎯 Modo de operación")
        print(f"   Actual: {self.config['GENERAL']['modo']}")
        print("   Opciones: completo | solo_extraer | solo_publicar")
        nuevo_valor = input("   Nuevo valor (Enter para mantener): ").strip()
        if nuevo_valor:
            valido, resultado = self.validar_modo(nuevo_valor)
            if valido:
                self.config['GENERAL']['modo'] = resultado
                self.cambios_realizados = True
                print("   ✅ Cambiado")
            else:
                print(f"   {resultado}")

        input("\n✅ Presiona Enter para volver...")

    def menu_contenido(self):
        self.limpiar_pantalla()
        self.mostrar_header()
        print("📝 CONFIGURACIÓN DE CONTENIDO (Artículos)\n")
        print("   ℹ️  Los datos de cada artículo se configuran en:")
        print("   ArticulosMarketplace/Articulo_X/datos.txt\n")
        print("   Campos disponibles:")
        print("   • titulo    - Nombre del producto")
        print("   • precio    - Precio en USD")
        print("   • categoria - Categoría de Marketplace")
        print("   • estado    - Nuevo / Usado")
        print("   • descripcion - Descripción del producto")
        print("   • ubicacion - Ciudad/ubicación")
        print("   • etiquetas - Palabras clave")
        print("\n   💡 Próximamente: editor visual de artículos")
        input("\n✅ Presiona Enter para volver...")

    def menu_publicacion(self):
        self.limpiar_pantalla()
        self.mostrar_header()
        print("🚀 CONFIGURACIÓN DE PUBLICACIÓN\n")

        print("🤖 Publicar automáticamente después de extraer")
        print(f"   Actual: {self.config['PUBLICACION']['auto_publicar']}")
        nuevo_valor = input("   Nuevo valor (si/no, Enter para mantener): ").strip()
        if nuevo_valor:
            valido, resultado = self.validar_si_no(nuevo_valor)
            if valido:
                self.config['PUBLICACION']['auto_publicar'] = resultado
                self.cambios_realizados = True
                print("   ✅ Cambiado")
            else:
                print(f"   {resultado}")

        print("\n⏱️  Tiempo entre publicaciones (segundos)")
        print(f"   Actual: {self.config['PUBLICACION']['tiempo_entre_publicaciones']}")
        print("   ℹ️  Recomendado: 10-30 segundos")
        nuevo_valor = input("   Nuevo valor (Enter para mantener): ").strip()
        if nuevo_valor:
            valido, resultado = self.validar_numero_positivo(nuevo_valor, min_val=5, max_val=300)
            if valido:
                if resultado < 10:
                    print("\n   ⚠️  ADVERTENCIA: Menos de 10s puede causar detección de spam")
                    confirmar = input("   ¿Continuar? (si/no): ")
                    if confirmar.lower() in ['si', 'sí', 's']:
                        self.config['PUBLICACION']['tiempo_entre_publicaciones'] = str(resultado)
                        self.cambios_realizados = True
                        print("   ✅ Cambiado")
                    else:
                        print("   ❌ Cancelado")
                else:
                    self.config['PUBLICACION']['tiempo_entre_publicaciones'] = str(resultado)
                    self.cambios_realizados = True
                    print("   ✅ Cambiado")
            else:
                print(f"   {resultado}")

        print("\n📈 Máximo de publicaciones por día")
        print(f"   Actual: {self.config['PUBLICACION']['max_publicaciones_por_dia']}")
        print("   ℹ️  Recomendado: 10-30 (evitar bloqueo)")
        nuevo_valor = input("   Nuevo valor (Enter para mantener): ").strip()
        if nuevo_valor:
            valido, resultado = self.validar_numero_positivo(nuevo_valor, min_val=1, max_val=100)
            if valido:
                if resultado > 50:
                    print("\n   ⚠️  ADVERTENCIA: Más de 50 diarias puede causar bloqueo")
                    confirmar = input("   ¿Continuar? (si/no): ")
                    if confirmar.lower() in ['si', 'sí', 's']:
                        self.config['PUBLICACION']['max_publicaciones_por_dia'] = str(resultado)
                        self.cambios_realizados = True
                        print("   ✅ Cambiado")
                    else:
                        print("   ❌ Cancelado")
                else:
                    self.config['PUBLICACION']['max_publicaciones_por_dia'] = str(resultado)
                    self.cambios_realizados = True
                    print("   ✅ Cambiado")
            else:
                print(f"   {resultado}")

        print("\n📋 Publicar todos los productos disponibles")
        print(f"   Actual: {self.config['PUBLICACION']['publicar_todos']}")
        print("   si = Publica todos | no = Solo publica el siguiente")
        nuevo_valor = input("   Nuevo valor (si/no, Enter para mantener): ").strip()
        if nuevo_valor:
            valido, resultado = self.validar_si_no(nuevo_valor)
            if valido:
                self.config['PUBLICACION']['publicar_todos'] = resultado
                self.cambios_realizados = True
                print("   ✅ Cambiado")
            else:
                print(f"   {resultado}")

        input("\n✅ Presiona Enter para volver...")

    def menu_whatsapp(self):
        self.limpiar_pantalla()
        self.mostrar_header()
        print("📱 CONFIGURACIÓN DE WHATSAPP (Extracción)\n")

        print("👤 Nombre del contacto en WhatsApp")
        print(f"   Actual: {self.config['EXTRACCION']['contacto_whatsapp']}")
        print("   ⚠️  Debe ser EXACTAMENTE igual a como aparece en WhatsApp")
        nuevo_valor = input("   Nuevo valor (Enter para mantener): ").strip()
        if nuevo_valor:
            valido, resultado = self.validar_contacto(nuevo_valor)
            if valido:
                self.config['EXTRACCION']['contacto_whatsapp'] = resultado
                self.cambios_realizados = True
                print("   ✅ Cambiado")
            else:
                print(f"   {resultado}")

        print("\n📜 Auto scroll (veces que hace scroll en catálogo)")
        print(f"   Actual: {self.config['EXTRACCION']['auto_scroll']}")
        nuevo_valor = input("   Nuevo valor (Enter para mantener): ").strip()
        if nuevo_valor:
            valido, resultado = self.validar_numero_positivo(nuevo_valor, min_val=1, max_val=20)
            if valido:
                self.config['EXTRACCION']['auto_scroll'] = str(resultado)
                self.cambios_realizados = True
                print("   ✅ Cambiado")
            else:
                print(f"   {resultado}")

        print("\n📦 Productos por extracción")
        print(f"   Actual: {self.config['EXTRACCION']['productos_por_extraccion']}")
        cantidad_max = int(self.config['GENERAL']['cantidad_productos'])
        print(f"   ℹ️  Máximo recomendado: {cantidad_max} (según cantidad_productos)")
        nuevo_valor = input("   Nuevo valor (Enter para mantener): ").strip()
        if nuevo_valor:
            valido, resultado = self.validar_numero_positivo(nuevo_valor, min_val=1, max_val=50)
            if valido:
                if resultado > cantidad_max:
                    print(f"\n   ⚠️  ADVERTENCIA: Extraerás {resultado} pero solo hay {cantidad_max} carpetas")
                    confirmar = input("   ¿Continuar? (si/no): ")
                    if confirmar.lower() in ['si', 'sí', 's']:
                        self.config['EXTRACCION']['productos_por_extraccion'] = str(resultado)
                        self.cambios_realizados = True
                        print("   ✅ Cambiado")
                    else:
                        print("   ❌ Cancelado")
                else:
                    self.config['EXTRACCION']['productos_por_extraccion'] = str(resultado)
                    self.cambios_realizados = True
                    print("   ✅ Cambiado")
            else:
                print(f"   {resultado}")

        input("\n✅ Presiona Enter para volver...")

    def menu_navegador(self):
        self.limpiar_pantalla()
        self.mostrar_header()
        print("🌐 CONFIGURACIÓN DE NAVEGADOR\n")
        print("   ℹ️  El sistema usa Chrome con tu perfil guardado")
        print("   para mantener la sesión de Facebook activa.\n")
        print("   💡 Si tienes problemas con la sesión:")
        print("   • Cierra Chrome completamente")
        print("   • Ejecuta la app nuevamente")
        print("   • Inicia sesión en Facebook cuando se abra el navegador")
        input("\n✅ Presiona Enter para volver...")

    def menu_seguridad(self):
        self.limpiar_pantalla()
        self.mostrar_header()
        print("🔒 CONFIGURACIÓN DE SEGURIDAD\n")

        print("⏱️  Confirmación antes de borrar carpetas")
        print(f"   Actual: {self.config['SEGURIDAD']['confirmacion_borrado']}")
        print("   si = Countdown de 5-10s | no = Borra inmediatamente")
        nuevo_valor = input("   Nuevo valor (si/no, Enter para mantener): ").strip()
        if nuevo_valor:
            valido, resultado = self.validar_si_no(nuevo_valor)
            if valido:
                self.config['SEGURIDAD']['confirmacion_borrado'] = resultado
                self.cambios_realizados = True
                print("   ✅ Cambiado")
            else:
                print(f"   {resultado}")

        print("\n💾 Crear backup antes de borrar carpetas")
        print(f"   Actual: {self.config['SEGURIDAD']['backup_antes_borrar']}")
        print("   si = Guarda backup en 'backups/' | no = Borra directo")
        nuevo_valor = input("   Nuevo valor (si/no, Enter para mantener): ").strip()
        if nuevo_valor:
            valido, resultado = self.validar_si_no(nuevo_valor)
            if valido:
                self.config['SEGURIDAD']['backup_antes_borrar'] = resultado
                self.cambios_realizados = True
                print("   ✅ Cambiado")
            else:
                print(f"   {resultado}")

        input("\n✅ Presiona Enter para volver...")

    def menu_tareas_automaticas(self):
        self.limpiar_pantalla()
        self.mostrar_header()
        print("🗓️  GESTIÓN DE TAREAS AUTOMÁTICAS\n")
        print("⚠️  Esta función requiere licencia FULL\n")
        print("   Permite crear tareas programadas en Windows para que")
        print("   la aplicación se ejecute automáticamente cada día.\n")
        print("   💡 Próximamente disponible en versión FULL")
        input("\n✅ Presiona Enter para volver...")

    def menu_limites(self):
        """Menú de configuración de límites"""
        self.limpiar_pantalla()
        self.mostrar_header()
        print("🔒 CONFIGURACIÓN DE LÍMITES\n")

        # Tiempo mínimo entre publicaciones
        print("⏱️  Tiempo mínimo entre publicaciones (segundos)")
        print(f"   Actual: {self.config['LIMITES']['tiempo_minimo_entre_publicaciones_segundos']}")
        print("   ℹ️  Recomendado: 120 segundos (2 minutos)")
        nuevo_valor = input("   Nuevo valor (Enter para mantener): ").strip()
        if nuevo_valor:
            valido, resultado = self.validar_numero_positivo(nuevo_valor, min_val=30, max_val=3600)
            if valido:
                self.config['LIMITES']['tiempo_minimo_entre_publicaciones_segundos'] = str(resultado)
                self.cambios_realizados = True
                print("   ✅ Cambiado")
            else:
                print(f"   {resultado}")

        # Permitir duplicados
        print("\n🔄 Permitir publicar mensajes duplicados")
        print(f"   Actual: {self.config['LIMITES']['permitir_duplicados']}")
        print("   si = Puede repetir mensajes | no = Evita repetir")
        nuevo_valor = input("   Nuevo valor (si/no, Enter para mantener): ").strip()
        if nuevo_valor:
            valido, resultado = self.validar_si_no(nuevo_valor)
            if valido:
                self.config['LIMITES']['permitir_duplicados'] = resultado
                self.cambios_realizados = True
                print("   ✅ Cambiado")
            else:
                print(f"   {resultado}")

        # Forzar publicación manual
        print("\n💪 Permitir forzar publicación manual")
        print(f"   Actual: {self.config['LIMITES']['permitir_forzar_publicacion_manual']}")
        print("   si = Permite ignorar límites | no = Respeta siempre los límites")
        nuevo_valor = input("   Nuevo valor (si/no, Enter para mantener): ").strip()
        if nuevo_valor:
            valido, resultado = self.validar_si_no(nuevo_valor)
            if valido:
                self.config['LIMITES']['permitir_forzar_publicacion_manual'] = resultado
                self.cambios_realizados = True
                print("   ✅ Cambiado")
            else:
                print(f"   {resultado}")

        input("\n✅ Presiona Enter para volver al menú principal...")

    def abrir_configurador_grafico(self):
        """Abre el configurador gráfico"""
        print("\n🎨 Abriendo configurador gráfico...")
        try:
            import subprocess
            subprocess.Popen(['python', 'configurador_gui.py'])
            print("✅ Configurador gráfico abierto en nueva ventana")
            input("\nPresiona Enter para continuar...")
        except Exception as e:
            print(f"❌ Error al abrir configurador gráfico: {e}")
            input("\nPresiona Enter para continuar...")

    def abrir_gestor_mensajes(self):
        """Abre el gestor de mensajes"""
        print("\n📄 Abriendo gestor de mensajes...")
        try:
            import subprocess
            subprocess.Popen(['python', 'gestor_mensajes_gui.py'])
            print("✅ Gestor de mensajes abierto en nueva ventana")
            input("\nPresiona Enter para continuar...")
        except Exception as e:
            print(f"❌ Error al abrir gestor de mensajes: {e}")
            input("\nPresiona Enter para continuar...")

    def ejecutar(self):
        try:
            self.cargar_config()
            self.menu_principal()
        except KeyboardInterrupt:
            print("\n\n❌ Configuración cancelada por el usuario")
        except Exception as e:
            print(f"\n❌ Error: {e}")


def main():
    configurador = ConfiguradorInteractivo()
    configurador.ejecutar()


if __name__ == "__main__":
    main()