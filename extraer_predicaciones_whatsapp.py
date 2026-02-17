import sys
import time
from datetime import datetime
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
    """Muestra el banner inicial"""
    print("\n" + "="*70)
    print(" " * 10 + "📱 EXTRACTOR DE PREDICACIONES DE WHATSAPP")
    print(" " * 15 + "Sistema de Predicaciones Automáticas")
    print("="*70 + "\n")


def mostrar_estado_sistema(gestor, config):
    """Muestra el estado actual del sistema"""
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
    """Verifica si el nombre del grupo está configurado, si no lo solicita"""
    if config.get('nombre_grupo_whatsapp') == 'Prédicas' and not es_automatico:
        print("⚠️  No has configurado el nombre de tu grupo de WhatsApp\n")
        print("   El nombre debe ser EXACTAMENTE igual a como aparece en WhatsApp")
        print("   Ejemplo: 'Grupo Predicaciones', 'Iglesia Central', etc.\n")
        
        nuevo_nombre = input("📱 Ingresa el nombre de tu grupo de WhatsApp: ").strip()
        
        if nuevo_nombre:
            guardar_nombre_grupo_whatsapp(nuevo_nombre)
            config['nombre_grupo_whatsapp'] = nuevo_nombre
            print(f"\n✅ Grupo guardado: {nuevo_nombre}\n")
        else:
            print("⚠️  Se usará el nombre por defecto: Prédicas\n")


def confirmar_extraccion(config, indice_actual, es_automatico=False):
    """Pide confirmación al usuario antes de extraer (solo en modo manual)"""
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
        for i in range(5, 0, -1):
            print(f"   {i}...", end='\r', flush=True)
            sys.stdout.flush()
            time.sleep(1)
        print("   ✅ ¡Iniciando extracción!\n")
        return True
    except KeyboardInterrupt:
        print("\n\n❌ Extracción cancelada por el usuario\n")
        return False


def main():
    """Función principal"""
    
    es_automatico = len(sys.argv) > 1 and sys.argv[1] == '--auto'
    
    if not es_automatico:
        mostrar_banner()
    
    try:
        config = leer_config_global()
    except Exception as e:
        print(f"❌ Error cargando configuración: {e}")
        if not es_automatico:
            input("\nPresiona Enter para salir...")
        return
    
    # Verificar nombre del grupo (primera vez)
    verificar_nombre_grupo(config, es_automatico)
    
    if not config.get('activar_predicaciones', False):
        print("⚠️  LAS PREDICACIONES ESTÁN DESACTIVADAS")
        print("\n💡 Para activarlas:")
        print("   1. Ejecuta '2_Configurador.bat'")
        print("   2. O edita config_global.txt:")
        print("      [PREDICACIONES]")
        print("      activar_predicaciones = si\n")
        if not es_automatico:
            input("Presiona Enter para salir...")
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
            
            print("\n" + "="*70)
            print("✅ EXTRACCIÓN COMPLETADA EXITOSAMENTE")
            print("="*70)
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
                print("   Activa alternancia en '2_Configurador.bat'")
        
        else:
            print("\n⚠️  NO SE EXTRAJO NINGUNA PREDICACIÓN")
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
        if not es_automatico:
            input("\nPresiona Enter para salir...")


if __name__ == "__main__":
    main()