import sys
import time
from datetime import datetime

# ── Colores ANSI ──────────────────────────────────────────────
V  = '\033[92m'   # verde
R  = '\033[91m'   # rojo
A  = '\033[93m'   # amarillo
C  = '\033[96m'   # cian
N  = '\033[1m'    # negrita
X  = '\033[0m'    # reset
# ─────────────────────────────────────────────────────────────

from compartido.gestor_archivos import (
    leer_config_global,
    verificar_y_crear_estructura,
    contar_predicaciones_pendientes,
    contar_predicaciones_publicadas,
    guardar_nombre_grupo_whatsapp
)
from extractores.extractor_whatsapp_predicaciones import ExtractorWhatsAppPredicaciones
from gestor_registro import GestorRegistro


def mostrar_banner():
    # Aplicar icono aquí — consola ya está activa en este punto
    try:
        import ctypes as _ct
        _hwnd = _ct.windll.kernel32.GetConsoleWindow()
        if _hwnd:
            _base = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
            _ico = os.path.join(_base, 'iconos', 'clapper.ico')
            if os.path.exists(_ico):
                _hicon = _ct.windll.user32.LoadImageW(0, _ico, 1, 0, 0, 0x10)
                if _hicon:
                    _ct.windll.user32.SendMessageW(_hwnd, 0x0080, 1, _hicon)
                    _ct.windll.user32.SendMessageW(_hwnd, 0x0080, 0, _hicon)
    except Exception:
        pass

    print(f"\n{N}{C}" + "="*70 + X)
    print(f"{N}{C}" + " " * 10 + "📱 EXTRACTOR DE PREDICACIONES DE WHATSAPP" + X)
    print(f"{N}{C}" + " " * 15 + "Sistema de Predicaciones Automáticas" + X)
    print(f"{N}{C}" + "="*70 + X + "\n")


def mostrar_estado_sistema(gestor, config):
    print("📊 ESTADO DEL SISTEMA:\n")

    predicaciones = gestor.registro.get('predicaciones_whatsapp', {})

    indice_actual = predicaciones.get('indice_catalogo', 0)
    total_extraidos = predicaciones.get('total_extraidos', 0)
    fecha_ultima = predicaciones.get('fecha_ultima_extraccion', 'Nunca')

    print(f"   📍 Última posición extraída: {indice_actual}")
    print(f"   📦 Total extraídos histórico: {total_extraidos}")
    print(f"   📅 Última extracción: {fecha_ultima}")

    pendientes = contar_predicaciones_pendientes()
    publicados = contar_predicaciones_publicadas()

    print(f"\n📂 ARCHIVOS EN CARPETAS:")
    print(f"   ⏳ Pendientes: {pendientes} predicaciones")
    print(f"   ✅ Publicados: {publicados} predicaciones")

    print(f"\n⚙️  CONFIGURACIÓN:")
    print(f"   📱 Grupo WhatsApp: {config['nombre_grupo_whatsapp']}")
    print(f"   📦 Mensajes por extracción: {config['mensajes_por_extraccion']}")
    print(f"   🔄 Alternancia activa: {'Sí' if config['alternar_con_predicaciones'] else 'No'}")

    if pendientes > 0:
        print(f"\n💡 INFO:")
        print(f"   Con {pendientes} pendientes y 4 publicaciones/día:")
        print(f"   Alternando 1:1 = 2 predicaciones/día")
        print(f"   Duración estimada: {pendientes / 2:.1f} días")


def verificar_nombre_grupo(config, es_automatico):
    """Verifica si el nombre del grupo está configurado, si no lo solicita via GUI"""
    if not config.get('nombre_grupo_whatsapp', '').strip() and not es_automatico:
        import tkinter as tk
        from tkinter import simpledialog
        root = tk.Tk()
        root.withdraw()
        nuevo_nombre = simpledialog.askstring(
            "📱 Grupo de WhatsApp",
            "No has configurado el nombre del grupo de WhatsApp.\n\n"
            "Ingresa el nombre EXACTAMENTE como aparece en WhatsApp:",
            parent=root
        )
        root.destroy()
        if nuevo_nombre and nuevo_nombre.strip():
            nuevo_nombre = nuevo_nombre.strip()
            guardar_nombre_grupo_whatsapp(nuevo_nombre)
            config['nombre_grupo_whatsapp'] = nuevo_nombre
        else:
            print("⚠️  Se usará el nombre por defecto: Prédicas\n")


def confirmar_extraccion(config, indice_actual, es_automatico=False):
    print("\n" + "="*70)
    print("🎯 EXTRACCIÓN A REALIZAR:")
    print("="*70)

    cantidad = config['mensajes_por_extraccion']

    print(f"   📱 Grupo: {config['nombre_grupo_whatsapp']}")
    print(f"   📦 Cantidad: {cantidad} mensajes")
    print(f"   📍 Posición actual: {indice_actual}")
    print(f"   🎯 Rango a extraer: [{indice_actual + 1} - {indice_actual + cantidad}]")
    print(f"   💾 Destino: cola-facebook/pendientes/")
    print("="*70 + "\n")

    if es_automatico:
        print("🤖 Modo automático - iniciando inmediatamente...\n")
        return True

    print("⏳ Iniciando en 5 segundos... (Presiona Ctrl+C para cancelar)\n")

    try:
        time.sleep(5)
        return True
    except KeyboardInterrupt:
        return False


