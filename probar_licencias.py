from gestor_licencias import GestorLicencias
from dialogos_licencia import DialogosLicencia


def probar_sistema_licencias():
    """Script de prueba para el sistema de licencias"""
    
    print("\n" + "="*70)
    print(" " * 20 + "🔐 PRUEBA DE SISTEMA DE LICENCIAS")
    print("="*70 + "\n")
    
    gestor = GestorLicencias("MensajesBiblicos")
    
    # Verificar si hay licencia guardada
    codigo_guardado = gestor.obtener_codigo_guardado()
    
    if codigo_guardado:
        print(f"📋 Código guardado encontrado: {codigo_guardado}\n")
    else:
        print("📋 No hay código de licencia guardado\n")
    
    # Solicitar código para probar
    print("Opciones de prueba:")
    print("1. LIC-TRIAL001  - Licencia TRIAL activa")
    print("2. LIC-FULL001   - Licencia FULL")
    print("3. LIC-INVALID   - Licencia inválida")
    print("4. Usar código guardado")
    print("5. Ingresar código personalizado\n")
    
    opcion = input("Selecciona una opción (1-5): ").strip()
    
    if opcion == "1":
        codigo = "LIC-TRIAL001"
    elif opcion == "2":
        codigo = "LIC-FULL001"
    elif opcion == "3":
        codigo = "LIC-INVALID"
    elif opcion == "4":
        if not codigo_guardado:
            print("\n❌ No hay código guardado")
            return
        codigo = codigo_guardado
    elif opcion == "5":
        codigo = input("\nIngresa el código: ").strip()
    else:
        print("\n❌ Opción inválida")
        return
    
    # Probar verificación
    print(f"\n🔍 Verificando licencia: {codigo}")
    print("⏳ Conectando con el backend...\n")
    
    resultado = gestor.verificar_licencia(codigo)
    
    print("="*70)
    print("RESPUESTA DEL BACKEND:")
    print("="*70)
    
    for clave, valor in resultado.items():
        print(f"  {clave}: {valor}")
    
    print("="*70 + "\n")
    
    # Guardar si es válida
    if resultado.get('valida'):
        guardar = input("¿Deseas guardar este código? (s/n): ").strip().lower()
        if guardar == 's':
            if gestor.guardar_codigo_licencia(codigo):
                print("✅ Código guardado correctamente")
            else:
                print("❌ Error al guardar código")
    
    # Probar flujo completo
    print("\n" + "="*70)
    print("PRUEBA DE FLUJO COMPLETO:")
    print("="*70 + "\n")
    
    estado = gestor.verificar_e_iniciar()
    
    print("Estado de la licencia:")
    for clave, valor in estado.items():
        print(f"  {clave}: {valor}")
    
    print("\n✅ Prueba completada")
    print("\n💡 Para usar en la aplicación real, ejecuta: py publicar_facebook.py")


if __name__ == "__main__":
    try:
        probar_sistema_licencias()
    except KeyboardInterrupt:
        print("\n\n⚠️  Prueba cancelada")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nPresiona Enter para salir...")