import json
import os
from datetime import datetime, timedelta


class GestorRegistro:
    """
    Gestiona el registro de publicaciones en Facebook
    Mantiene historial de últimos 5 mensajes para evitar repetición
    Similar a GestorRegistro de Marketplace pero adaptado para Facebook
    """
    
    def __init__(self, archivo_registro="registro_publicaciones.json"):
        self.archivo_registro = archivo_registro
        self.registro = self.cargar_registro()
    
    def cargar_registro(self):
        """Carga el registro desde el archivo JSON o crea uno nuevo"""
        if os.path.exists(self.archivo_registro):
            try:
                with open(self.archivo_registro, 'r', encoding='utf-8') as f:
                    registro = json.load(f)
                    
                # Asegurar que existan todos los campos necesarios
                campos_requeridos = {
                    'total_publicaciones': 0,
                    'ultima_ejecucion': None,
                    'fecha_ultima_publicacion': None,
                    'historial_reciente': [],  # Últimos N mensajes (para memoria)
                    'historial_completo': [],  # Historial completo con detalles
                    'estadisticas': {
                        'publicaciones_exitosas': 0,
                        'publicaciones_fallidas': 0,
                        'total_intentos': 0,
                        'tiempo_promedio_publicacion': 0
                    },
                    'errores': []
                }
                
                # Agregar campos faltantes
                for campo, valor_default in campos_requeridos.items():
                    if campo not in registro:
                        registro[campo] = valor_default
                
                return registro
                
            except Exception as e:
                print(f"⚠️  Error cargando registro: {e}")
                print("   Creando registro nuevo...")
                return self._crear_registro_vacio()
        else:
            print("📝 Creando nuevo registro_publicaciones.json")
            return self._crear_registro_vacio()
    
    def _crear_registro_vacio(self):
        """Crea estructura de registro vacía"""
        return {
            'total_publicaciones': 0,
            'ultima_ejecucion': None,
            'fecha_ultima_publicacion': None,
            'historial_reciente': [],  # Últimos N mensajes publicados
            'historial_completo': [],  # Lista de todas las publicaciones con detalles
            'estadisticas': {
                'publicaciones_exitosas': 0,
                'publicaciones_fallidas': 0,
                'total_intentos': 0,
                'tiempo_promedio_publicacion': 0,
                'mensaje_mas_publicado': None,
                'contador_mensajes': {}  # Cuenta veces que se publicó cada mensaje
            },
            'errores': []
        }
    
    def guardar_registro(self):
        """Guarda el registro en el archivo JSON"""
        try:
            with open(self.archivo_registro, 'w', encoding='utf-8') as f:
                json.dump(self.registro, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Error guardando registro: {e}")
            return False
    
    def puede_publicar_ahora(self, tiempo_minimo_segundos, permitir_forzar_manual=False):
        """
        Verifica si se puede publicar según el tiempo mínimo configurado
        
        Args:
            tiempo_minimo_segundos: Segundos mínimos entre publicaciones
            permitir_forzar_manual: Si True, permite publicar manualmente sin verificar tiempo
            
        Returns:
            tuple: (puede_publicar: bool, mensaje: str)
        """
        fecha_ultima = self.registro.get('fecha_ultima_publicacion')
        
        if not fecha_ultima:
            # Primera publicación, permitir
            return True, "Primera publicación"
        
        try:
            ultima_pub = datetime.strptime(fecha_ultima, "%Y-%m-%d %H:%M:%S")
            ahora = datetime.now()
            diferencia = (ahora - ultima_pub).total_seconds()
            
            if diferencia < tiempo_minimo_segundos:
                tiempo_restante = int(tiempo_minimo_segundos - diferencia)
                
                if permitir_forzar_manual:
                    # Mostrar advertencia pero permitir
                    return True, f"⚠️  Última publicación hace {int(diferencia)}s (forzado manual)"
                else:
                    # Bloquear publicación
                    return False, f"Última publicación hace {int(diferencia)}s. Espera {tiempo_restante}s más"
            
            return True, f"Última publicación hace {int(diferencia)}s"
            
        except Exception as e:
            print(f"⚠️  Error verificando tiempo: {e}")
            return True, "Error en verificación, permitiendo publicación"
    
    def registrar_publicacion_exitosa(self, mensaje_archivo, contenido, longitud, intentos, tiempo_ejecucion):
        """
        Registra una publicación exitosa
        
        Args:
            mensaje_archivo: Nombre del archivo (ej: mensaje-007.txt)
            contenido: Contenido publicado (primeros 100 caracteres)
            longitud: Longitud total del mensaje
            intentos: Número de intentos que tomó
            tiempo_ejecucion: Tiempo total en segundos
        """
        ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Crear entrada para historial completo
        entrada = {
            'fecha': ahora,
            'mensaje_archivo': mensaje_archivo,
            'contenido_preview': contenido[:100] + "..." if len(contenido) > 100 else contenido,
            'longitud': longitud,
            'estado': 'exitoso',
            'intentos': intentos,
            'tiempo_ejecucion': tiempo_ejecucion
        }
        
        # Agregar a historial completo
        self.registro['historial_completo'].append(entrada)
        
        # Agregar a historial reciente (para memoria de últimos 5)
        self.registro['historial_reciente'].append(mensaje_archivo)
        
        # Actualizar contadores
        self.registro['total_publicaciones'] += 1
        self.registro['fecha_ultima_publicacion'] = ahora
        self.registro['ultima_ejecucion'] = ahora
        
        # Actualizar estadísticas
        self.registro['estadisticas']['publicaciones_exitosas'] += 1
        self.registro['estadisticas']['total_intentos'] += intentos
        
        # Actualizar tiempo promedio
        total_pubs = self.registro['estadisticas']['publicaciones_exitosas']
        tiempo_actual = self.registro['estadisticas'].get('tiempo_promedio_publicacion', 0)
        nuevo_promedio = ((tiempo_actual * (total_pubs - 1)) + tiempo_ejecucion) / total_pubs
        self.registro['estadisticas']['tiempo_promedio_publicacion'] = round(nuevo_promedio, 2)
        
        # Actualizar contador de mensajes
        contador = self.registro['estadisticas'].get('contador_mensajes', {})
        contador[mensaje_archivo] = contador.get(mensaje_archivo, 0) + 1
        self.registro['estadisticas']['contador_mensajes'] = contador
        
        # Actualizar mensaje más publicado
        mensaje_mas_usado = max(contador, key=contador.get)
        self.registro['estadisticas']['mensaje_mas_publicado'] = mensaje_mas_usado
        
        # Guardar cambios
        self.guardar_registro()
        
        print(f"✅ Publicación registrada: {mensaje_archivo}")
    
    def registrar_error(self, mensaje_archivo, error):
        """
        Registra un error durante la publicación
        
        Args:
            mensaje_archivo: Nombre del archivo que se intentó publicar
            error: Descripción del error
        """
        ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        entrada_error = {
            'fecha': ahora,
            'mensaje_archivo': mensaje_archivo,
            'error': str(error)
        }
        
        self.registro['errores'].append(entrada_error)
        self.registro['estadisticas']['publicaciones_fallidas'] += 1
        self.registro['ultima_ejecucion'] = ahora
        
        self.guardar_registro()
        
        print(f"❌ Error registrado: {mensaje_archivo} - {error}")
    
    def obtener_estadisticas(self):
        """
        Obtiene estadísticas del registro
        
        Returns:
            dict: Estadísticas completas
        """
        stats = self.registro['estadisticas']
        
        total_intentos = stats.get('total_intentos', 0)
        total_exitosas = stats.get('publicaciones_exitosas', 0)
        promedio_intentos = round(total_intentos / total_exitosas, 2) if total_exitosas > 0 else 0
        
        total_publicaciones = total_exitosas + stats.get('publicaciones_fallidas', 0)
        tasa_exito = round((total_exitosas / total_publicaciones * 100), 1) if total_publicaciones > 0 else 0
        
        return {
            'total_publicaciones': self.registro['total_publicaciones'],
            'publicaciones_exitosas': total_exitosas,
            'publicaciones_fallidas': stats.get('publicaciones_fallidas', 0),
            'tasa_exito': tasa_exito,
            'promedio_intentos': promedio_intentos,
            'tiempo_promedio': stats.get('tiempo_promedio_publicacion', 0),
            'total_errores': len(self.registro['errores']),
            'mensaje_mas_publicado': stats.get('mensaje_mas_publicado'),
            'mensajes_en_historial': len(self.registro['historial_reciente']),
            'ultima_publicacion': self.registro.get('fecha_ultima_publicacion')
        }
    
    def mostrar_estadisticas(self):
        """Muestra estadísticas en consola de forma visual"""
        stats = self.obtener_estadisticas()
        
        print("\n" + "="*60)
        print(" " * 15 + "📊 ESTADÍSTICAS DEL SISTEMA")
        print("="*60)
        print(f"📈 Total publicaciones:        {stats['total_publicaciones']}")
        print(f"✅ Exitosas:                   {stats['publicaciones_exitosas']}")
        print(f"❌ Fallidas:                   {stats['publicaciones_fallidas']}")
        print(f"🎯 Tasa de éxito:              {stats['tasa_exito']}%")
        print(f"🔄 Promedio de intentos:       {stats['promedio_intentos']}")
        print(f"⏱️  Tiempo promedio:            {stats['tiempo_promedio']}s")
        print(f"🔥 Mensaje más publicado:      {stats['mensaje_mas_publicado']}")
        print(f"💾 Mensajes en memoria:        {stats['mensajes_en_historial']}")
        
        if stats['ultima_publicacion']:
            print(f"📅 Última publicación:         {stats['ultima_publicacion']}")
        
        print("="*60 + "\n")
    
    def mostrar_historial_reciente(self, cantidad=5):
        """
        Muestra los últimos N mensajes publicados (memoria activa)
        
        Args:
            cantidad: Número de mensajes a mostrar
        """
        historial = self.registro.get('historial_reciente', [])
        
        if not historial:
            print("📭 No hay historial de publicaciones aún")
            return
        
        ultimos = historial[-cantidad:] if len(historial) >= cantidad else historial
        
        print("\n" + "="*60)
        print(f"🚫 MENSAJES BLOQUEADOS (Últimos {len(ultimos)} publicados)")
        print("="*60)
        
        for i, mensaje in enumerate(reversed(ultimos), 1):
            print(f"  {i}. {mensaje}")
        
        print("="*60 + "\n")
    
    def limpiar_historial_reciente(self):
        """
        Limpia el historial reciente (memoria de últimos 5)
        Útil para resetear el sistema de memoria
        """
        confirmacion = input("⚠️  ¿Seguro que quieres limpiar el historial reciente? (escribe 'SI'): ")
        
        if confirmacion == "SI":
            mensajes_borrados = len(self.registro['historial_reciente'])
            self.registro['historial_reciente'] = []
            self.guardar_registro()
            print(f"🗑️  Historial reciente limpiado ({mensajes_borrados} mensajes)")
        else:
            print("❌ Limpieza cancelada")


def main():
    """Función de prueba del módulo"""
    print("🧪 Probando GestorRegistro...\n")
    
    gestor = GestorRegistro()
    
    # Mostrar estadísticas
    gestor.mostrar_estadisticas()
    
    # Mostrar historial reciente
    gestor.mostrar_historial_reciente(5)


if __name__ == "__main__":
    main()
