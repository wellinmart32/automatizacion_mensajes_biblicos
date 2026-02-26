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


def main_solo_predicacion():
    """Publica únicamente la siguiente prédica extraída pendiente"""
    from compartido.gestor_archivos import obtener_siguiente_predicacion, mover_predicacion_a_publicados, escribir_estado_predicaciones
    from publicar_facebook import publicar_con_reintentos

    print("\n" + "="*70)
    print("📤 PUBLICAR PRÉDICA EXTRAÍDA")
    print("="*70)

    ruta, nombre = obtener_siguiente_predicacion()
    if not ruta:
        print("⚠️  No hay prédicas extraídas pendientes.")
        print("   Usa primero 'Extraer Predicaciones de WhatsApp'.")
        pass
        return

    try:
        with open(ruta, 'r', encoding='utf-8') as f:
            url = f.read().strip()
    except Exception as e:
        print(f"❌ Error leyendo prédica: {e}")
        return

    print(f"📄 Prédica: {nombre}")
    print(f"🔗 URL: {url[:80]}...")

    config = leer_config_global()
    gestor = GestorRegistro()

    from publicadores.publicador_facebook import PublicadorFacebook
    print("\n🌐 Iniciando navegador...")
    publicador = PublicadorFacebook(config)
    publicador.iniciar_navegador()

    try:
        exito = publicar_con_reintentos(publicador, url, 'predicacion', config, gestor, nombre)
        if exito:
            gestor.registrar_publicacion_exitosa(nombre, url, len(url), 1, 0, tipo='predicacion')
            mover_predicacion_a_publicados(nombre)
            escribir_estado_predicaciones()
            print(f"\n✅ Prédica publicada: {nombre}")
        else:
            print("\n❌ No se pudo publicar la prédica.")
    finally:
        publicador.cerrar_navegador()


def main():
    """Orquestador maestro - Ejecuta el flujo completo automáticamente"""
    if "--modulo" in sys.argv:
        idx = sys.argv.index("--modulo")
        if idx + 1 < len(sys.argv) and sys.argv[idx + 1] == "publicar_predicaciones":
            main_solo_predicacion()
            return

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
            # Importar y llamar directamente en lugar de subprocess
            from publicar_facebook import main as publicar_main
            publicar_main()
    else:
        print("⛔ Módulo Facebook desactivado - saltando...")

    # MÓDULO 3: Enviar oraciones WhatsApp (si está activo)
    if modulo_oraciones:
        print("\n" + "="*70)
        print("📱 MÓDULO: ENVÍO DE ORACIONES WHATSAPP")
        print("="*70 + "\n")
        from publicadores.whatsapp_oracion import main as oraciones_main
        oraciones_main()
    else:
        print("⛔ Módulo oraciones WhatsApp desactivado - saltando...")

    # Resumen final
    print("\n" + "="*70)
    print("📊 RESUMEN FINAL")
    print("="*70)
    gestor_final = GestorRegistro()
    gestor_final.mostrar_estadisticas()

    cerrar_con_exito()


def _verificar_wizard_completado():
    """Si no hay licencia configurada, lanza el wizard y termina"""
    import subprocess
    from gestor_licencias import GestorLicencias
    gestor = GestorLicencias("MensajesBiblicos")
    if not os.path.exists(gestor.archivo_config):
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
            wizard = os.path.join(base_dir, "WizardMensajes.exe")
        else:
            wizard = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wizard_primera_vez.py")

        if os.path.exists(wizard):
            subprocess.Popen([wizard])
        else:
            print("⚠️  Ejecuta WizardMensajes.exe para configurar el sistema.")
        return False
    return True


if __name__ == "__main__":
    if not _verificar_wizard_completado():
        sys.exit(0)
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Proceso cancelado por el usuario\n")
        sys.exit(0)
    except Exception as e:
        import traceback
        cerrar_con_error(f"Error inesperado: {e}\n\n{traceback.format_exc()}")