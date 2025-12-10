import os
import configparser
import random
import shutil
from datetime import datetime


def leer_config_global():
    """
    Lee config_global.txt y retorna un diccionario con la configuración
    Similar al sistema de Marketplace pero adaptado para Facebook
    """
    archivo_config = "config_global.txt"
    
    if not os.path.exists(archivo_config):
        print("⚠️  No existe config_global.txt. Creando configuración por defecto...")
        crear_config_defecto()
    
    config = configparser.ConfigParser()
    config.read(archivo_config, encoding='utf-8')
    
    # Convertir a diccionario con tipos correctos
    config_dict = {
        # [GENERAL]
        'nombre_proyecto': config['GENERAL']['nombre_proyecto'],
        'carpeta_mensajes': config['GENERAL']['carpeta_mensajes'],
        'navegador': config['GENERAL']['navegador'].lower(),
        'modo_debug': config['GENERAL']['modo_debug'].lower() == 'si',
        
        # [PUBLICACION]
        'tiempo_entre_intentos': int(config['PUBLICACION']['tiempo_entre_intentos']),
        'max_intentos_por_publicacion': int(config['PUBLICACION']['max_intentos_por_publicacion']),
        'espera_despues_publicar': int(config['PUBLICACION']['espera_despues_publicar']),
        'verificar_publicacion_exitosa': config['PUBLICACION']['verificar_publicacion_exitosa'].lower() == 'si',
        'espera_estabilizacion_modal': int(config['PUBLICACION']['espera_estabilizacion_modal']),
        
        # [LIMITES]
        'tiempo_minimo_entre_publicaciones_segundos': int(config['LIMITES']['tiempo_minimo_entre_publicaciones_segundos']),
        'permitir_duplicados': config['LIMITES']['permitir_duplicados'].lower() == 'si',
        'permitir_forzar_publicacion_manual': config['LIMITES']['permitir_forzar_publicacion_manual'].lower() == 'si',
        
        # [MENSAJES]
        'seleccion': config['MENSAJES']['seleccion'].lower(),
        'historial_evitar_repetir': int(config['MENSAJES']['historial_evitar_repetir']),
        'formato_fecha': config['MENSAJES']['formato_fecha'].lower() == 'si',
        'agregar_hashtags': config['MENSAJES']['agregar_hashtags'].lower() == 'si',
        'hashtags': config['MENSAJES']['hashtags'],
        'agregar_firma': config['MENSAJES']['agregar_firma'].lower() == 'si',
        'texto_firma': config['MENSAJES']['texto_firma'],
        
        # [DEBUG]
        'modo_debug': config['DEBUG']['modo_debug'].lower(),
        
        # [NAVEGADOR]
        'usar_perfil_existente': config['NAVEGADOR']['usar_perfil_existente'].lower() == 'si',
        'carpeta_perfil_custom': config['NAVEGADOR']['carpeta_perfil_custom'],
        'desactivar_notificaciones': config['NAVEGADOR']['desactivar_notificaciones'].lower() == 'si',
        'maximizar_ventana': config['NAVEGADOR']['maximizar_ventana'].lower() == 'si',
        
        # [PREDICACIONES]
        'activar_predicaciones': config['PREDICACIONES']['activar_predicaciones'].lower() == 'si' if config.has_option('PREDICACIONES', 'activar_predicaciones') else False,
        'alternar_con_predicaciones': config['PREDICACIONES']['alternar_con_predicaciones'].lower() == 'si' if config.has_option('PREDICACIONES', 'alternar_con_predicaciones') else False,
        'nombre_grupo_whatsapp': config['PREDICACIONES']['nombre_grupo_whatsapp'] if config.has_option('PREDICACIONES', 'nombre_grupo_whatsapp') else 'Prédicas',
        'mensajes_por_extraccion': int(config['PREDICACIONES']['mensajes_por_extraccion']) if config.has_option('PREDICACIONES', 'mensajes_por_extraccion') else 10,
        'agregar_introduccion_predica': config['PREDICACIONES']['agregar_introduccion_predica'].lower() == 'si' if config.has_option('PREDICACIONES', 'agregar_introduccion_predica') else True,
        'texto_introduccion_predica': config['PREDICACIONES']['texto_introduccion_predica'].replace('\\n', '\n') if config.has_option('PREDICACIONES', 'texto_introduccion_predica') else '🎬 Predicación recomendada:\n\n',
        'agregar_hashtags_predicaciones': config['PREDICACIONES']['agregar_hashtags_predicaciones'].lower() == 'si' if config.has_option('PREDICACIONES', 'agregar_hashtags_predicaciones') else True,
        'hashtags_predicaciones': config['PREDICACIONES']['hashtags_predicaciones'] if config.has_option('PREDICACIONES', 'hashtags_predicaciones') else '#Predicación,#Fe,#Cristiano'
    }
    
    return config_dict


