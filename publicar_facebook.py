import sys
import time
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
    print(f"   🔄 Máx. intentos: {config['max_intentos_por_publicacion']}")
    
    # Info de mensajes bíblicos
    from compartido.gestor_archivos import obtener_estadisticas_mensajes
    stats_mensajes = obtener_estadisticas_mensajes()
    
    print(f"\n📊 MENSAJES BÍBLICOS:")
    print(f"   Total: {stats_mensajes['total_mensajes']} archivos")
    
    # Info de predicaciones
    if config.get('activar_predicaciones', False):
        pendientes = contar_predicaciones_pendientes()
        publicadas = contar_predicaciones_publicadas()
        
        print(f"\n🎬 PREDICACIONES:")
        print(f"   Pendientes: {pendientes}")
        print(f"   Publicadas: {publicadas}")
        print(f"   Alternancia: {'ACTIVADA ✅' if config.get('alternar_con_predicaciones') else 'DESACTIVADA'}")
        print(f"   Tiempo espera preview: {config.get('tiempo_espera_previsualizacion', 12)}s")


def decidir_tipo_publicacion(gestor, config):
    """
    Decide si publicar mensaje bíblico o predicación según alternancia 1:1
    
    Returns:
        str: 'biblico' o 'predicacion'
    """
    if not config.get('activar_predicaciones', False):
        return 'biblico'
    
    if not config.get('alternar_con_predicaciones', False):
        return 'biblico'
    
    # Verificar si hay predicaciones pendientes
    pendientes = contar_predicaciones_pendientes()
    if pendientes == 0:
        print("⚠️  No hay predicaciones pendientes, publicando mensaje bíblico")
        return 'biblico'
    
    # Verificar última publicación
    historial = gestor.registro.get('historial_completo', [])
    
    if not historial:
        # Primera publicación, empezar con mensaje bíblico
        return 'biblico'
    
    # Obtener tipo de la última publicación
    ultima = historial[-1]
    ultimo_tipo = ultima.get('tipo', 'biblico')
    
    # Alternar: si último fue bíblico → predicación, si fue predicación → bíblico
    if ultimo_tipo == 'biblico':
        return 'predicacion'
    else:
        return 'biblico'


def preparar_contenido_biblico(config, gestor):
    """
    Prepara el contenido de un mensaje bíblico
    
    Returns:
        tuple: (contenido, nombre_archivo) o (None, None)
    """
    print("\n🎯 SELECCIÓN DE MENSAJE:")
    print(f"   Método: {config['seleccion'].capitalize()} (evitando últimos publicados)")
    
    if config['seleccion'] == 'aleatoria':
        contenido, nombre_archivo = obtener_mensaje_aleatorio_sin_repetir(gestor.registro)
    else:
        contenido, nombre_archivo = obtener_mensaje_secuencial(gestor.registro)
    
    if not contenido:
        print("❌ No se pudo obtener mensaje bíblico")
        return None, None
    
    return contenido, nombre_archivo


def preparar_contenido_predicacion(config):
    """
    Prepara el contenido de una predicación
    
    Returns:
        tuple: (contenido_completo, nombre_archivo, enlace_original) o (None, None, None)
    """
    print("\n🎯 SELECCIÓN DE PREDICACIÓN:")
    
    ruta_archivo, nombre_archivo = obtener_siguiente_predicacion()
    
    if not ruta_archivo:
        print("❌ No hay predicaciones pendientes")
        return None, None, None
    
    print(f"   Archivo: {nombre_archivo}")
    
    # Leer el contenido del archivo
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            contenido = f.read().strip()
        
        # El contenido puede ser un enlace directo o [IMAGEN]
        if contenido.startswith('[IMAGEN]'):
            print("⚠️  Predicación tipo imagen - No soportado aún")
            return None, None, None
        
        # Es un enlace
        enlace = contenido
        
        # Construir contenido completo con introducción y hashtags
        texto_completo = ""
        
        # Agregar introducción
        if config.get('agregar_introduccion_predica', True):
            intro = config.get('texto_introduccion_predica', '🎬 Predicación recomendada:\n\n')
            texto_completo += intro
            # Asegurar salto de línea después de introducción
            if not intro.endswith('\n\n'):
                texto_completo += '\n\n'
        
        # Agregar enlace
        texto_completo += enlace
        
        # Agregar hashtags
        if config.get('agregar_hashtags_predicaciones', True):
            hashtags = config.get('hashtags_predicaciones', '#Predicación,#Fe,#Cristiano')
            texto_completo += f"\n\n{hashtags}"
        
        return texto_completo, nombre_archivo, enlace
        
    except Exception as e:
        print(f"❌ Error leyendo predicación: {e}")
        return None, None, None


