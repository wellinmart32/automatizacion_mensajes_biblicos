import sys
import time
import os
import ctypes
import configparser

from datetime import datetime
from compartido.gestor_archivos import (
    leer_config_global,
    verificar_y_crear_estructura,
    obtener_mensaje_aleatorio_sin_repetir,
    obtener_mensaje_secuencial,
    contar_predicaciones_pendientes,
    obtener_siguiente_predicacion,
    mover_predicacion_a_publicados
)
from publicadores.publicador_facebook import PublicadorFacebook
from gestor_registro import GestorRegistro
from gestor_licencias import GestorLicencias
from dialogos_licencia import DialogosLicencia


def verificar_licencia_inicio():
    gestor_lic = GestorLicencias("MensajesBiblicos")
    resultado = gestor_lic.verificar_e_iniciar()

    if resultado.get('necesita_ingreso'):
        codigo = DialogosLicencia.solicitar_codigo_licencia()
        if not codigo:
            DialogosLicencia.mostrar_error("Necesitas un código de licencia para usar la aplicación")
            return None
        gestor_lic.guardar_codigo_licencia(codigo)
        resultado = gestor_lic.verificar_e_iniciar()

    if resultado.get('error'):
        DialogosLicencia.mostrar_error(resultado.get('mensaje'))
        return None

    if resultado.get('expirado'):
        DialogosLicencia.mostrar_trial_expirado(resultado.get('codigo'))
        return None

    if resultado.get('tipo') == 'TRIAL':
        dias = resultado.get('dias_restantes')
        print(f"\n⚠️  MODO TRIAL - Quedan {dias} días\n")

    if resultado.get('tipo') == 'FULL':
        print("\n✅ Licencia completa activada - Todas las funciones desbloqueadas\n")

    return resultado


def mostrar_banner():
    print("\n" + "="*70)
    print(" " * 15 + "🚀 PUBLICADOR AUTOMÁTICO DE FACEBOOK")
    print(" " * 20 + "Sistema de Mensajes Bíblicos")
    print("="*70 + "\n")


def mostrar_configuracion(config):
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
    if config['seleccion'] in ('aleatorio', 'aleatoria'):
        contenido, nombre_archivo = obtener_mensaje_aleatorio_sin_repetir(gestor.registro)
    else:
        contenido, nombre_archivo = obtener_mensaje_secuencial(gestor.registro)
    return (contenido, nombre_archivo), 'biblico'


def publicar_con_reintentos(publicador, contenido, tipo_publicacion, config, gestor, nombre_archivo=None):
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


def _publicar_mensaje_biblico(config):
    gestor = GestorRegistro()
    gestor.mostrar_estadisticas()
    gestor.mostrar_historial_reciente(5)

    if not gestor.puede_publicar_ahora(config.get('max_publicaciones_por_dia', 20)):
        print(f"\n⚠️  Límite diario alcanzado")
        return

    contenido_data, tipo_pub = obtener_contenido_publicacion(gestor, config)
    contenido, nombre_archivo = contenido_data
    if not contenido:
        print("❌ No hay mensajes disponibles")
        return

    print(f"\n📖 Mensaje seleccionado: {nombre_archivo}")
    print("\n🌐 Inicializando navegador...")
    publicador = PublicadorFacebook(config)
    publicador.iniciar_navegador()

    try:
        exito = publicar_con_reintentos(publicador, contenido, tipo_pub, config, gestor, nombre_archivo)
        if exito:
            gestor.registrar_publicacion_exitosa(nombre_archivo, '', 0, 1, 0, tipo='biblico')
            print("\n" + "="*70)
            print("✅ MENSAJE BÍBLICO PUBLICADO EXITOSAMENTE")
            print("="*70)
        else:
            print("\n" + "="*70)
            print("❌ NO SE PUDO PUBLICAR EL MENSAJE")
            print("="*70)
            gestor.registrar_error(nombre_archivo, tipo_pub, "Falló después de todos los intentos")
    finally:
        publicador.cerrar_navegador()