def crear_config_defecto():
    """Crea config_global.txt con valores por defecto si no existe"""
    print("⚠️  Función crear_config_defecto() no implementada aún")
    print("   Por favor, copia manualmente el archivo config_global.txt al proyecto")


def verificar_y_crear_estructura():
    """
    Verifica y crea todas las carpetas necesarias del sistema
    Incluye carpetas de predicaciones
    """
    config = leer_config_global()
    
    carpetas_necesarias = [
        config['carpeta_mensajes'],
        'cola-facebook',
        'cola-facebook/pendientes',
        'cola-facebook/publicados'
    ]
    
    # Crear carpeta de perfil si no usa perfil existente
    if not config['usar_perfil_existente']:
        carpetas_necesarias.append(config['carpeta_perfil_custom'])
    
    carpetas_creadas = []
    for carpeta in carpetas_necesarias:
        if not os.path.exists(carpeta):
            os.makedirs(carpeta)
            carpetas_creadas.append(carpeta)
    
    # Crear .gitkeep en carpetas de predicaciones
    gitkeep_pendientes = os.path.join('cola-facebook', 'pendientes', '.gitkeep')
    gitkeep_publicados = os.path.join('cola-facebook', 'publicados', '.gitkeep')
    
    if not os.path.exists(gitkeep_pendientes):
        with open(gitkeep_pendientes, 'w') as f:
            f.write('')
    
    if not os.path.exists(gitkeep_publicados):
        with open(gitkeep_publicados, 'w') as f:
            f.write('')
    
    if carpetas_creadas:
        print(f"✅ Carpetas creadas: {', '.join(carpetas_creadas)}")
    
    return True


def contar_predicaciones_pendientes():
    """
    Cuenta cuántas predicaciones hay en cola-facebook/pendientes/
    
    Returns:
        int: Número de predicaciones pendientes
    """
    carpeta = 'cola-facebook/pendientes'
    
    if not os.path.exists(carpeta):
        return 0
    
    archivos = [f for f in os.listdir(carpeta) 
               if f.endswith('.txt') and f.startswith('predica-')]
    
    return len(archivos)


def contar_predicaciones_publicadas():
    """
    Cuenta cuántas predicaciones hay en cola-facebook/publicados/
    
    Returns:
        int: Número de predicaciones publicadas
    """
    carpeta = 'cola-facebook/publicados'
    
    if not os.path.exists(carpeta):
        return 0
    
    archivos = [f for f in os.listdir(carpeta) 
               if f.endswith('.txt') and f.startswith('predica-')]
    
    return len(archivos)


def obtener_siguiente_predicacion():
    """
    Obtiene la siguiente predicación pendiente (orden alfabético)
    
    Returns:
        tuple: (ruta_completa, nombre_archivo) o (None, None)
    """
    carpeta = 'cola-facebook/pendientes'
    
    if not os.path.exists(carpeta):
        return None, None
    
    # Obtener archivos .txt que empiecen con 'predica-'
    archivos = [f for f in os.listdir(carpeta) 
               if f.endswith('.txt') and f.startswith('predica-')]
    
    if not archivos:
        return None, None
    
    # Ordenar alfabéticamente (predica-001.txt, predica-002.txt, etc.)
    archivos.sort()
    
    # Tomar el primero
    archivo_siguiente = archivos[0]
    ruta_completa = os.path.join(carpeta, archivo_siguiente)
    
    return ruta_completa, archivo_siguiente


def mover_predicacion_a_publicados(nombre_archivo):
    """
    Mueve una predicación de pendientes/ a publicados/
    También mueve archivos asociados (imágenes si existen)
    
    Args:
        nombre_archivo: Nombre del archivo (ej: predica-001.txt)
    
    Returns:
        bool: True si se movió correctamente
    """
    carpeta_pendientes = 'cola-facebook/pendientes'
    carpeta_publicados = 'cola-facebook/publicados'
    
    # Asegurar que existan las carpetas
    os.makedirs(carpeta_publicados, exist_ok=True)
    
    # Rutas del archivo .txt
    origen_txt = os.path.join(carpeta_pendientes, nombre_archivo)
    destino_txt = os.path.join(carpeta_publicados, nombre_archivo)
    
    try:
        # Mover archivo .txt
        if os.path.exists(origen_txt):
            shutil.move(origen_txt, destino_txt)
            print(f"   📦 Movido: {nombre_archivo}")
        
        # Buscar archivo de imagen asociado (mismo nombre pero .jpg)
        nombre_base = nombre_archivo.replace('.txt', '')
        nombre_imagen = f"{nombre_base}.jpg"
        
        origen_img = os.path.join(carpeta_pendientes, nombre_imagen)
        destino_img = os.path.join(carpeta_publicados, nombre_imagen)
        
        if os.path.exists(origen_img):
            shutil.move(origen_img, destino_img)
            print(f"   🖼️  Movida imagen: {nombre_imagen}")
        
        return True
        
    except Exception as e:
        print(f"   ⚠️  Error moviendo predicación: {e}")
        return False