def publicar_contenido(publicador, contenido, tipo, config):
    """
    Publica el contenido usando el publicador correcto
    
    Args:
        publicador: Instancia de PublicadorFacebook
        contenido: Texto completo a publicar
        tipo: 'biblico' o 'predicacion'
        config: Configuración del sistema
        
    Returns:
        bool: True si se publicó exitosamente
    """
    max_intentos = config['max_intentos_por_publicacion']
    tiempo_entre_intentos = config['tiempo_entre_intentos']
    
    for intento in range(1, max_intentos + 1):
        print(f"\n{'='*70}")
        print(f"🎯 INTENTO {intento}/{max_intentos}")
        print(f"{'='*70}\n")
        
        try:
            # PASO 1: Verificar sesión de Facebook
            if not publicador.verificar_sesion_facebook():
                print("❌ No se pudo verificar sesión de Facebook")
                if intento < max_intentos:
                    print(f"⏳ Esperando {tiempo_entre_intentos}s antes de reintentar...")
                    time.sleep(tiempo_entre_intentos)
                    continue
                return False
            
            # PASO 2: Abrir compositor
            if not publicador.abrir_compositor():
                print("❌ No se pudo abrir el compositor")
                if intento < max_intentos:
                    print(f"⏳ Esperando {tiempo_entre_intentos}s antes de reintentar...")
                    time.sleep(tiempo_entre_intentos)
                    continue
                return False
            
            # PASO 3: Publicar según tipo
            if tipo == 'predicacion':
                # Detectar si es enlace
                es_enlace = any(plat in contenido.lower() for plat in ['http', 'youtube', 'instagram', 'facebook', 'tiktok'])
                
                if es_enlace and config.get('usar_estrategia_optimizada_enlaces', True):
                    # Separar introducción, enlace y hashtags
                    lineas = contenido.split('\n')
                    enlace = None
                    intro_lineas = []
                    hashtags_lineas = []
                    
                    encontro_enlace = False
                    for linea in lineas:
                        if any(plat in linea.lower() for plat in ['http', 'youtube', 'instagram', 'facebook', 'tiktok']):
                            enlace = linea.strip()
                            encontro_enlace = True
                        elif not encontro_enlace:
                            intro_lineas.append(linea)
                        else:
                            hashtags_lineas.append(linea)
                    
                    intro = '\n'.join(intro_lineas).strip()
                    hashtags = '\n'.join(hashtags_lineas).strip()
                    
                    # Usar método optimizado para enlaces
                    if not publicador.publicar_enlace_con_preview_optimizado(enlace if enlace else contenido, intro, hashtags):
                        print(f"⚠️  Intento {intento} falló")
                        if intento < max_intentos:
                            print(f"⏳ Esperando {tiempo_entre_intentos}s antes de reintentar...")
                            time.sleep(tiempo_entre_intentos)
                            continue
                        return False
                else:
                    # Texto normal
                    if not publicador.ingresar_texto(contenido):
                        print(f"⚠️  Intento {intento} falló al ingresar texto")
                        if intento < max_intentos:
                            print(f"⏳ Esperando {tiempo_entre_intentos}s antes de reintentar...")
                            time.sleep(tiempo_entre_intentos)
                            continue
                        return False
                    
                    if not publicador.publicar_mensaje():
                        print(f"⚠️  Intento {intento} falló al publicar")
                        if intento < max_intentos:
                            print(f"⏳ Esperando {tiempo_entre_intentos}s antes de reintentar...")
                            time.sleep(tiempo_entre_intentos)
                            continue
                        return False
            else:
                # Mensaje bíblico - método tradicional
                if not publicador.ingresar_texto(contenido):
                    print(f"⚠️  Intento {intento} falló al ingresar texto")
                    if intento < max_intentos:
                        print(f"⏳ Esperando {tiempo_entre_intentos}s antes de reintentar...")
                        time.sleep(tiempo_entre_intentos)
                        continue
                    return False
                
                if not publicador.publicar_mensaje():
                    print(f"⚠️  Intento {intento} falló al publicar")
                    if intento < max_intentos:
                        print(f"⏳ Esperando {tiempo_entre_intentos}s antes de reintentar...")
                        time.sleep(tiempo_entre_intentos)
                        continue
                    return False
            
            # PASO 4: Verificar éxito
            publicador.verificar_publicacion_exitosa()
            
            print(f"✅ Publicación exitosa en intento {intento}")
            return True
            
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
    
    # Mostrar banner
    mostrar_banner()
    
    # Cargar configuración
    try:
        config = leer_config_global()
    except Exception as e:
        print(f"❌ Error leyendo configuración: {e}")
        input("\nPresiona Enter para salir...")
        return
    
    # Mostrar configuración
    mostrar_configuracion(config)
    
    # Inicializar gestor de registro
    gestor = GestorRegistro()
    
    # Mostrar estadísticas
    gestor.mostrar_estadisticas()
    
    # Mostrar historial bloqueado (memoria)
    gestor.mostrar_historial_reciente(config['historial_evitar_repetir'])
    
    # Verificar límite de tiempo
    tiempo_minimo = config['tiempo_minimo_entre_publicaciones_segundos']
    es_manual = True  # Ejecución manual desde este script
    
    puede_publicar, mensaje_limite = gestor.puede_publicar_ahora(
        tiempo_minimo, 
        config['permitir_forzar_publicacion_manual'] and es_manual
    )
    
    if not puede_publicar:
        print(f"\n⏸️  NO SE PUEDE PUBLICAR AHORA:")
        print(f"   {mensaje_limite}")
        print(f"\n💡 Espera {tiempo_minimo}s entre publicaciones")
        input("\nPresiona Enter para salir...")
        return
    
    print(f"\n🖱️  Ejecución MANUAL")
    
    # Decidir tipo de publicación
    tipo_publicacion = decidir_tipo_publicacion(gestor, config)
    
    print(f"\n🎯 TIPO DE PUBLICACIÓN: {'📖 MENSAJE BÍBLICO' if tipo_publicacion == 'biblico' else '🎬 PREDICACIÓN'}\n")
    
    # Preparar contenido
    contenido = None
    nombre_archivo = None
    
    if tipo_publicacion == 'biblico':
        contenido, nombre_archivo = preparar_contenido_biblico(config, gestor)
    else:
        contenido, nombre_archivo, enlace_original = preparar_contenido_predicacion(config)
    
    if not contenido:
        print("❌ No se pudo preparar el contenido")
        input("\nPresiona Enter para salir...")
        return
    
    # Mostrar preview
    print(f"\n📄 PREVIEW:")
    print("-" * 70)
    preview = contenido[:200] + "..." if len(contenido) > 200 else contenido
    print(preview)
    print("-" * 70)
    
    # Iniciar navegador
    publicador = PublicadorFacebook(config)
    
    inicio = time.time()
    
    try:
        publicador.iniciar_navegador()
        
        # Publicar
        print(f"\n{'='*70}")
        print(f"{'📖 PUBLICANDO MENSAJE BÍBLICO' if tipo_publicacion == 'biblico' else '🎬 PUBLICANDO PREDICACIÓN'}")
        print(f"{'='*70}")
        print(f"📄 Archivo: {nombre_archivo}")
        print(f"📝 Longitud: {len(contenido)} caracteres")
        print(f"🔄 Máximo de intentos: {config['max_intentos_por_publicacion']}")
        
        if tipo_publicacion == 'predicacion':
            es_enlace = any(plat in contenido.lower() for plat in ['http', 'youtube', 'instagram', 'facebook', 'tiktok'])
            print(f"🔗 Tipo: {'Enlace' if es_enlace else 'Texto'} (Estrategia optimizada: {'Sí' if config.get('usar_estrategia_optimizada_enlaces', True) else 'No'})")
        
        print(f"{'='*70}\n")
        
        exito = publicar_contenido(publicador, contenido, tipo_publicacion, config)
        
        fin = time.time()
        tiempo_ejecucion = round(fin - inicio, 1)
        
        if exito:
            # Registrar éxito
            gestor.registrar_publicacion_exitosa(
                mensaje_archivo=nombre_archivo,
                contenido=contenido,
                longitud=len(contenido),
                intentos=1,  # TODO: capturar intentos reales
                tiempo_ejecucion=tiempo_ejecucion,
                tipo=tipo_publicacion
            )
            
            # Si es predicación, mover a publicados
            if tipo_publicacion == 'predicacion':
                mover_predicacion_a_publicados(nombre_archivo)
            
            print(f"\n{'='*70}")
            print("✅ PUBLICACIÓN EXITOSA")
            print(f"{'='*70}")
            print(f"⏱️  Tiempo: {tiempo_ejecucion}s")
            print(f"📄 Archivo: {nombre_archivo}")
            print(f"{'='*70}\n")
        else:
            # Registrar error
            gestor.registrar_error(nombre_archivo, f"Falló después de {config['max_intentos_por_publicacion']} intentos", tipo_publicacion)
            
            print(f"\n{'='*70}")
            print("❌ PROCESO CON ERRORES")
            print(f"{'='*70}\n")
    
    except KeyboardInterrupt:
        print("\n\n❌ Proceso cancelado por el usuario")
    
    except Exception as e:
        print(f"\n❌ Error durante la publicación: {e}")
        import traceback
        traceback.print_exc()
        
        if nombre_archivo:
            gestor.registrar_error(nombre_archivo, str(e), tipo_publicacion)
    
    finally:
        publicador.cerrar_navegador()
        print("⏳ Cerrando en 2 segundos...")
        time.sleep(2)


if __name__ == "__main__":
    main()
