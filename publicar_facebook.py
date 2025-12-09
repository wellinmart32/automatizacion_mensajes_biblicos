import time
import sys
from datetime import datetime
from compartido.gestor_archivos import (
    leer_config_global,
    verificar_estructura_carpetas,
    obtener_mensaje_aleatorio_sin_repetir,
    obtener_mensaje_secuencial,
    obtener_estadisticas_mensajes
)
from publicadores.publicador_facebook import PublicadorFacebook
from gestor_registro import GestorRegistro


def mostrar_banner():
    """Muestra el banner inicial del sistema"""
    print("\n" + "="*70)
    print(" " * 15 + "🚀 PUBLICADOR AUTOMÁTICO DE FACEBOOK")
    print(" " * 20 + "Sistema de Mensajes Bíblicos")
    print("="*70 + "\n")


def mostrar_informacion_sistema(config, gestor):
    """Muestra información del sistema antes de ejecutar"""
    print("⚙️  CONFIGURACIÓN DEL SISTEMA:")
    print(f"   📁 Carpeta mensajes: {config['carpeta_mensajes']}")
    print(f"   🌐 Navegador: {config['navegador'].upper()}")
    print(f"   🎲 Selección: {config['seleccion'].capitalize()}")
    print(f"   💾 Memoria: Últimos {config['historial_evitar_repetir']} mensajes")
    print(f"   🔄 Máx. intentos: {config['max_intentos_por_publicacion']}")
    print(f"   🐛 Modo debug: {config['modo_debug'].capitalize()}")
    
    # Mostrar estadísticas de mensajes
    stats_mensajes = obtener_estadisticas_mensajes()
    print(f"\n📊 MENSAJES DISPONIBLES:")
    print(f"   Total: {stats_mensajes['total_mensajes']} archivos")
    
    if stats_mensajes['total_mensajes'] == 0:
        print(f"   ⚠️  No hay mensajes en: {config['carpeta_mensajes']}/")
        print(f"   Por favor, agrega archivos .txt antes de publicar")
        return False
    
    # Mostrar estadísticas del sistema
    gestor.mostrar_estadisticas()
    
    # Mostrar historial reciente (mensajes bloqueados)
    gestor.mostrar_historial_reciente(config['historial_evitar_repetir'])
    
    return True


def verificar_tiempo_minimo(gestor, config, es_ejecucion_manual=False):
    """
    Verifica si se puede publicar según el tiempo mínimo
    
    Args:
        gestor: Instancia de GestorRegistro
        config: Configuración del sistema
        es_ejecucion_manual: True si es clic manual, False si es tarea programada
        
    Returns:
        bool: True si puede publicar
    """
    tiempo_minimo = config['tiempo_minimo_entre_publicaciones_segundos']
    permitir_forzar = config['permitir_forzar_publicacion_manual'] and es_ejecucion_manual
    
    puede, mensaje = gestor.puede_publicar_ahora(tiempo_minimo, permitir_forzar)
    
    if not puede:
        print(f"\n⏳ VERIFICACIÓN DE TIEMPO:")
        print(f"   {mensaje}")
        print(f"   Tiempo mínimo configurado: {tiempo_minimo}s")
        print("\n💡 Esto evita publicaciones duplicadas si se ejecutan 2 tareas al mismo tiempo")
        return False
    
    if permitir_forzar and "forzado" in mensaje.lower():
        print(f"\n⚠️  PUBLICACIÓN MANUAL FORZADA:")
        print(f"   {mensaje}")
        print(f"   Se permite por ser ejecución manual\n")
    
    return True


