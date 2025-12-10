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
    """Ejecuta un script de Python y maneja errores"""
    print(f"\n{'='*70}")
    print(f"🚀 {descripcion}")
    print(f"{'='*70}\n")
    
    try:
        # Construir comando con parámetro --auto si es necesario
        comando = [sys.executable, script_name]
        if modo_auto:
            comando.append('--auto')
        
        resultado = subprocess.run(
            comando,
            capture_output=False,
            text=True
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


def main():
    """Orquestador maestro - Ejecuta el flujo completo automáticamente"""
    
    print("\n" + "="*70)
    print(" " * 10 + "🎯 PUBLICADOR AUTOMÁTICO - FLUJO COMPLETO")
    print(" " * 12 + "Mensajes Bíblicos + Predicaciones WhatsApp")
    print("="*70 + "\n")
    
    # Leer configuración
    try:
        config = leer_config_global()
    except Exception as e:
        print(f"❌ Error leyendo configuración: {e}")
        print("   Ejecuta '2_Configurador.bat' para configurar el sistema")
        input("\nPresiona Enter para salir...")
        return
    
    # Verificar estructura
    print("📁 Verificando estructura de carpetas...")
    verificar_y_crear_estructura()
    print()
    
    # Inicializar gestor de registro
    gestor = GestorRegistro()
    
    # Mostrar configuración
    print("⚙️  CONFIGURACIÓN DEL FLUJO:\n")
    print(f"   📖 Mensajes bíblicos: {config['carpeta_mensajes']}")
    print(f"   🌐 Navegador: {config['navegador'].upper()}")
    print(f"   🎲 Selección: {config['seleccion'].capitalize()}")
    
    if config.get('activar_predicaciones', False):
        print(f"   🎬 Predicaciones: ACTIVADAS")
        print(f"   🔀 Alternancia 1:1: {'Sí' if config.get('alternar_con_predicaciones') else 'No'}")
        print(f"   📱 Grupo WhatsApp: {config['nombre_grupo_whatsapp']}")
    else:
        print(f"   🎬 Predicaciones: DESACTIVADAS")
    
    # Mostrar estadísticas
    gestor.mostrar_estadisticas()
    
    # Verificar predicaciones pendientes
    pendientes = contar_predicaciones_pendientes()
    
    print("\n" + "="*70)
    print("📦 ESTADO DE PREDICACIONES:")
    print("="*70)
    print(f"   ⏳ Pendientes: {pendientes}")
    print("="*70 + "\n")
    
    # DECISIÓN: ¿Necesita extraer predicaciones?
    necesita_extraer = False
    
    if config.get('activar_predicaciones', False) and config.get('alternar_con_predicaciones', False):
        # Verificar si necesita extraer
        if pendientes < 5:  # Umbral: menos de 5 predicaciones
            print("⚠️  POCAS PREDICACIONES PENDIENTES")
            print(f"   Pendientes: {pendientes}")
            print(f"   Umbral mínimo: 5")
            print(f"   → Se extraerán más predicaciones de WhatsApp\n")
            necesita_extraer = True
        else:
            print(f"✅ SUFICIENTES PREDICACIONES PENDIENTES")
            print(f"   Pendientes: {pendientes}")
            print(f"   → No es necesario extraer más\n")
    
    # Mostrar plan de ejecución
    print("="*70)
    print("📋 PLAN DE EJECUCIÓN:")
    print("="*70)
    
    if necesita_extraer:
        print("  1️⃣  Extraer predicaciones de WhatsApp")
        print("  2️⃣  Publicar en Facebook (mensaje bíblico o predicación)")
    else:
        print("  1️⃣  Publicar en Facebook (mensaje bíblico o predicación)")
    
    print("="*70 + "\n")
    
    # Countdown automático
    print("⏳ Iniciando automáticamente en 5 segundos...")
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
    
    # FASE 1: Extraer predicaciones (si es necesario)
    if necesita_extraer:
        print("\n" + "="*70)
        print("📱 FASE 1: EXTRACCIÓN DE PREDICACIONES DE WHATSAPP")
        print("="*70 + "\n")
        
        exito_extraccion = ejecutar_script(
            "extraer_predicaciones_whatsapp.py",
            "Extracción de Predicaciones WhatsApp"
        )
        
        if not exito_extraccion:
            print("\n⚠️  La extracción tuvo problemas.")
            continuar = input("¿Continuar con la publicación de todos modos? (si/no): ")
            if continuar.lower() not in ['si', 'sí', 's']:
                print("\n❌ Proceso cancelado")
                return
        
        # Actualizar contador de pendientes
        pendientes = contar_predicaciones_pendientes()
        print(f"\n✅ Predicaciones pendientes actualizadas: {pendientes}")
    
    # FASE 2: Publicar en Facebook
    print("\n" + "="*70)
    print("🚀 FASE 2: PUBLICACIÓN EN FACEBOOK")
    print("="*70 + "\n")
    
    # Verificar límite de tiempo (si fue publicación reciente)
    tiempo_minimo = config['tiempo_minimo_entre_publicaciones_segundos']
    puede_publicar, mensaje = gestor.puede_publicar_ahora(tiempo_minimo, False)
    
    if not puede_publicar:
        print(f"⏸️  NO SE PUEDE PUBLICAR AHORA:")
        print(f"   {mensaje}")
        print(f"   Tiempo mínimo: {tiempo_minimo}s")
        print("\n💡 El sistema esperará automáticamente en la próxima ejecución")
    else:
        ejecutar_script(
            "publicar_facebook.py",
            "Publicación en Facebook"
        )
    
    # RESUMEN FINAL
    print("\n" + "="*70)
    print("✅ FLUJO COMPLETO FINALIZADO")
    print("="*70 + "\n")
    
    # Estadísticas actualizadas
    gestor_final = GestorRegistro()
    gestor_final.mostrar_estadisticas()
    
    # Estado actualizado de predicaciones
    pendientes_final = contar_predicaciones_pendientes()
    
    print("📦 ESTADO FINAL DE PREDICACIONES:")
    print(f"   ⏳ Pendientes: {pendientes_final}")
    
    if config.get('activar_predicaciones', False) and config.get('alternar_con_predicaciones', False):
        if pendientes_final < 5:
            print(f"   ⚠️  Quedan pocas predicaciones")
            print(f"   💡 En la próxima ejecución se extraerán más automáticamente")
        else:
            print(f"   ✅ Suficientes predicaciones disponibles")
    
    print("\n💡 Próxima ejecución:")
    print("   • Ejecuta '0_Ejecutar_Todo.bat' para repetir el proceso")
    print("   • El sistema decidirá automáticamente si extraer más predicaciones")
    print("   • La alternancia 1:1 continúa automáticamente")
    print("   • Configura tareas programadas para automatizar completamente\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Proceso cancelado por el usuario\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        input("\nPresiona Enter para salir...")
