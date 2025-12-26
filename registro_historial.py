"""
Módulo de Registro de Historial de Predicaciones
Se integra con el publicador de Facebook para registrar URLs publicadas
"""

import os
import json
from datetime import datetime


class RegistroHistorialPredicaciones:
    """
    Gestiona el historial de predicaciones publicadas
    Registra URLs en historial_publicados.json
    """
    
    def __init__(self):
        self.archivo_historial = "cola-facebook/historial_publicados.json"
        self.carpeta_publicados = "cola-facebook/publicados"
        
        # Asegurar que existe la carpeta
        os.makedirs(os.path.dirname(self.archivo_historial), exist_ok=True)
        os.makedirs(self.carpeta_publicados, exist_ok=True)
    
    def cargar_historial(self):
        """Carga el historial actual"""
        if os.path.exists(self.archivo_historial):
            try:
                with open(self.archivo_historial, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return self._crear_historial_vacio()
        return self._crear_historial_vacio()
    
    def _crear_historial_vacio(self):
        """Crea estructura de historial vacía"""
        return {
            "urls_publicadas": [],
            "total_publicadas": 0,
            "ultima_actualizacion": None,
            "primera_publicacion": None
        }
    
    def guardar_historial(self, historial):
        """Guarda el historial actualizado"""
        historial["ultima_actualizacion"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(self.archivo_historial, 'w', encoding='utf-8') as f:
            json.dump(historial, indent=2, ensure_ascii=False, fp=f)
    
    def registrar_publicacion(self, archivo_predica, url_publicada=None):
        """
        Registra una predicación como publicada
        
        Args:
            archivo_predica: Nombre del archivo (ej: "predica-001.txt")
            url_publicada: URL extraída del archivo (opcional, se lee automáticamente)
        
        Returns:
            bool: True si se registró correctamente
        """
        try:
            # Si no se proporciona URL, leerla del archivo
            if not url_publicada:
                ruta_pendiente = os.path.join("cola-facebook/pendientes", archivo_predica)
                ruta_publicado = os.path.join("cola-facebook/publicados", archivo_predica)
                
                # Intentar leer de pendientes o publicados
                if os.path.exists(ruta_pendiente):
                    with open(ruta_pendiente, 'r', encoding='utf-8') as f:
                        url_publicada = f.read().strip()
                elif os.path.exists(ruta_publicado):
                    with open(ruta_publicado, 'r', encoding='utf-8') as f:
                        url_publicada = f.read().strip()
                else:
                    print(f"⚠️  No se encontró el archivo: {archivo_predica}")
                    return False
            
            # Validar URL
            if not url_publicada or not url_publicada.startswith('http'):
                print(f"⚠️  URL inválida: {url_publicada}")
                return False
            
            # Cargar historial
            historial = self.cargar_historial()
            
            # Verificar si ya está registrada
            if url_publicada in historial["urls_publicadas"]:
                print(f"ℹ️  URL ya estaba registrada en historial")
                return True
            
            # Registrar
            historial["urls_publicadas"].append(url_publicada)
            historial["total_publicadas"] = len(historial["urls_publicadas"])
            
            # Actualizar fecha de primera publicación
            if not historial["primera_publicacion"]:
                historial["primera_publicacion"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Guardar
            self.guardar_historial(historial)
            
            print(f"✅ Predicación registrada en historial")
            print(f"   Archivo: {archivo_predica}")
            print(f"   URL: {url_publicada[:60]}...")
            print(f"   Total histórico: {historial['total_publicadas']} predicaciones")
            
            return True
            
        except Exception as e:
            print(f"❌ Error registrando en historial: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def obtener_estadisticas(self):
        """Obtiene estadísticas del historial"""
        historial = self.cargar_historial()
        
        return {
            "total_publicadas": historial["total_publicadas"],
            "primera_publicacion": historial.get("primera_publicacion"),
            "ultima_actualizacion": historial.get("ultima_actualizacion"),
            "urls_unicas": len(set(historial["urls_publicadas"]))
        }
    
    def mostrar_estadisticas(self):
        """Muestra las estadísticas en consola"""
        stats = self.obtener_estadisticas()
        
        print("\n" + "="*60)
        print("📊 ESTADÍSTICAS DEL HISTORIAL")
        print("="*60)
        print(f"   📈 Total publicadas: {stats['total_publicadas']}")
        print(f"   🔗 URLs únicas: {stats['urls_unicas']}")
        
        if stats['primera_publicacion']:
            print(f"   📅 Primera publicación: {stats['primera_publicacion']}")
        
        if stats['ultima_actualizacion']:
            print(f"   🕒 Última actualización: {stats['ultima_actualizacion']}")
        
        print("="*60 + "\n")


# ============================================================================
# EJEMPLO DE USO EN TU PUBLICADOR
# ============================================================================
"""
En tu archivo publicador_facebook.py (o el que uses), agrega esto:

1. Al inicio del archivo:
   from registro_historial import RegistroHistorialPredicaciones

2. Después de publicar exitosamente en Facebook:
   
   # Tu código actual de publicación...
   if publicacion_exitosa:
       # Mover de pendientes a publicados
       shutil.move(
           f"cola-facebook/pendientes/{archivo}",
           f"cola-facebook/publicados/{archivo}"
       )
       
       # AGREGAR ESTO: Registrar en historial
       registro = RegistroHistorialPredicaciones()
       registro.registrar_publicacion(archivo)

Eso es todo. El registro se hace automáticamente.
"""


# ============================================================================
# SCRIPT DE PRUEBA
# ============================================================================
if __name__ == "__main__":
    print("="*60)
    print("PRUEBA DEL REGISTRO DE HISTORIAL")
    print("="*60 + "\n")
    
    registro = RegistroHistorialPredicaciones()
    
    # Mostrar estadísticas actuales
    registro.mostrar_estadisticas()
    
    # Prueba de registro manual (si tienes archivos)
    print("Para probar, puedes:")
    print("1. Tener un archivo predica-XXX.txt en pendientes/")
    print("2. Ejecutar: registro.registrar_publicacion('predica-001.txt')")
    print("\nO proporcionar URL directamente:")
    print("registro.registrar_publicacion('predica-001.txt', 'https://youtube.com/shorts/ABC123')")
