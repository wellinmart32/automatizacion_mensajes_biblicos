import sys
import time
import os
from datetime import datetime
from compartido.gestor_archivos import (
    leer_config_global,
    verificar_y_crear_estructura,
    obtener_mensaje_aleatorio_sin_repetir,
    obtener_mensaje_secuencial,
    contar_predicaciones_pendientes,
    contar_predicaciones_publicadas,
    obtener_siguiente_predicacion,
    mover_predicacion_a_publicados
)
from publicadores.publicador_facebook import PublicadorFacebook
from gestor_registro import GestorRegistro
from gestor_licencias import GestorLicencias
from dialogos_licencia import DialogosLicencia


def verificar_licencia_inicio():
    """Verificar licencia al iniciar la aplicación"""
    gestor_lic = GestorLicencias("MensajesBiblicos")
    resultado = gestor_lic.verificar_e_iniciar()
    
    # Primera vez - solicitar código
    if resultado.get('necesita_ingreso'):
        codigo = DialogosLicencia.solicitar_codigo_licencia()
        
        if not codigo:
            DialogosLicencia.mostrar_error("Necesitas un código de licencia para usar la aplicación")
            return None
        
        # Guardar y verificar
        gestor_lic.guardar_codigo_licencia(codigo)
        resultado = gestor_lic.verificar_e_iniciar()
    
    # Error en verificación
    if resultado.get('error'):
        DialogosLicencia.mostrar_error(resultado.get('mensaje'))
        return None
    
    # Trial expirado
    if resultado.get('expirado'):
        DialogosLicencia.mostrar_trial_expirado(resultado.get('codigo'))
        return None
    
    # Trial activo
    if resultado.get('tipo') == 'TRIAL':
        dias = resultado.get('dias_restantes')
        print(f"\n⚠️  MODO TRIAL - Quedan {dias} días\n")
    
    # Full - mostrar mensaje de bienvenida
    if resultado.get('tipo') == 'FULL':
        print("\n✅ Licencia completa activada - Todas las funciones desbloqueadas\n")
    
    return resultado


def mostrar_banner():
    """Muestra el banner inicial"""
    print("\n" + "="*70)
    print(" " * 15 + "🚀 PUBLICADOR AUTOMÁTICO DE FACEBOOK")
    print(" " * 20 + "Sistema de Mensajes Bíblicos")
    print("="*70 + "\n")


def mostrar_configuracion(config):
    """Muestra la configuración actual"""
    print("📁 Verificando estructura...")
    verificar_y_crear_estructura()
    print()
    
    print("⚙️  CONFIGURACIÓN DEL SISTEMA:")
    print(f"   📁 Carpeta mensajes: {config['carpeta_mensajes']}")
    print(f"   🌐 Navegador: {config['navegador'].upper()}")
    print(f"   🎲 Selección: {config['seleccion'].capitalize()}")
    print(f"   💾 Memoria: Últimos {config['historial_evitar_repetir']} mensajes")
    print(f"   🔄 Máx. intentos: {config.get('max_intentos', 3)}")
    
    if config.get('activar_predicaciones'):
        print(f"   🎬 Predicaciones: ACTIVADAS")
        print(f"   📱 Grupo WhatsApp: {config['nombre_grupo_whatsapp']}")
    
    print()


def obtener_contenido_publicacion(gestor, config):
    """Obtiene el contenido a publicar según configuración"""
    if config['seleccion'] in ('aleatorio', 'aleatoria'):
        contenido, nombre_archivo = obtener_mensaje_aleatorio_sin_repetir(gestor.registro)
    else:
        contenido, nombre_archivo = obtener_mensaje_secuencial(gestor.registro)
    
    return (contenido, nombre_archivo), 'biblico'


def publicar_con_reintentos(publicador, contenido, tipo_publicacion, config, gestor, nombre_archivo=None):
    """Intenta publicar con reintentos configurables"""
    max_intentos = config.get('max_intentos', 3)
    tiempo_entre_intentos = config.get('tiempo_entre_intentos', 10)
    
    for intento in range(1, max_intentos + 1):
        try:
            print(f"\n{'='*70}")
            print(f"🔄 INTENTO {intento} DE {max_intentos}")
            print(f"{'='*70}\n")
            
            exito = publicador.publicar_completo(contenido)
            
            if exito:
                print(f"✅ Publicación exitosa en intento {intento}")
                return True
            else:
                print(f"⚠️  Intento {intento} falló")
                if intento < max_intentos:
                    print(f"⏳ Esperando {tiempo_entre_intentos}s antes de reintentar...")
                    time.sleep(tiempo_entre_intentos)
        
        except Exception as e:
            print(f"❌ Error en intento {intento}: {e}")
            if intento < max_intentos:
                print(f"⏳ Esperando {tiempo_entre_intentos}s antes de reintentar...")
                time.sleep(tiempo_entre_intentos)
            else:
                import traceback
                traceback.print_exc()
    
    return False