def _publicar_predicacion(config):
    gestor = GestorRegistro()
    ruta_archivo, titulo = obtener_siguiente_predicacion()
    if not ruta_archivo:
        print("❌ No hay predicaciones pendientes")
        return

    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            contenido = f.read().strip()
        if not contenido:
            print("❌ El archivo de predicación está vacío")
            return
    except Exception as e:
        print(f"❌ Error leyendo predicación: {e}")
        return

    # FIX Bug 2: Agregar mensaje introductorio desde configuración
    if config.get('agregar_introduccion_predica', True):
        intro = config.get('texto_introduccion_predica', '🎬 Predicación recomendada:\n\n')
        if intro:
            intro = intro.rstrip() + '\n\n'
            contenido = f"{intro}{contenido}"

    print(f"\n📹 Publicando predicación: {titulo}")
    print("\n🌐 Inicializando navegador...")
    publicador = PublicadorFacebook(config)
    publicador.iniciar_navegador()

    try:
        exito = publicar_con_reintentos(publicador, contenido, 'predicacion', config, gestor, titulo)
        if exito:
            gestor.registrar_publicacion_exitosa(titulo, '', 0, 1, 0, tipo='predicacion')
            mover_predicacion_a_publicados(titulo)
            print("\n" + "="*70)
            print("✅ PREDICACIÓN PUBLICADA EXITOSAMENTE")
            print("="*70)
        else:
            print("\n" + "="*70)
            print("❌ NO SE PUDO PUBLICAR LA PREDICACIÓN")
            print("="*70)
            gestor.registrar_error(titulo, 'predicacion', "Falló después de todos los intentos")
    finally:
        publicador.cerrar_navegador()

def _ejecutar_secuencia_full(config):
    if not getattr(sys, '_consola_abierta', False):
        try:
            ctypes.windll.kernel32.AllocConsole()
            sys.stdout = open('CONOUT$', 'w')
            sys.stderr = open('CONOUT$', 'w')
            sys._consola_abierta = True
        except:
            pass
    import subprocess
    base_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))

    cfg = configparser.RawConfigParser(delimiters=('=',))
    cfg.read(os.path.join(base_dir, "config_global.txt"), encoding='utf-8')
    modulos = cfg.get('SECUENCIA', 'modulos_activos', fallback='biblico,extraer,publicar_predica').strip()
    lista = [m.strip() for m in modulos.split(',') if m.strip()]

    for modulo in lista:
        if modulo == 'biblico':
            _publicar_mensaje_biblico(config)

        elif modulo == 'extraer':
            exe = os.path.join(base_dir, 'ExtractorPredicaciones.exe')
            if os.path.exists(exe):
                print("\n🎬 Iniciando extracción de predicaciones...")
                subprocess.Popen([exe]).wait()
            else:
                print("⚠️  ExtractorPredicaciones.exe no encontrado")

        elif modulo == 'publicar_predica':
            if contar_predicaciones_pendientes() > 0:
                _publicar_predicacion(config)
            else:
                print("\n📭 Sin predicaciones pendientes para publicar")

        elif modulo == 'oraciones':
            exe = os.path.join(base_dir, 'OracionesWhatsApp.exe')
            if os.path.exists(exe):
                print("\n📱 Iniciando envío de oraciones...")
                subprocess.Popen([exe]).wait()
            else:
                print("⚠️  OracionesWhatsApp.exe no encontrado")

