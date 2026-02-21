import os
import subprocess
import sys
import time
from compartido.gestor_archivos import (
    leer_config_global,
    verificar_y_crear_estructura,
    contar_predicaciones_pendientes
)
from gestor_registro import GestorRegistro


def ejecutar_script(script_name, descripcion, modo_auto=True):
    """Ejecuta un script sin abrir ventanas de consola adicionales"""
    print(f"\n{'='*70}")
    print(f"🚀 {descripcion}")
    print(f"{'='*70}\n")

    try:
        comando = [sys.executable, script_name]
        if modo_auto:
            comando.append('--auto')

        # Evitar ventanas de consola adicionales en Windows
        flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0

        resultado = subprocess.run(
            comando,
            capture_output=False,
            text=True,
            creationflags=flags
        )

        if resultado.returncode == 0:
            print(f"\n✅ {descripcion} - Completado")
            return True
        else:
            print(f"\n⚠️  {descripcion} - Finalizado con advertencias")
            return False

    except Exception as e:
        print(f"\n❌ Error ejecutando {script_name}: {e}")
        return False


def cerrar_con_exito():
    """Cierra la consola automáticamente con countdown"""
    print("\n" + "="*70)
    print("✅ PROCESO COMPLETADO EXITOSAMENTE")
    print("="*70)
    for i in range(5, 0, -1):
        print(f"   Cerrando en {i} segundos...", end='\r', flush=True)
        time.sleep(1)
    print()


def cerrar_con_error(mensaje):
    """Muestra el error y espera confirmación del usuario"""
    print("\n" + "="*70)
    print("❌ SE PRODUJO UN ERROR")
    print("="*70)
    print(f"\n{mensaje}\n")
    input("Presiona Enter para cerrar...")


def main():
    """Orquestador maestro - Ejecuta el flujo completo automáticamente"""

    print("\n" + "="*70)
    print(" " * 10 + "🎯 PUBLICADOR AUTOMÁTICO - FLUJO COMPLETO")
    print(" " * 12 + "Mensajes Bíblicos + WhatsApp")
    print("="*70 + "\n")

    # Leer configuración
    try:
        config = leer_config_global()
    except Exception as e:
        cerrar_con_error(f"Error leyendo configuración: {e}\nEjecuta el Wizard para reconfigurar.")
        return

    # Verificar estructura
    print("📁 Verificando estructura de carpetas...")
    verificar_y_crear_estructura()
    print()

    # Inicializar gestor de registro
    gestor = GestorRegistro()

    # Mostrar módulos activos
    modulo_facebook     = config.get('modulo_facebook', True)
    modulo_oraciones    = config.get('modulo_oraciones', False)
    modulo_predicaciones = config.get('modulo_predicaciones', False)

    print("⚙️  MÓDULOS ACTIVOS:\n")
    print(f"   📘 Publicar en Facebook:        {'✅ Sí' if modulo_facebook else '⛔ No'}")
    print(f"   📱 Enviar oraciones WhatsApp:   {'✅ Sí' if modulo_oraciones else '⛔ No'}")
    print(f"   🎬 Extraer predicaciones:        {'✅ Sí' if modulo_predicaciones else '⛔ No'}")
    print()

    # Mostrar estadísticas
    gestor.mostrar_estadisticas()

    # Countdown automático
    print("\n⏳ Iniciando automáticamente en 5 segundos...")
    print("   (Presiona Ctrl+C para cancelar)\n")
    try:
        for i in range(5, 0, -1):
            print(f"   {i}...", end='\r', flush=True)
            sys.stdout.flush()
            time.sleep(1)
        print("   ✅ ¡Iniciando!\n")
    except KeyboardInterrupt:
        print("\n\n❌ Proceso cancelado por el usuario\n")
        sys.exit(0)

    # MÓDULO 1: Extraer predicaciones (si está activo)
    if modulo_predicaciones and config.get('activar_predicaciones', False):
        pendientes = contar_predicaciones_pendientes()
        if pendientes < 5:
            print("\n" + "="*70)
            print("📱 MÓDULO: EXTRACCIÓN DE PREDICACIONES DE WHATSAPP")
            print("="*70 + "\n")
            ejecutar_script("extraer_predicaciones_whatsapp.py", "Extracción de Predicaciones")

    # MÓDULO 2: Publicar en Facebook (si está activo)
    if modulo_facebook:
        print("\n" + "="*70)
        print("📘 MÓDULO: PUBLICACIÓN EN FACEBOOK")
        print("="*70 + "\n")

        tiempo_minimo = config['tiempo_minimo_entre_publicaciones_segundos']
        puede_publicar, mensaje = gestor.puede_publicar_ahora(tiempo_minimo, False)

        if not puede_publicar:
            print(f"⏸️  NO SE PUEDE PUBLICAR AHORA: {mensaje}")
        else:
            ejecutar_script("publicar_facebook.py", "Publicación en Facebook")
    else:
        print("⛔ Módulo Facebook desactivado - saltando...")

    # MÓDULO 3: Enviar oraciones WhatsApp (si está activo)
    if modulo_oraciones:
        print("\n" + "="*70)
        print("📱 MÓDULO: ENVÍO DE ORACIONES WHATSAPP")
        print("="*70 + "\n")
        ejecutar_script("publicadores/whatsapp_oracion.py", "Envío de Oraciones WhatsApp", modo_auto=False)
    else:
        print("⛔ Módulo oraciones WhatsApp desactivado - saltando...")

    # Resumen final
    print("\n" + "="*70)
    print("📊 RESUMEN FINAL")
    print("="*70)
    gestor_final = GestorRegistro()
    gestor_final.mostrar_estadisticas()

    cerrar_con_exito()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Proceso cancelado por el usuario\n")
        sys.exit(0)
    except Exception as e:
        import traceback
        cerrar_con_error(f"Error inesperado: {e}\n\n{traceback.format_exc()}")