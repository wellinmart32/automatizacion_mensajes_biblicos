import os
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path


class GestorLicencias:
    """Gestor de licencias con sistema de cache local"""

    def __init__(self, nombre_app="MensajesBiblicos"):
        self.nombre_app = nombre_app
        self.url_backend = "http://localhost:8080/api/public/verificar-licencia"
        
        # Código developer maestro (funciona para todas las apps)
        self.codigo_developer_master = "LIC-MASTER-WELLI"
        
        # Ruta del archivo de configuración local
        if os.name == 'nt':  # Windows
            base_path = Path(os.environ.get('USERPROFILE', '~'))
        else:  # Linux/Mac
            base_path = Path.home()
        
        self.carpeta_config = base_path / '.config' / 'AutomaPro' / nombre_app
        self.archivo_config = self.carpeta_config / 'config.json'
        self.dias_revalidacion = 7  # Re-verificar cada 7 días (excepto developer)

    def _es_codigo_developer_permanente(self, codigo):
        """Verifica si es un código developer master"""
        return codigo == self.codigo_developer_master

    def obtener_codigo_guardado(self):
        """Obtiene el código de licencia guardado localmente"""
        try:
            if self.archivo_config.exists():
                with open(self.archivo_config, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
                    return datos.get('codigo_licencia', '')
        except Exception as e:
            print(f"Error leyendo configuración local: {e}")
        return ''

    def guardar_codigo_licencia(self, codigo):
        """Guarda el código de licencia localmente"""
        try:
            self.carpeta_config.mkdir(parents=True, exist_ok=True)
            
            datos = {}
            if self.archivo_config.exists():
                with open(self.archivo_config, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
            
            datos['codigo_licencia'] = codigo
            
            with open(self.archivo_config, 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error guardando código de licencia: {e}")
            return False

    def _obtener_cache_local(self):
        """Obtiene los datos de licencia del cache local"""
        try:
            if self.archivo_config.exists():
                with open(self.archivo_config, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error leyendo cache local: {e}")
        return None

    def _guardar_cache_local(self, datos_licencia):
        """Guarda los datos de licencia en cache local"""
        try:
            self.carpeta_config.mkdir(parents=True, exist_ok=True)
            
            cache = self._obtener_cache_local() or {}
            
            codigo = datos_licencia.get('codigo', datos_licencia.get('codigoLicencia', ''))
            
            cache.update({
                'codigo_licencia': codigo,
                'tipo': datos_licencia.get('tipo', 'TRIAL'),
                'valida': datos_licencia.get('valida', False),
                'expirada': datos_licencia.get('expirada', False),
                'dias_restantes': datos_licencia.get('diasRestantes'),
                'fecha_verificacion': datetime.now().isoformat(),
                'es_developer_permanente': self._es_codigo_developer_permanente(codigo)
            })
            
            with open(self.archivo_config, 'w', encoding='utf-8') as f:
                json.dump(cache, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error guardando cache: {e}")
            return False

    def _necesita_revalidacion(self, cache):
        """Verifica si necesita re-validar contra el backend"""
        if not cache or 'fecha_verificacion' not in cache:
            return True
        
        # Códigos developer permanentes NUNCA necesitan revalidación
        if cache.get('es_developer_permanente'):
            return False
        
        try:
            fecha_verificacion = datetime.fromisoformat(cache['fecha_verificacion'])
            dias_pasados = (datetime.now() - fecha_verificacion).days
            return dias_pasados >= self.dias_revalidacion
        except:
            return True

    def verificar_licencia(self, codigo_licencia, mostrar_mensajes=True):
        """
        Verifica la licencia usando sistema de cache
        
        Returns:
            dict con estructura:
            {
                'tipo': 'TRIAL' | 'FULL',
                'valida': True | False,
                'expirada': True | False,
                'diasRestantes': int | None,
                'mensaje': str,
                'desde_cache': True | False
            }
        """
        
        # CASO ESPECIAL: Código developer permanente
        if self._es_codigo_developer_permanente(codigo_licencia):
            if mostrar_mensajes:
                print("👑 Código developer permanente detectado")
            
            # Guardar en cache
            self._guardar_cache_local({
                'codigo': codigo_licencia,
                'tipo': 'FULL',
                'valida': True,
                'expirada': False,
                'diasRestantes': None
            })
            
            return {
                'tipo': 'FULL',
                'valida': True,
                'expirada': False,
                'diasRestantes': None,
                'mensaje': 'Licencia developer permanente',
                'desde_cache': False,
                'developer_permanente': True
            }
        
        # Verificar cache local
        cache = self._obtener_cache_local()
        
        # Si existe cache y no necesita revalidación, usar cache
        if cache and not self._necesita_revalidacion(cache):
            if mostrar_mensajes:
                if cache.get('es_developer_permanente'):
                    print("👑 Licencia developer permanente (cache)")
                else:
                    print("✅ Usando licencia en cache (verificada recientemente)")
            
            return {
                'tipo': cache.get('tipo', 'TRIAL'),
                'valida': cache.get('valida', False),
                'expirada': cache.get('expirada', False),
                'diasRestantes': cache.get('dias_restantes'),
                'mensaje': 'Licencia válida (desde cache local)',
                'desde_cache': True,
                'developer_permanente': cache.get('es_developer_permanente', False)
            }
        
        # Intentar verificar contra backend
        try:
            if mostrar_mensajes:
                print(f"🔍 Verificando licencia: {codigo_licencia}")
            
            response = requests.post(
                self.url_backend,
                json={'codigoLicencia': codigo_licencia},
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            
            if response.status_code == 200:
                datos = response.json()
                
                # Guardar en cache
                self._guardar_cache_local(datos)
                
                if mostrar_mensajes:
                    if datos.get('valida'):
                        tipo = datos.get('tipo', 'TRIAL')
                        print(f"✅ Licencia {tipo} verificada correctamente")
                    else:
                        print("❌ Licencia inválida o expirada")
                
                return {
                    'tipo': datos.get('tipo', 'TRIAL'),
                    'valida': datos.get('valida', False),
                    'expirada': datos.get('expirada', False),
                    'diasRestantes': datos.get('diasRestantes'),
                    'mensaje': datos.get('mensaje', ''),
                    'desde_cache': False,
                    'developer_permanente': False
                }
            else:
                raise Exception(f"Error del servidor: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            # Backend no disponible - usar cache si existe
            if cache and cache.get('valida'):
                if mostrar_mensajes:
                    print("⚠️  Backend no disponible. Usando cache local.")
                
                # Extender fecha de verificación para no reintentar cada día
                # (excepto para developer que ya nunca revalida)
                if not cache.get('es_developer_permanente'):
                    cache['fecha_verificacion'] = datetime.now().isoformat()
                    with open(self.archivo_config, 'w', encoding='utf-8') as f:
                        json.dump(cache, f, indent=2, ensure_ascii=False)
                
                return {
                    'tipo': cache.get('tipo', 'TRIAL'),
                    'valida': True,
                    'expirada': False,
                    'diasRestantes': cache.get('dias_restantes'),
                    'mensaje': 'Licencia válida (backend no disponible, usando cache)',
                    'desde_cache': True,
                    'developer_permanente': cache.get('es_developer_permanente', False)
                }
            else:
                if mostrar_mensajes:
                    print("❌ No se pudo verificar la licencia y no hay cache disponible")
                
                return {
                    'tipo': 'TRIAL',
                    'valida': False,
                    'expirada': False,
                    'diasRestantes': None,
                    'mensaje': 'No se pudo verificar la licencia. Backend no disponible.',
                    'desde_cache': False,
                    'developer_permanente': False
                }
                
        except requests.exceptions.Timeout:
            # Timeout - usar cache si existe
            if cache and cache.get('valida'):
                if mostrar_mensajes:
                    print("⚠️  Timeout al verificar. Usando cache local.")
                
                # Extender fecha de verificación
                if not cache.get('es_developer_permanente'):
                    cache['fecha_verificacion'] = datetime.now().isoformat()
                    with open(self.archivo_config, 'w', encoding='utf-8') as f:
                        json.dump(cache, f, indent=2, ensure_ascii=False)
                
                return {
                    'tipo': cache.get('tipo', 'TRIAL'),
                    'valida': True,
                    'expirada': False,
                    'diasRestantes': cache.get('dias_restantes'),
                    'mensaje': 'Licencia válida (timeout, usando cache)',
                    'desde_cache': True,
                    'developer_permanente': cache.get('es_developer_permanente', False)
                }
            else:
                if mostrar_mensajes:
                    print("❌ Timeout y no hay cache disponible")
                
                return {
                    'tipo': 'TRIAL',
                    'valida': False,
                    'expirada': False,
                    'diasRestantes': None,
                    'mensaje': 'Timeout al verificar licencia',
                    'desde_cache': False,
                    'developer_permanente': False
                }
                
        except Exception as e:
            # Error general - usar cache si existe
            if cache and cache.get('valida'):
                if mostrar_mensajes:
                    print(f"⚠️  Error al verificar ({e}). Usando cache local.")
                
                # Extender fecha de verificación
                if not cache.get('es_developer_permanente'):
                    cache['fecha_verificacion'] = datetime.now().isoformat()
                    with open(self.archivo_config, 'w', encoding='utf-8') as f:
                        json.dump(cache, f, indent=2, ensure_ascii=False)
                
                return {
                    'tipo': cache.get('tipo', 'TRIAL'),
                    'valida': True,
                    'expirada': False,
                    'diasRestantes': cache.get('dias_restantes'),
                    'mensaje': f'Licencia válida (error: {e}, usando cache)',
                    'desde_cache': True,
                    'developer_permanente': cache.get('es_developer_permanente', False)
                }
            else:
                if mostrar_mensajes:
                    print(f"❌ Error: {e}")
                
                return {
                    'tipo': 'TRIAL',
                    'valida': False,
                    'expirada': False,
                    'diasRestantes': None,
                    'mensaje': f'Error al verificar: {e}',
                    'desde_cache': False,
                    'developer_permanente': False
                }

    def verificar_e_iniciar(self, mostrar_mensajes=True):
        """
        Verifica la licencia guardada e inicia la aplicación
        
        Returns:
            dict: Datos de la licencia verificada
        """
        codigo = self.obtener_codigo_guardado()
        
        if not codigo:
            if mostrar_mensajes:
                print("❌ No hay código de licencia guardado")
            return {
                'tipo': 'TRIAL',
                'valida': False,
                'expirada': False,
                'diasRestantes': None,
                'mensaje': 'No hay código de licencia',
                'desde_cache': False,
                'developer_permanente': False
            }
        
        return self.verificar_licencia(codigo, mostrar_mensajes)

    def limpiar_cache(self):
        """Elimina el cache local (fuerza re-verificación)"""
        try:
            if self.archivo_config.exists():
                self.archivo_config.unlink()
                print("✅ Cache eliminado correctamente")
                return True
        except Exception as e:
            print(f"❌ Error al eliminar cache: {e}")
            return False


# Función de compatibilidad para código existente
def verificar_licencia_inicio():
    """Función helper para verificar licencia al inicio (mantiene compatibilidad)"""
    from dialogos_licencia import DialogosLicencia
    
    gestor = GestorLicencias()
    codigo_guardado = gestor.obtener_codigo_guardado()
    
    if not codigo_guardado:
        codigo = DialogosLicencia.solicitar_codigo_licencia()
        if codigo:
            gestor.guardar_codigo_licencia(codigo)
            codigo_guardado = codigo
        else:
            print("❌ No se ingresó código de licencia")
            return None
    
    resultado = gestor.verificar_licencia(codigo_guardado)
    
    if not resultado['valida']:
        DialogosLicencia.mostrar_trial_expirado()
        return None
    
    if resultado.get('developer_permanente'):
        print("👑 Licencia developer permanente activada")
    elif resultado['tipo'] == 'TRIAL':
        DialogosLicencia.mostrar_banner_trial(resultado.get('diasRestantes', 0))
    else:
        print(f"✅ Licencia FULL activada")
    
    return resultado


if __name__ == "__main__":
    # Prueba del gestor
    print("=== Prueba del Gestor de Licencias con Cache ===\n")
    
    gestor = GestorLicencias()
    
    # Opción 1: Probar con código guardado
    print("1. Verificando con código guardado...")
    resultado = gestor.verificar_e_iniciar()
    print(f"Resultado: {resultado}\n")
    
    # Opción 2: Probar con código developer
    print("2. Probando código LIC-DEV-WELLI-001...")
    resultado = gestor.verificar_licencia("LIC-DEV-WELLI-001")
    print(f"Resultado: {resultado}\n")