def _validar_y_ejecutar_secuencia(config):
    """Valida configuración antes de ejecutar secuencia (doble clic en exe)"""
    import tkinter as tk
    from tkinter import messagebox
    import configparser as _cp
    import subprocess as _sp

    base_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))

    cfg = _cp.ConfigParser()
    cfg.read(os.path.join(base_dir, "config_global.txt"), encoding='utf-8')
    modulos = cfg.get('SECUENCIA', 'modulos_activos', fallback='').strip()

    root = tk.Tk()
    root.withdraw()

    # Validación 1: secuencia no configurada
    if not modulos:
        respuesta = messagebox.askokcancel(
            "⚙️ Secuencia no configurada",
            "No has configurado la secuencia de módulos.\n\n"
            "¿Deseas ir al Configurador para definirla ahora?",
            parent=root
        )
        root.destroy()
        if respuesta:
            exe_cfg = os.path.join(base_dir, "ConfiguradorMensajes.exe")
            if os.path.exists(exe_cfg):
                _sp.Popen([exe_cfg, "--pestana=secuencia"]).wait()
            else:
                _sp.Popen([sys.executable, "configurador_gui.py", "--pestana=secuencia"]).wait()
        else:
            _ejecutar_secuencia_full(config)
        return

    # Validación 2: grupo WhatsApp no configurado
    lista = [m.strip() for m in modulos.split(',') if m.strip()]
    necesita_grupo = 'extraer' in lista or 'publicar_predica' in lista
    if necesita_grupo:
        grupo = cfg.get('PREDICACIONES', 'nombre_grupo_whatsapp', fallback='').strip()
        if not grupo:
            respuesta = messagebox.askokcancel(
                "⚠️ Configuración incompleta",
                "La secuencia incluye 'Extraer Predicaciones' pero no has configurado\n"
                "el nombre del grupo de WhatsApp.\n\n"
                "¿Deseas ir al Configurador para completarlo ahora?",
                parent=root
            )
            root.destroy()
            if respuesta:
                exe_cfg = os.path.join(base_dir, "ConfiguradorMensajes.exe")
                if os.path.exists(exe_cfg):
                    _sp.Popen([exe_cfg, "--pestana=extractor"]).wait()
                else:
                    _sp.Popen([sys.executable, "configurador_gui.py", "--pestana=extractor"]).wait()
            else:
                _ejecutar_secuencia_full(config)
            return

    root.destroy()
    _ejecutar_secuencia_full(config)

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--solo-biblico', action='store_true')
    parser.add_argument('--secuencia', action='store_true')
    args, _ = parser.parse_known_args()

    estado_licencia = verificar_licencia_inicio()
    if not estado_licencia:
        print("\n❌ No se pudo verificar la licencia.")
        input("\nPresiona Enter para cerrar...")
        return

    mostrar_banner()

    try:
        config = leer_config_global()
    except Exception as e:
        print(f"❌ Error leyendo configuración: {e}")
        return

    mostrar_configuracion(config)

    es_full = estado_licencia.get('tipo') in ['FULL', 'MASTER'] or estado_licencia.get('developer_permanente')

    try:
        if args.solo_biblico:
            _publicar_mensaje_biblico(config)
        elif args.secuencia:
            _ejecutar_secuencia_full(config)
        elif es_full:
            _validar_y_ejecutar_secuencia(config)
        else:
            _publicar_mensaje_biblico(config)
    except KeyboardInterrupt:
        print("\n\n⚠️  Proceso cancelado por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()


def _verificar_wizard_completado():
    try:
        import subprocess
        config_path = os.path.join(
            os.path.expanduser("~"), ".config", "AutomaPro", "MensajesBiblicos", "config.json"
        )
        if not os.path.exists(config_path):
            if getattr(sys, 'frozen', False):
                base_dir = os.path.dirname(sys.executable)
                wizard = os.path.join(base_dir, "WizardMensajes.exe")
            else:
                wizard = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wizard_primera_vez.py")
            if os.path.exists(wizard):
                subprocess.Popen([wizard])
            return False
        return True
    except Exception:
        return True


if __name__ == "__main__":
    if not _verificar_wizard_completado():
        sys.exit(0)

    import argparse as _ap
    _p = _ap.ArgumentParser()
    _p.add_argument('--solo-biblico', action='store_true')
    _p.add_argument('--secuencia', action='store_true')
    _args, _ = _p.parse_known_args()

    if _args.solo_biblico or _args.secuencia:
        ctypes.windll.kernel32.AllocConsole()
        sys.stdout = open('CONOUT$', 'w')
        sys.stderr = open('CONOUT$', 'w')

    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Proceso cancelado por el usuario\n")
        sys.exit(0)
    except Exception as e:
        import traceback
        print(f"\n❌ Error inesperado: {e}")
        traceback.print_exc()