def main():
    """Función principal del publicador"""
    
    # VERIFICAR LICENCIA PRIMERO
    estado_licencia = verificar_licencia_inicio()
    
    if not estado_licencia:
        print("\n❌ No se pudo verificar la licencia. Cerrando aplicación...")
        return
    
    # Mostrar banner
    mostrar_banner()
    
    # Cargar configuración
    try:
        config = leer_config_global()
    except Exception as e:
        print(f"❌ Error leyendo configuración: {e}")
        return
    
    # Mostrar configuración
    mostrar_configuracion(config)
    
    # Inicializar gestor de registro
    gestor = GestorRegistro()
    
    # Mostrar estadísticas
    gestor.mostrar_estadisticas()
    
    # Mostrar historial reciente
    gestor.mostrar_historial_reciente(5)
    
    # Verificar límite diario
    if not gestor.puede_publicar_ahora(config.get('max_publicaciones_por_dia', 20)):
        print(f"\n⚠️  Ya se alcanzó el límite de {config.get('max_publicaciones_por_dia', 20)} publicaciones hoy")
        print("   Intenta mañana o aumenta el límite en config_global.txt")
        return
    
    # Obtener contenido a publicar
    contenido_data, tipo_pub = obtener_contenido_publicacion(gestor, config)
    
    if tipo_pub == 'predicacion':
        ruta_video, titulo = contenido_data
        if not ruta_video:
            print("❌ No hay predicaciones pendientes")
            return
        print(f"\n📹 Publicando predicación: {titulo}")
        contenido = ruta_video
        nombre_archivo = titulo
    else:
        contenido, nombre_archivo = contenido_data
        if not contenido:
            print("❌ No hay mensajes disponibles")
            return
        print(f"\n📖 Mensaje seleccionado: {nombre_archivo}")
    
    # Inicializar publicador
    print("\n🌐 Inicializando navegador...")
    publicador = PublicadorFacebook(config)
    publicador.iniciar_navegador()
    
    try:
        # Publicar con reintentos
        exito = publicar_con_reintentos(
            publicador,
            contenido,
            tipo_pub,
            config,
            gestor,
            nombre_archivo
        )
        
        if exito:
            # Registrar publicación
            if tipo_pub == 'predicacion':
                gestor.registrar_publicacion_exitosa(nombre_archivo, '', 0, 1, 0, tipo='predicacion')
                mover_predicacion_a_publicados(nombre_archivo)
            else:
                gestor.registrar_publicacion_exitosa(nombre_archivo, '', 0, 1, 0, tipo='biblico')
            
            print("\n" + "="*70)
            print("✅ PUBLICACIÓN COMPLETADA EXITOSAMENTE")
            print("="*70)
        else:
            print("\n" + "="*70)
            print("❌ NO SE PUDO COMPLETAR LA PUBLICACIÓN")
            print("="*70)
            gestor.registrar_error(nombre_archivo, tipo_pub, "Falló después de todos los intentos")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Publicación cancelada por el usuario")
        gestor.registrar_error(nombre_archivo, tipo_pub, "Cancelado por usuario")
    
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        gestor.registrar_error(nombre_archivo, tipo_pub, str(e))
    
    finally:
        publicador.cerrar_navegador()


def _verificar_wizard_completado():
    """Si no hay licencia configurada, lanza el wizard y termina"""
    import subprocess
    gestor = GestorLicencias("MensajesBiblicos")
    if not os.path.exists(gestor.archivo_config):
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
            wizard = os.path.join(base_dir, "WizardMensajes.exe")
            if os.path.exists(wizard):
                # Ocultar consola y lanzar wizard directamente
                import ctypes
                ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
                subprocess.Popen([wizard])
        else:
            wizard = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wizard_primera_vez.py")
            if os.path.exists(wizard):
                subprocess.Popen([wizard])
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
        print(f"\n❌ Error inesperado: {e}")
        traceback.print_exc()