def obtener_mensaje_segun_config(config, gestor):
    """
    Obtiene un mensaje según la configuración (aleatorio o secuencial)
    
    Args:
        config: Configuración del sistema
        gestor: Instancia de GestorRegistro
        
    Returns:
        tuple: (contenido, nombre_archivo) o (None, None) si falla
    """
    print("\n🎯 SELECCIÓN DE MENSAJE:\n")
    
    if config['seleccion'] == 'aleatoria':
        print("   Método: Aleatorio (evitando últimos publicados)")
        return obtener_mensaje_aleatorio_sin_repetir(gestor.registro)
    elif config['seleccion'] == 'secuencial':
        print("   Método: Secuencial (en orden)")
        return obtener_mensaje_secuencial(gestor.registro)
    else:
        print(f"   ⚠️  Método desconocido: {config['seleccion']}")
        print("   Usando método aleatorio por defecto...")
        return obtener_mensaje_aleatorio_sin_repetir(gestor.registro)


def publicar_con_reintentos(mensaje, nombre_archivo, config, publicador, gestor):
    """
    Intenta publicar un mensaje con reintentos
    
    Args:
        mensaje: Contenido del mensaje
        nombre_archivo: Nombre del archivo del mensaje
        config: Configuración del sistema
        publicador: Instancia de PublicadorFacebook
        gestor: Instancia de GestorRegistro
        
    Returns:
        bool: True si la publicación fue exitosa
    """
    max_intentos = config['max_intentos_por_publicacion']
    tiempo_entre_intentos = config['tiempo_entre_intentos']
    
    print("\n" + "="*70)
    print(f"📤 INICIANDO PUBLICACIÓN")
    print("="*70)
    print(f"📄 Archivo: {nombre_archivo}")
    print(f"📝 Longitud: {len(mensaje)} caracteres")
    print(f"🔄 Máximo de intentos: {max_intentos}")
    print("="*70 + "\n")
    
    tiempo_inicio = time.time()
    
    for intento in range(1, max_intentos + 1):
        print(f"\n{'='*70}")
        print(f"🎯 INTENTO {intento}/{max_intentos}")
        print(f"{'='*70}\n")
        
        try:
            # Intentar publicar
            exito = publicador.publicar_completo(mensaje)
            
            if exito:
                # Calcular tiempo de ejecución
                tiempo_ejecucion = round(time.time() - tiempo_inicio, 2)
                
                # Registrar éxito
                gestor.registrar_publicacion_exitosa(
                    mensaje_archivo=nombre_archivo,
                    contenido=mensaje,
                    longitud=len(mensaje),
                    intentos=intento,
                    tiempo_ejecucion=tiempo_ejecucion
                )
                
                print("\n" + "="*70)
                print("✅ ¡PUBLICACIÓN EXITOSA!")
                print("="*70)
                print(f"📄 Mensaje: {nombre_archivo}")
                print(f"🔄 Intentos: {intento}")
                print(f"⏱️  Tiempo: {tiempo_ejecucion}s")
                print("="*70 + "\n")
                
                return True
            
            else:
                print(f"\n⚠️  Intento {intento} falló")
                
                if intento < max_intentos:
                    print(f"⏳ Esperando {tiempo_entre_intentos}s antes de reintentar...")
                    time.sleep(tiempo_entre_intentos)
                else:
                    print(f"\n❌ Se agotaron los {max_intentos} intentos")
        
        except Exception as e:
            print(f"\n❌ Error en intento {intento}: {e}")
            
            if config['modo_debug']:
                import traceback
                traceback.print_exc()
            
            if intento < max_intentos:
                print(f"⏳ Esperando {tiempo_entre_intentos}s antes de reintentar...")
                time.sleep(tiempo_entre_intentos)
    
    # Registrar error después de agotar intentos
    tiempo_ejecucion = round(time.time() - tiempo_inicio, 2)
    
    gestor.registrar_error(
        mensaje_archivo=nombre_archivo,
        error=f"Falló después de {max_intentos} intentos"
    )
    
    return False