def obtener_mensaje_aleatorio_sin_repetir(registro_publicaciones):
    """
    Obtiene un mensaje aleatorio evitando los últimos N publicados
    
    Args:
        registro_publicaciones: Diccionario con historial de publicaciones
        
    Returns:
        tuple: (contenido_mensaje, nombre_archivo) o (None, None) si no hay mensajes
    """
    config = leer_config_global()
    carpeta = config['carpeta_mensajes']
    
    # Verificar que exista la carpeta
    if not os.path.exists(carpeta):
        print(f"❌ No existe la carpeta: {carpeta}")
        return None, None
    
    # Obtener todos los archivos .txt
    todos_mensajes = [f for f in os.listdir(carpeta) if f.endswith('.txt')]
    
    if not todos_mensajes:
        print(f"❌ No hay archivos .txt en la carpeta: {carpeta}")
        return None, None
    
    print(f"📦 Total de mensajes disponibles: {len(todos_mensajes)}")
    
    # Obtener historial de últimos N mensajes
    historial_reciente = registro_publicaciones.get('historial_reciente', [])
    limite_historial = config['historial_evitar_repetir']
    
    # Mensajes bloqueados (últimos N publicados)
    mensajes_bloqueados = historial_reciente[-limite_historial:] if historial_reciente else []
    
    # Mensajes disponibles (no están en el historial reciente)
    mensajes_disponibles = [m for m in todos_mensajes if m not in mensajes_bloqueados]
    
    print(f"🚫 Mensajes bloqueados (últimos {limite_historial}): {len(mensajes_bloqueados)}")
    print(f"✅ Mensajes disponibles: {len(mensajes_disponibles)}")
    
    # Si no hay mensajes disponibles, usar todos (caso extremo)
    if not mensajes_disponibles:
        print("⚠️  No hay mensajes disponibles. Usando todos los mensajes.")
        mensajes_disponibles = todos_mensajes
    
    # Mostrar mensajes bloqueados en debug
    if mensajes_bloqueados and config['modo_debug'] in ['detallado', 'completo']:
        print(f"\n🚫 Bloqueados actualmente:")
        for i, msg in enumerate(mensajes_bloqueados, 1):
            print(f"   {i}. {msg}")
    
    # Seleccionar uno aleatorio de los disponibles
    mensaje_seleccionado = random.choice(mensajes_disponibles)
    
    print(f"\n🎲 Mensaje seleccionado: {mensaje_seleccionado}")
    
    # Leer contenido del mensaje
    ruta_mensaje = os.path.join(carpeta, mensaje_seleccionado)
    try:
        with open(ruta_mensaje, 'r', encoding='utf-8') as f:
            contenido = f.read().strip()
        
        # Aplicar transformaciones según config
        contenido = aplicar_transformaciones_mensaje(contenido, config)
        
        return contenido, mensaje_seleccionado
    
    except Exception as e:
        print(f"❌ Error leyendo mensaje {mensaje_seleccionado}: {e}")
        return None, None


def obtener_mensaje_secuencial(registro_publicaciones):
    """
    Obtiene el siguiente mensaje en orden alfabético
    
    Args:
        registro_publicaciones: Diccionario con historial de publicaciones
        
    Returns:
        tuple: (contenido_mensaje, nombre_archivo) o (None, None) si no hay mensajes
    """
    config = leer_config_global()
    carpeta = config['carpeta_mensajes']
    
    # Verificar que exista la carpeta
    if not os.path.exists(carpeta):
        print(f"❌ No existe la carpeta: {carpeta}")
        return None, None
    
    # Obtener todos los archivos .txt ordenados
    todos_mensajes = sorted([f for f in os.listdir(carpeta) if f.endswith('.txt')])
    
    if not todos_mensajes:
        print(f"❌ No hay archivos .txt en la carpeta: {carpeta}")
        return None, None
    
    # Obtener el último mensaje publicado
    historial = registro_publicaciones.get('historial_completo', [])
    
    if not historial:
        # Primera publicación, usar el primero
        mensaje_seleccionado = todos_mensajes[0]
    else:
        # Obtener el último publicado (solo bíblicos)
        ultimo_biblico = None
        for entrada in reversed(historial):
            if entrada.get('tipo', 'biblico') == 'biblico':
                ultimo_biblico = entrada.get('mensaje_archivo')
                break
        
        if not ultimo_biblico:
            # No hay bíblicos previos, empezar desde el primero
            mensaje_seleccionado = todos_mensajes[0]
        else:
            try:
                # Encontrar índice del último publicado
                indice_actual = todos_mensajes.index(ultimo_biblico)
                # Siguiente mensaje (con rotación)
                indice_siguiente = (indice_actual + 1) % len(todos_mensajes)
                mensaje_seleccionado = todos_mensajes[indice_siguiente]
            except ValueError:
                # Si el último publicado no existe, empezar desde el primero
                mensaje_seleccionado = todos_mensajes[0]
    
    print(f"📋 Mensaje secuencial seleccionado: {mensaje_seleccionado}")
    
    # Leer contenido
    ruta_mensaje = os.path.join(carpeta, mensaje_seleccionado)
    try:
        with open(ruta_mensaje, 'r', encoding='utf-8') as f:
            contenido = f.read().strip()
        
        # Aplicar transformaciones
        contenido = aplicar_transformaciones_mensaje(contenido, config)
        
        return contenido, mensaje_seleccionado
    
    except Exception as e:
        print(f"❌ Error leyendo mensaje {mensaje_seleccionado}: {e}")
        return None, None


