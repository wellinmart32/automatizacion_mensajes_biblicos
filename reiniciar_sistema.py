#!/usr/bin/env python3
"""
Script de Reinicio del Sistema - Mensajes Bíblicos
Permite reiniciar diferentes partes del sistema con un menú interactivo
Estilo consistente con el proyecto de Marketplace
"""

import json
import os
import shutil
from datetime import datetime


class ReiniciadorSistema:
    """Gestiona el reinicio de diferentes componentes del sistema"""
    
    def __init__(self):
        self.archivo_registro = "registro_publicaciones.json"
        self.carpeta_pendientes = "cola-facebook/pendientes"
        self.carpeta_publicados = "cola-facebook/publicados"
        self.carpeta_mensajes = "mensajes"
        self.carpeta_perfiles = "perfiles"
    
    def limpiar_pantalla(self):
        """Limpia la consola"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def mostrar_header(self):
        """Muestra el encabezado"""
        print("=" * 70)
        print(" " * 15 + "🔄 REINICIAR SISTEMA")
        print(" " * 12 + "Sistema de Mensajes Bíblicos")
        print("=" * 70)
        print()
    
    def cargar_registro(self):
        """Carga el registro actual"""
        if not os.path.exists(self.archivo_registro):
            return None
        
        try:
            with open(self.archivo_registro, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    
    def mostrar_estado_actual(self):
        """Muestra el estado actual del sistema"""
        self.limpiar_pantalla()
        self.mostrar_header()
        
        print("📊 ESTADO ACTUAL DEL SISTEMA:\n")
        
        # Leer registro
        registro = self.cargar_registro()
        
        if not registro:
            print("⚠️  No se encontró registro_publicaciones.json")
            print("   El sistema parece estar sin inicializar.\n")
        else:
            # Estadísticas generales
            print(f"📈 PUBLICACIONES:")
            print(f"   Total: {registro.get('total_publicaciones', 0)}")
            stats = registro.get('estadisticas', {})
            print(f"   Mensajes bíblicos: {stats.get('publicaciones_biblicas', 0)}")
            print(f"   Predicaciones: {stats.get('publicaciones_predicaciones', 0)}")
            print(f"   Exitosas: {stats.get('publicaciones_exitosas', 0)}")
            print(f"   Fallidas: {stats.get('publicaciones_fallidas', 0)}")
            
            # Predicaciones WhatsApp
            print(f"\n🎬 PREDICACIONES WHATSAPP:")
            pred = registro.get('predicaciones_whatsapp', {})
            print(f"   Índice actual: {pred.get('indice_catalogo', 0)}")
            print(f"   Total extraídos: {pred.get('total_extraidos', 0)}")
            print(f"   Última extracción: {pred.get('fecha_ultima_extraccion', 'Nunca')}")
        
        # Contar archivos
        print(f"\n📂 ARCHIVOS:")
        
        # Mensajes bíblicos
        if os.path.exists(self.carpeta_mensajes):
            mensajes = [f for f in os.listdir(self.carpeta_mensajes) if f.endswith('.txt')]
            print(f"   Mensajes bíblicos: {len(mensajes)} archivos")
        
        # Predicaciones pendientes
        if os.path.exists(self.carpeta_pendientes):
            pendientes = [f for f in os.listdir(self.carpeta_pendientes) if f.endswith('.txt')]
            print(f"   Predicaciones pendientes: {len(pendientes)} archivos")
        else:
            print(f"   Predicaciones pendientes: 0 archivos")
        
        # Predicaciones publicadas
        if os.path.exists(self.carpeta_publicados):
            publicados = [f for f in os.listdir(self.carpeta_publicados) if f.endswith('.txt')]
            print(f"   Predicaciones publicadas: {len(publicados)} archivos")
        else:
            print(f"   Predicaciones publicadas: 0 archivos")
        
        # Perfiles
        if os.path.exists(self.carpeta_perfiles):
            print(f"   Perfiles guardados: Sí (sesiones de navegador)")
        else:
            print(f"   Perfiles guardados: No")
        
        print("\n" + "=" * 70)
        input("\nPresiona Enter para volver al menú...")
    
    def reiniciar_indice_predicaciones(self):
        """Opción 1: Solo reinicia el índice de predicaciones"""
        self.limpiar_pantalla()
        self.mostrar_header()
        
        print("🔄 OPCIÓN 1: REINICIAR ÍNDICE DE PREDICACIONES\n")
        
        registro = self.cargar_registro()
        if not registro:
            print("❌ No se encontró registro_publicaciones.json")
            input("\nPresiona Enter para continuar...")
            return
        
        pred = registro.get('predicaciones_whatsapp', {})
        indice_actual = pred.get('indice_catalogo', 0)
        
        print("📋 ACCIÓN A REALIZAR:")
        print(f"   Índice actual: {indice_actual}")
        print(f"   Nuevo índice: 0")
        print(f"\n💡 Esto permitirá volver a extraer las predicaciones desde el inicio.")
        print(f"   El historial de publicaciones se mantendrá intacto.\n")
        
        print("=" * 70)
        print("\n⚠️  ADVERTENCIA: Esta acción modificará el registro\n")
        confirmacion = input("Escribe 'SI' en MAYÚSCULAS para confirmar: ")
        
        if confirmacion != 'SI':
            print("\n❌ Operación cancelada")
            input("\nPresiona Enter para continuar...")
            return
        
        # Reiniciar índice
        registro['predicaciones_whatsapp']['indice_catalogo'] = 0
        
        # Guardar
        with open(self.archivo_registro, 'w', encoding='utf-8') as f:
            json.dump(registro, f, indent=2, ensure_ascii=False)
        
        print("\n✅ Índice reiniciado exitosamente")
        print("   Índice de predicaciones: 0")
        input("\nPresiona Enter para continuar...")
    
    def reiniciar_historial_publicaciones(self):
        """Opción 2: Solo reinicia el historial de publicaciones"""
        self.limpiar_pantalla()
        self.mostrar_header()
        
        print("🔄 OPCIÓN 2: REINICIAR HISTORIAL DE PUBLICACIONES\n")
        
        registro = self.cargar_registro()
        if not registro:
            print("❌ No se encontró registro_publicaciones.json")
            input("\nPresiona Enter para continuar...")
            return
        
        total = registro.get('total_publicaciones', 0)
        
        print("📋 ACCIÓN A REALIZAR:")
        print(f"   Se borrarán {total} publicaciones del historial")
        print(f"   Las estadísticas se resetearán a 0")
        print(f"   El índice de predicaciones se mantendrá\n")
        
        print("=" * 70)
        print("\n⚠️  ADVERTENCIA CRÍTICA: Esta acción es PERMANENTE\n")
        confirmacion = input("Escribe 'SI' en MAYÚSCULAS para confirmar: ")
        
        if confirmacion != 'SI':
            print("\n❌ Operación cancelada")
            input("\nPresiona Enter para continuar...")
            return
        
        # Mantener solo datos de predicaciones
        pred_backup = registro.get('predicaciones_whatsapp', {})
        
        # Resetear registro
        registro['total_publicaciones'] = 0
        registro['ultima_ejecucion'] = None
        registro['fecha_ultima_publicacion'] = None
        registro['historial_reciente'] = []
        registro['historial_completo'] = []
        registro['estadisticas'] = {
            'publicaciones_exitosas': 0,
            'publicaciones_fallidas': 0,
            'total_intentos': 0,
            'tiempo_promedio_publicacion': 0,
            'publicaciones_biblicas': 0,
            'publicaciones_predicaciones': 0
        }
        registro['errores'] = []
        registro['predicaciones_whatsapp'] = pred_backup
        
        # Guardar
        with open(self.archivo_registro, 'w', encoding='utf-8') as f:
            json.dump(registro, f, indent=2, ensure_ascii=False)
        
        print("\n✅ Historial reiniciado exitosamente")
        print("   Total publicaciones: 0")
        print("   Índice de predicaciones: MANTENIDO")
        input("\nPresiona Enter para continuar...")
    
    def reiniciar_todo_sistema(self):
        """Opción 3: Reinicia TODO el sistema"""
        self.limpiar_pantalla()
        self.mostrar_header()
        
        print("🔄 OPCIÓN 3: REINICIAR TODO EL SISTEMA\n")
        
        print("⚠️  ADVERTENCIA: Esta acción eliminará:\n")
        print("   ❌ registro_publicaciones.json → se reseteará completamente")
        print("   ❌ cola-facebook/pendientes/*.txt → predicaciones pendientes")
        print("   ❌ cola-facebook/publicados/*.txt → predicaciones publicadas")
        print("   ❌ perfiles/ → sesiones de navegador (WhatsApp y Facebook)")
        print("\n   ✅ SE CONSERVARÁ:")
        print("   ✓ mensajes/*.txt → tus mensajes bíblicos originales")
        print("   ✓ config_global.txt → tu configuración")
        print("   ✓ Código del sistema (extractores, publicadores, etc.)")
        print("\n💡 Es como ejecutar el sistema por primera vez.")
        print("   Podrás volver a extraer las predicaciones de WhatsApp.\n")
        
        print("=" * 70)
        print("\n⚠️  ADVERTENCIA CRÍTICA: Esta acción es PERMANENTE\n")
        confirmacion = input("Escribe 'SI' en MAYÚSCULAS para confirmar: ")
        
        if confirmacion != 'SI':
            print("\n❌ Operación cancelada")
            input("\nPresiona Enter para continuar...")
            return
        
        print("\n🔄 Reiniciando sistema...")
        
        # 1. Resetear registro_publicaciones.json
        registro_inicial = {
            "total_publicaciones": 0,
            "ultima_ejecucion": None,
            "fecha_ultima_publicacion": None,
            "historial_reciente": [],
            "historial_completo": [],
            "estadisticas": {
                "publicaciones_exitosas": 0,
                "publicaciones_fallidas": 0,
                "total_intentos": 0,
                "tiempo_promedio_publicacion": 0,
                "publicaciones_biblicas": 0,
                "publicaciones_predicaciones": 0
            },
            "errores": [],
            "predicaciones_whatsapp": {
                "indice_catalogo": 0,
                "total_extraidos": 0,
                "fecha_ultima_extraccion": None,
                "historial_extracciones": []
            }
        }
        
        with open(self.archivo_registro, 'w', encoding='utf-8') as f:
            json.dump(registro_inicial, f, indent=2, ensure_ascii=False)
        
        print("   ✅ registro_publicaciones.json reseteado")
        
        # 2. Borrar archivos de cola-facebook/pendientes/
        pendientes_borrados = 0
        if os.path.exists(self.carpeta_pendientes):
            for archivo in os.listdir(self.carpeta_pendientes):
                if archivo.endswith('.txt'):
                    os.remove(os.path.join(self.carpeta_pendientes, archivo))
                    pendientes_borrados += 1
        
        print(f"   ✅ {pendientes_borrados} archivos borrados de pendientes/")
        
        # 3. Borrar archivos de cola-facebook/publicados/
        publicados_borrados = 0
        if os.path.exists(self.carpeta_publicados):
            for archivo in os.listdir(self.carpeta_publicados):
                if archivo.endswith('.txt'):
                    os.remove(os.path.join(self.carpeta_publicados, archivo))
                    publicados_borrados += 1
        
        print(f"   ✅ {publicados_borrados} archivos borrados de publicados/")
        
        # 4. Borrar carpeta de perfiles (sesiones de navegador)
        # ⚠️ TEMPORALMENTE DESACTIVADO PARA PRUEBAS
        # if os.path.exists(self.carpeta_perfiles):
        #     try:
        #         shutil.rmtree(self.carpeta_perfiles)
        #         print(f"   ✅ Carpeta 'perfiles/' eliminada (sesiones de navegador)")
        #     except Exception as e:
        #         print(f"   ⚠️  Error eliminando perfiles/: {e}")
        # else:
        #     print(f"   ℹ️  Carpeta 'perfiles/' no existe")
        
        print(f"   ⚠️  Perfiles conservados (modo prueba)")
        
        print("\n" + "=" * 70)
        print("✅ SISTEMA REINICIADO COMPLETAMENTE")
        print("=" * 70)
        print("\n💡 PRÓXIMOS PASOS:")
        print("   1. Ejecuta '0_Ejecutar_Todo.bat'")
        print("   2. El sistema extraerá predicaciones de WhatsApp")
        print("   3. Comenzará a publicar alternando 1:1")
        print("   4. NO necesitas volver a iniciar sesión (perfiles conservados)")
        print("=" * 70)
        
        input("\nPresiona Enter para continuar...")
    
    def mostrar_menu(self):
        """Muestra el menú principal"""
        while True:
            self.limpiar_pantalla()
            self.mostrar_header()
            
            print("¿Qué deseas hacer?\n")
            print("1. 🔄 Reiniciar SOLO índice de predicaciones")
            print("   └─ Vuelve índice a 0, mantiene historial\n")
            
            print("2. 📊 Reiniciar SOLO historial de publicaciones")
            print("   └─ Limpia historial y estadísticas, mantiene índice\n")
            
            print("3. 💥 Reiniciar TODO el sistema (RECOMENDADO)")
            print("   └─ Resetea JSON + borra archivos + elimina perfiles")
            print("   └─ Conserva mensajes bíblicos y configuración\n")
            
            print("4. 📋 Ver estado actual del sistema\n")
            
            print("5. ❌ Salir\n")
            
            print("=" * 70)
            opcion = input("Selecciona una opción (1-5): ")
            
            if opcion == '1':
                self.reiniciar_indice_predicaciones()
            elif opcion == '2':
                self.reiniciar_historial_publicaciones()
            elif opcion == '3':
                self.reiniciar_todo_sistema()
            elif opcion == '4':
                self.mostrar_estado_actual()
            elif opcion == '5':
                print("\n👋 ¡Hasta luego!\n")
                break
            else:
                print("\n❌ Opción inválida. Intenta de nuevo.")
                input("\nPresiona Enter para continuar...")


def main():
    """Función principal"""
    try:
        reiniciador = ReiniciadorSistema()
        reiniciador.mostrar_menu()
    except KeyboardInterrupt:
        print("\n\n❌ Proceso cancelado por el usuario\n")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        input("\nPresiona Enter para salir...")


if __name__ == "__main__":
    main()