def main():
    """Función principal que orquesta todo el sistema"""
    
    # Mostrar banner
    mostrar_banner()
    
    # Cargar configuración
    try:
        config = leer_config_global()
    except Exception as e:
        print(f"❌ Error cargando configuración: {e}")
        print("\n💡 Asegúrate de que existe config_global.txt en la carpeta del proyecto")
        input("\nPresiona Enter para salir...")
        return
    
    # Verificar y crear estructura de carpetas
    print("📁 Verificando estructura de carpetas...")
    verificar_estructura_carpetas()
    print()
    
    # Inicializar gestor de registro
    gestor = GestorRegistro()
    
    # Mostrar información del sistema
    if not mostrar_informacion_sistema(config, gestor):
        input("\nPresiona Enter para salir...")
        return
    
    # Detectar si es ejecución manual o automática
    # Si se ejecuta desde consola interactiva, es manual
    es_ejecucion_manual = sys.stdin.isatty()
    
    if es_ejecucion_manual:
        print("🖱️  Ejecución MANUAL detectada (clic en acceso directo)")
    else:
        print("⏰ Ejecución AUTOMÁTICA detectada (tarea programada)")
    
    # Verificar tiempo mínimo entre publicaciones
    if not verificar_tiempo_minimo(gestor, config, es_ejecucion_manual):
        print("\n⏸️  Publicación cancelada por tiempo mínimo\n")
        input("Presiona Enter para salir...")
        return
    
    # Obtener mensaje según configuración
    mensaje, nombre_archivo = obtener_mensaje_segun_config(config, gestor)
    
    if not mensaje or not nombre_archivo:
        print("\n❌ No se pudo obtener un mensaje para publicar")
        input("\nPresiona Enter para salir...")
        return
    
    # Mostrar preview del mensaje
    print(f"\n📄 PREVIEW DEL MENSAJE:")
    print("-" * 70)
    preview = mensaje[:200] + "..." if len(mensaje) > 200 else mensaje
    print(preview)
    print("-" * 70 + "\n")
    
    # Countdown antes de iniciar (solo en modo manual)
    if es_ejecucion_manual and config['modo_debug'] == 'detallado':
        print("⏳ Iniciando en 3 segundos... (Presiona Ctrl+C para cancelar)\n")
        try:
            for i in range(3, 0, -1):
                print(f"   {i}...", end='\r', flush=True)
                sys.stdout.flush()
                time.sleep(1)
            print("   ✅ ¡Iniciando!\n")
        except KeyboardInterrupt:
            print("\n\n❌ Cancelado por el usuario\n")
            return
    
    # Inicializar publicador
    publicador = PublicadorFacebook(config)
    
    try:
        # Iniciar navegador
        publicador.iniciar_navegador()
        
        # Publicar con reintentos
        exito = publicar_con_reintentos(
            mensaje=mensaje,
            nombre_archivo=nombre_archivo,
            config=config,
            publicador=publicador,
            gestor=gestor
        )
        
        # Mostrar estadísticas actualizadas
        if exito:
            print("\n📊 ESTADÍSTICAS ACTUALIZADAS:")
            gestor.mostrar_estadisticas()
        
        # Resumen final
        print("\n" + "="*70)
        if exito:
            print("✅ PROCESO COMPLETADO EXITOSAMENTE")
        else:
            print("❌ PROCESO FINALIZADO CON ERRORES")
        print("="*70)
        
        if exito:
            print("\n💡 Próxima publicación:")
            if config['seleccion'] == 'aleatoria':
                print(f"   Se seleccionará aleatoriamente evitando últimos {config['historial_evitar_repetir']}")
            else:
                print("   Se publicará el siguiente mensaje en orden")
        
        print()
        
    except KeyboardInterrupt:
        print("\n\n❌ Proceso cancelado por el usuario")
    
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        
        if config['modo_debug']:
            import traceback
            traceback.print_exc()
    
    finally:
        # Cerrar navegador
        publicador.cerrar_navegador()
        
        # Pausa final (solo en modo manual)
        if es_ejecucion_manual:
            print("\n⏳ El navegador se cerrará en 2 segundos...")
            time.sleep(2)


if __name__ == "__main__":
    main()