def aplicar_transformaciones_mensaje(contenido, config):
    """
    Aplica transformaciones al mensaje según configuración
    (fecha, hashtags, firma, etc.)
    
    Args:
        contenido: Texto del mensaje original
        config: Diccionario de configuración
        
    Returns:
        str: Mensaje transformado
    """
    mensaje_final = contenido
    
    # Agregar fecha
    if config['formato_fecha']:
        fecha_actual = datetime.now().strftime("%d/%m/%Y")
        mensaje_final = f"{mensaje_final}\n\n📅 {fecha_actual}"
    
    # Agregar hashtags
    if config['agregar_hashtags'] and config['hashtags']:
        mensaje_final = f"{mensaje_final}\n\n{config['hashtags']}"
    
    # Agregar firma
    if config['agregar_firma'] and config['texto_firma']:
        mensaje_final = f"{mensaje_final}\n\n{config['texto_firma']}"
    
    return mensaje_final


def obtener_ruta_perfil_navegador():
    """
    Obtiene la ruta del perfil del navegador según configuración
    
    Returns:
        str: Ruta al perfil o None si usa perfil existente del sistema
    """
    config = leer_config_global()
    
    if config['usar_perfil_existente']:
        # Detectar perfil según navegador
        if config['navegador'] == 'firefox':
            return obtener_primer_perfil_firefox()
        elif config['navegador'] == 'chrome':
            # Chrome usa perfil del sistema por defecto
            return None
        else:
            print(f"⚠️  Navegador desconocido: {config['navegador']}")
            return None
    else:
        # Usar carpeta de perfil personalizada
        carpeta_perfil = config['carpeta_perfil_custom']
        
        # Crear carpeta si no existe
        if not os.path.exists(carpeta_perfil):
            os.makedirs(carpeta_perfil)
            print(f"✅ Carpeta de perfil creada: {carpeta_perfil}")
        
        return os.path.abspath(carpeta_perfil)


def obtener_primer_perfil_firefox():
    """
    Encuentra automáticamente el primer perfil de Firefox disponible
    
    Returns:
        str: Ruta al perfil de Firefox o None si no se encuentra
    """
    ruta_perfiles = os.path.expanduser("~\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles")
    
    if not os.path.exists(ruta_perfiles):
        print(f"⚠️  No se encontró la carpeta de perfiles de Firefox: {ruta_perfiles}")
        return None
    
    perfiles = [f for f in os.listdir(ruta_perfiles) if os.path.isdir(os.path.join(ruta_perfiles, f))]
    
    if not perfiles:
        print("⚠️  No se encontraron perfiles de Firefox")
        return None
    
    perfil_seleccionado = os.path.join(ruta_perfiles, perfiles[0])
    print(f"🦊 Perfil Firefox detectado: {perfiles[0]}")
    return perfil_seleccionado


def obtener_estadisticas_mensajes():
    """
    Obtiene estadísticas sobre los mensajes disponibles
    
    Returns:
        dict: Estadísticas de mensajes
    """
    config = leer_config_global()
    carpeta = config['carpeta_mensajes']
    
    if not os.path.exists(carpeta):
        return {
            'total_mensajes': 0,
            'mensajes_validos': [],
            'existe_carpeta': False
        }
    
    todos_archivos = os.listdir(carpeta)
    mensajes_txt = [f for f in todos_archivos if f.endswith('.txt')]
    
    return {
        'total_mensajes': len(mensajes_txt),
        'mensajes_validos': sorted(mensajes_txt),
        'existe_carpeta': True,
        'ruta_carpeta': os.path.abspath(carpeta)
    }