def main():
    import os
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('AutomaPro.ExtractorPredicaciones')
    except Exception:
        pass

    # Habilitar colores ANSI en consola Windows
    try:
        import ctypes as _ct
        _ct.windll.kernel32.SetConsoleMode(_ct.windll.kernel32.GetStdHandle(-11), 7)
    except Exception:
        pass

    # Ícono personalizado en ventana de consola
    try:
        import ctypes as _ct
        _hwnd = 0
        for _ in range(50):
            _hwnd = _ct.windll.kernel32.GetConsoleWindow()
            if _hwnd:
                break
            time.sleep(0.1)
        if _hwnd:
            _base = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
            _ico = os.path.join(_base, 'iconos', 'clapper.ico')
            if os.path.exists(_ico):
                _hicon = _ct.windll.user32.LoadImageW(0, _ico, 1, 0, 0, 0x10)
                if _hicon:
                    _ct.windll.user32.SendMessageW(_hwnd, 0x0080, 1, _hicon)
                    _ct.windll.user32.SendMessageW(_hwnd, 0x0080, 0, _hicon)
                    # Reaplicar después de un momento para garantizar
                    time.sleep(0.3)
                    _ct.windll.user32.SendMessageW(_hwnd, 0x0080, 1, _hicon)
                    _ct.windll.user32.SendMessageW(_hwnd, 0x0080, 0, _hicon)
    except Exception:
        pass

    es_automatico = len(sys.argv) > 1 and sys.argv[1] == '--auto'

    if not es_automatico:
        mostrar_banner()

    try:
        config = leer_config_global()
    except Exception as e:
        print(f"❌ Error cargando configuración: {e}")
        return

    # Si no hay grupo configurado — salir sin interrumpir
    if not config.get('nombre_grupo_whatsapp', '').strip():
        print("⚠️  No hay grupo de WhatsApp configurado.")
        print("   Ve al Configurador → pestaña 'Extractor WhatsApp' y configura el nombre del grupo.")
        return

    if not config.get('activar_predicaciones', False):
        print("⚠️  LAS PREDICACIONES ESTÁN DESACTIVADAS")
        print("\n💡 Para activarlas:")
        print("   1. Abre el Configurador")
        print("   2. Ve a pestaña 'Extractor WhatsApp'")
        print("   3. Configura el nombre del grupo\n")
        return

    print("📁 Verificando estructura de carpetas...")
    verificar_y_crear_estructura()
    print()

    gestor = GestorRegistro()

    mostrar_estado_sistema(gestor, config)

    predicaciones = gestor.registro.get('predicaciones_whatsapp', {})
    indice_actual = predicaciones.get('indice_catalogo', 0)

    if not confirmar_extraccion(config, indice_actual, es_automatico):
        return

    extractor = ExtractorWhatsAppPredicaciones()

    try:
        predicaciones_extraidas = extractor.ejecutar(
            nombre_grupo=config['nombre_grupo_whatsapp'],
            cantidad=config['mensajes_por_extraccion'],
            indice_inicio=indice_actual
        )

        if predicaciones_extraidas:
            nuevo_indice = indice_actual + config['mensajes_por_extraccion']

            gestor.registrar_extraccion_predicaciones(
                cantidad_extraida=len(predicaciones_extraidas),
                nuevo_indice=nuevo_indice,
                nombre_grupo=config['nombre_grupo_whatsapp']
            )

            print(f"\n{V}{N}" + "="*70 + X)
            print(f"{V}{N}✅ EXTRACCIÓN COMPLETADA EXITOSAMENTE{X}")
            print(f"{V}{N}" + "="*70 + X)
            print(f"📦 Predicaciones extraídas: {len(predicaciones_extraidas)}")
            print(f"📍 Nueva posición: {nuevo_indice}")
            print(f"💾 Guardadas en: cola-facebook/pendientes/")
            print("="*70)

            print("\n📊 ESTADO ACTUALIZADO:")
            pendientes = contar_predicaciones_pendientes()
            publicados = contar_predicaciones_publicadas()
            print(f"   ⏳ Pendientes: {pendientes}")
            print(f"   ✅ Publicados: {publicados}")

            print("\n💡 PRÓXIMOS PASOS:")
            if config['alternar_con_predicaciones']:
                print("   ✅ Alternancia activada")
                print("   📅 Las publicaciones automáticas publicarán:")
                print("      • 1 mensaje bíblico")
                print("      • 1 predicación")
                print("      • 1 mensaje bíblico")
                print("      • 1 predicación")
                print("      • ...")
            else:
                print("   ⚠️  Alternancia desactivada")
                print("   Solo se publicarán mensajes bíblicos")

        else:
            print(f"\n{A}{N}⚠️  NO SE EXTRAJO NINGUNA PREDICACIÓN{X}")
            print("\n💡 Posibles causas:")
            print("   • Ya no hay mensajes nuevos en el grupo")
            print("   • El índice actual ya llegó al final")
            print("   • Los mensajes recientes son solo texto (sin enlaces/imágenes)")
            print("\n   Revisa el grupo de WhatsApp y verifica que haya contenido nuevo")

        print()

    except KeyboardInterrupt:
        print("\n\n❌ Proceso cancelado por el usuario")

    except Exception as e:
        print(f"\n❌ Error durante la extracción: {e}")
        import traceback
        traceback.print_exc()

    finally:
        print(f"\n{N}👋 Finalizando programa...{X}")
        time.sleep(2)


if __name__ == "__main__":
    main()