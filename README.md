# 🚀 Publicador Automático de Facebook - Mensajes Bíblicos

Sistema modular profesional para publicar automáticamente mensajes bíblicos en Facebook con sistema de memoria inteligente que evita repetir los últimos 5 mensajes publicados.

---

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Requisitos](#-requisitos)
- [Instalación](#-instalación)
- [Migración desde Versión Anterior](#-migración-desde-versión-anterior)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Configuración](#-configuración)
- [Uso](#-uso)
- [Tareas Programadas](#-tareas-programadas)
- [Sistema de Memoria](#-sistema-de-memoria)
- [Solución de Problemas](#-solución-de-problemas)
- [Mantenimiento](#-mantenimiento)

---

## ✨ Características

### **Sistema de Memoria Inteligente**
- 🧠 **Evita repeticiones**: Bloquea los últimos 5 mensajes publicados
- 📊 **Estadísticas completas**: Registro de todas las publicaciones
- 🎲 **Selección aleatoria**: Entre los mensajes disponibles
- 📈 **Tracking completo**: Sabe cuál es el mensaje más publicado

### **Configuración Flexible**
- ⚙️ **Todo configurable**: Sin tocar código
- 🔄 **Reintentos automáticos**: Hasta 3 intentos por publicación
- 🌐 **Multi-navegador**: Firefox o Chrome
- 🕒 **Control de tiempo**: Evita publicaciones duplicadas

### **Arquitectura Profesional**
- 📦 **Modular**: Fácil de mantener y extender
- 🎯 **Separación de responsabilidades**: Cada módulo una función
- 🔒 **Git-ready**: Con `.gitignore` incluido
- 📝 **Bien documentado**: Comentarios en español

---

## 🔧 Requisitos

### **Software Necesario:**
- **Python 3.8+**
- **Firefox** (recomendado) o **Chrome**
- **Windows 10/11** (para tareas programadas)

### **Python debe estar instalado y en PATH**
Verifica ejecutando en CMD:
```bash
py --version
```

Si no funciona, reinstala Python marcando "Add to PATH".

---

## 📥 Instalación

### **1. Preparar el Proyecto**

Si es tu primera vez:
```bash
# Navegar a tu carpeta de repositorios
cd C:\Users\TU_USUARIO\OneDrive\Documents\Repositorios

# Crear carpeta del proyecto
mkdir automatizacion-mensajes-biblicos
cd automatizacion-mensajes-biblicos
```

### **2. Copiar Archivos del Sistema**

Copia todos los archivos descargados a la carpeta del proyecto:
```
automatizacion-mensajes-biblicos/
├── compartido/
│   ├── __init__.py
│   └── gestor_archivos.py
├── publicadores/
│   ├── __init__.py
│   └── publicador_facebook.py
├── mensajes/                    ← Crea esta carpeta
├── .gitignore
├── config_global.txt
├── gestor_registro.py
├── publicar_facebook.py
├── configurador_interactivo.py
├── requirements.txt
├── 1_Publicar_Facebook.bat
└── 2_Configurador.bat
```

### **3. Agregar tus Mensajes**

Copia tus 21 archivos `.txt` a la carpeta `mensajes/`:
```
mensajes/
├── mensaje-001.txt
├── mensaje-002.txt
├── ...
└── mensaje-021.txt
```

### **4. Instalar Dependencias**

Abre CMD en la carpeta del proyecto y ejecuta:
```bash
pip install -r requirements.txt
```

Esto instalará:
- `selenium` - Automatización del navegador
- `webdriver-manager` - Gestión de ChromeDriver
- `pyperclip` - Manejo del portapapeles

### **5. Verificar Instalación**

Ejecuta el configurador para verificar:
```bash
py configurador_interactivo.py
```

Si ves el menú de configuración, ¡todo está listo! ✅

---

## 🔄 Migración desde Versión Anterior

Si ya tenías el sistema viejo (`automatizacion_mensajes_biblicos.py`), sigue estos pasos:

### **Paso 1: Backup (Opcional)**
```bash
# Hacer copia de seguridad
xcopy automatizacion_mensajes_biblicos automatizacion_mensajes_biblicos_BACKUP /E /I
```

### **Paso 2: Renombrar Proyecto**
```bash
cd C:\Users\TU_USUARIO\OneDrive\Documents\Repositorios
rename automatizacion_mensajes_biblicos automatizacion-mensajes-biblicos
cd automatizacion-mensajes-biblicos
```

### **Paso 3: Limpiar Archivos Viejos**
Elimina estos archivos:
- ❌ `automatizacion_mensajes_biblicos.py`
- ❌ `iniciar_publicacion_automatica.bat`
- ❌ Cualquier archivo de capturas antiguo

### **Paso 4: Crear Estructura**
```bash
mkdir compartido
mkdir publicadores
mkdir mensajes
```

### **Paso 5: Mover Mensajes**
```bash
move mensaje-*.txt mensajes\
```

### **Paso 6: Copiar Archivos Nuevos**
Copia todos los archivos del sistema nuevo (ver [Instalación](#-instalación)).

### **Paso 7: Instalar Dependencias**
```bash
pip install -r requirements.txt
```

### **Paso 8: Probar**
```bash
# Doble clic en:
1_Publicar_Facebook.bat
```

---

## 📁 Estructura del Proyecto

```
automatizacion-mensajes-biblicos/
│
├── 📁 compartido/              # Módulo de funciones compartidas
│   ├── __init__.py
│   └── gestor_archivos.py     # Manejo de archivos y configuración
│
├── 📁 publicadores/            # Módulo de publicadores
│   ├── __init__.py
│   └── publicador_facebook.py # Lógica de Selenium/Facebook
│
├── 📁 mensajes/                # Tus 21 mensajes bíblicos
│   ├── mensaje-001.txt
│   ├── mensaje-002.txt
│   └── ...
│
├── 📁 perfiles/                # Perfiles del navegador (auto-generado)
│   └── facebook_publicador/
│
├── 📄 .gitignore               # Protege archivos sensibles
├── 📄 config_global.txt        # ⭐ Configuración del sistema
├── 📄 registro_publicaciones.json  # Historial y memoria (auto-generado)
│
├── 📄 gestor_registro.py       # Manejo del registro
├── 📄 publicar_facebook.py     # ⭐ Script principal
├── 📄 configurador_interactivo.py  # Configurador visual
│
├── 📄 1_Publicar_Facebook.bat  # ⭐ Acceso directo principal
├── 📄 2_Configurador.bat       # Acceso directo al configurador
│
├── 📄 requirements.txt         # Dependencias Python
└── 📄 README.md               # Este archivo
```

### **Archivos Importantes:**

| Archivo | Propósito |
|---------|-----------|
| `config_global.txt` | Toda la configuración del sistema |
| `registro_publicaciones.json` | Historial + memoria de últimos 5 |
| `1_Publicar_Facebook.bat` | Ejecuta una publicación |
| `2_Configurador.bat` | Modifica configuración |

---

## ⚙️ Configuración

### **Configuración Básica**

El archivo `config_global.txt` contiene toda la configuración:

```ini
[GENERAL]
# Carpeta donde están tus mensajes
carpeta_mensajes = mensajes

[MENSAJES]
# Método de selección: aleatoria o secuencial
seleccion = aleatoria

# Cantidad de mensajes a evitar (memoria)
historial_evitar_repetir = 5

# Agregar hashtags automáticamente
agregar_hashtags = si
hashtags = #fe #biblia #cristianismo #predica

[PUBLICACION]
# Segundos entre reintentos si falla
tiempo_entre_intentos = 3

# Máximo de intentos por publicación
max_intentos_por_publicacion = 3

# Segundos de espera para estabilizar el modal
espera_estabilizacion_modal = 3

[LIMITES]
# Tiempo mínimo entre publicaciones (evita duplicados)
tiempo_minimo_entre_publicaciones_segundos = 120

# Permitir forzar publicación manual
permitir_forzar_publicacion_manual = si

[NAVEGADOR]
# Navegador a usar: firefox o chrome
navegador = firefox

# Usar perfil existente (recomendado)
usar_perfil_existente = si
```

### **Modificar Configuración**

**Opción 1: Configurador Visual (Recomendado)**
```bash
# Doble clic en:
2_Configurador.bat
```

**Opción 2: Editar Archivo Directamente**
```bash
notepad config_global.txt
```

### **Configuraciones Comunes:**

#### **Cambiar navegador a Chrome:**
```ini
[NAVEGADOR]
navegador = chrome
```

#### **Cambiar memoria a últimos 3:**
```ini
[MENSAJES]
historial_evitar_repetir = 3
```

#### **Desactivar hashtags:**
```ini
[MENSAJES]
agregar_hashtags = no
```

---

## 🎯 Uso

### **Publicación Manual**

Para publicar un mensaje manualmente:

1. **Doble clic en:** `1_Publicar_Facebook.bat`
2. El sistema automáticamente:
   - ✅ Verifica la configuración
   - ✅ Muestra estadísticas
   - ✅ Selecciona un mensaje (evitando últimos 5)
   - ✅ Abre Firefox/Chrome
   - ✅ Publica en Facebook
   - ✅ Registra la publicación
   - ✅ Cierra el navegador

### **Primera Ejecución**

La primera vez que ejecutes:

1. **Firefox se abrirá** en WhatsApp/Facebook
2. **Inicia sesión** en Facebook si no lo has hecho
3. **Espera** a que se complete el login
4. El sistema continuará automáticamente

**Nota:** El perfil se guarda, no tendrás que volver a iniciar sesión.

### **Ejecución Normal**

Ejecuciones posteriores:
```
1. Sistema verifica tiempo mínimo (120s desde última publicación)
2. Carga mensajes disponibles (21 - 5 bloqueados = 16 disponibles)
3. Selecciona uno aleatoriamente
4. Muestra preview del mensaje
5. Publica en Facebook
6. Muestra estadísticas actualizadas
```

### **Salida Típica:**

```
======================================================================
               🚀 PUBLICADOR AUTOMÁTICO DE FACEBOOK
                    Sistema de Mensajes Bíblicos
======================================================================

⚙️  CONFIGURACIÓN DEL SISTEMA:
   📁 Carpeta mensajes: mensajes
   🌐 Navegador: FIREFOX
   🎲 Selección: Aleatoria
   💾 Memoria: Últimos 5 mensajes
   🔄 Máx. intentos: 3

============================================================
               📊 ESTADÍSTICAS DEL SISTEMA
============================================================
📈 Total publicaciones:        48
✅ Exitosas:                   46
❌ Fallidas:                   2
🎯 Tasa de éxito:              95.8%
🔥 Mensaje más publicado:      mensaje-001.txt
💾 Mensajes en memoria:        5
============================================================

🎯 SELECCIÓN DE MENSAJE:
   Método: Aleatorio (evitando últimos publicados)
📦 Total de mensajes disponibles: 21
🚫 Mensajes bloqueados (últimos 5): 5
✅ Mensajes disponibles: 16

🎲 Mensaje seleccionado: mensaje-012.txt

🌐 Iniciando FIREFOX...
✅ Navegador iniciado correctamente

🔐 Verificando sesión de Facebook...
✅ Ya tienes sesión activa en Facebook

📝 Abriendo compositor de publicación...
✅ Clic exitoso
✅ Modal confirmado abierto

✍️  Ingresando texto...
✅ Texto ingresado correctamente (608 caracteres)

🚀 Buscando botón 'Publicar'...
✅ Clic en 'Publicar'

======================================================================
✅ ¡PUBLICACIÓN EXITOSA!
======================================================================
📄 Mensaje: mensaje-012.txt
🔄 Intentos: 1
⏱️  Tiempo: 14.2s
======================================================================
```

---

## ⏰ Tareas Programadas

### **Configurar Publicaciones Automáticas**

Para que se publique automáticamente varias veces al día:

#### **Paso 1: Abrir Programador de Tareas**
1. Presiona `Win + R`
2. Escribe: `taskschd.msc`
3. Enter

#### **Paso 2: Crear Nueva Tarea**
1. Clic derecho en "Biblioteca del Programador de tareas"
2. "Crear tarea..."

#### **Paso 3: Configurar General**
```
Nombre: Publicar Mensaje Facebook - 08:40
Descripción: Publica mensaje bíblico automáticamente
☑️ Ejecutar con los privilegios más altos
```

#### **Paso 4: Configurar Desencadenador**
```
Nuevo → Diario
Hora: 08:40:00
Repetir cada: -
☑️ Habilitado
```

#### **Paso 5: Configurar Acción**
```
Acción: Iniciar un programa
Programa: py
Argumentos: publicar_facebook.py
Iniciar en: C:\Users\TU_USUARIO\...\automatizacion-mensajes-biblicos
```

#### **Paso 6: Repetir para Más Horarios**

Crea 4 tareas con estos horarios:
- ⏰ **08:40** - Mañana
- ⏰ **11:00** - Media mañana
- ⏰ **13:00** - Tarde
- ⏰ **16:00** - Media tarde

### **Verificar Tareas**

Para ver si funcionan:
1. En Programador de Tareas
2. Busca tus tareas
3. Clic derecho → "Ejecutar"
4. Observa si publica correctamente

---

## 🧠 Sistema de Memoria

### **¿Cómo Funciona?**

El sistema mantiene un **historial de los últimos 5 mensajes publicados** y los bloquea temporalmente:

```
Publicación 1: mensaje-007.txt  → Bloqueado por 5 turnos
Publicación 2: mensaje-012.txt  → Bloqueado por 5 turnos
Publicación 3: mensaje-003.txt  → Bloqueado por 5 turnos
Publicación 4: mensaje-019.txt  → Bloqueado por 5 turnos
Publicación 5: mensaje-015.txt  → Bloqueado por 5 turnos
Publicación 6: mensaje-021.txt  → mensaje-007.txt ya disponible ✅
```

### **Matemática de la Memoria**

Con 21 mensajes y memoria de 5:
- **Mensajes disponibles:** 21 - 5 = **16 opciones**
- **Rotación completa:** Después de ~21 publicaciones
- **Probabilidad de repetición inmediata:** 0% (bloqueado)

### **Ver Mensajes Bloqueados**

Al ejecutar `1_Publicar_Facebook.bat` verás:

```
============================================================
🚫 MENSAJES BLOQUEADOS (Últimos 5 publicados)
============================================================
  1. mensaje-019.txt
  2. mensaje-007.txt
  3. mensaje-015.txt
  4. mensaje-003.txt
  5. mensaje-012.txt
============================================================
```

### **Cambiar Tamaño de Memoria**

En `config_global.txt`:
```ini
[MENSAJES]
# Evitar últimos 3 (en lugar de 5)
historial_evitar_repetir = 3
```

**Recomendaciones:**
- **3 mensajes:** Más repetición, útil si tienes pocos mensajes
- **5 mensajes:** Balance perfecto (recomendado)
- **7 mensajes:** Menos repetición, requiere más mensajes

---

## 🔧 Solución de Problemas

### **❌ Error: "No se encontró el archivo config_global.txt"**

**Causa:** No está en la carpeta correcta.

**Solución:**
```bash
# Verifica que estás en la carpeta del proyecto
cd C:\Users\TU_USUARIO\...\automatizacion-mensajes-biblicos

# Verifica que existe el archivo
dir config_global.txt
```

---

### **❌ Error: "No module named 'selenium'"**

**Causa:** No instalaste las dependencias.

**Solución:**
```bash
pip install -r requirements.txt
```

---

### **❌ Error: "No se pudo iniciar el navegador"**

**Causa:** Firefox/Chrome no está instalado o no se encuentra.

**Solución para Firefox:**
```bash
# Verifica que Firefox está instalado
"C:\Program Files\Mozilla Firefox\firefox.exe"
```

**Solución para Chrome:**
```ini
# Cambiar a Chrome en config_global.txt
[NAVEGADOR]
navegador = chrome
```

---

### **❌ Error: "No se encontró el área de texto"**

**Causa:** Facebook cambió su interfaz.

**Solución temporal:**
1. Espera 10 segundos y reintenta
2. Si persiste, reporta el error (Facebook actualiza su interfaz frecuentemente)

---

### **❌ Error: "Límite de tiempo alcanzado"**

**Causa:** Publicaste hace menos de 2 minutos.

**Solución:**
- Espera 2 minutos y reintenta
- O desactiva el límite en `config_global.txt`:
```ini
[LIMITES]
tiempo_minimo_entre_publicaciones_segundos = 30
```

---

### **⚠️ El mensaje no se publicó correctamente**

**Diagnóstico:**

1. **Revisa `registro_publicaciones.json`:**
```json
{
  "errores": [
    {
      "fecha": "2024-12-09 10:15:00",
      "mensaje_archivo": "mensaje-012.txt",
      "error": "No se encontró el botón Publicar"
    }
  ]
}
```

2. **Verifica tu sesión de Facebook:**
   - Abre Firefox manualmente
   - Ve a facebook.com
   - Verifica que estás logueado

3. **Aumenta tiempo de estabilización:**
```ini
[PUBLICACION]
espera_estabilizacion_modal = 5
```

---

### **🐛 Modo Debug Avanzado**

Para ver más información:

```ini
[DEBUG]
modo_debug = detallado
```

Esto mostrará más detalles durante la ejecución.

---

## 🛠️ Mantenimiento

### **Ver Estadísticas**

Ejecuta el sistema y revisa las estadísticas mostradas:
```
📈 Total publicaciones:        145
✅ Exitosas:                   142
❌ Fallidas:                   3
🎯 Tasa de éxito:              97.9%
🔥 Mensaje más publicado:      mensaje-001.txt
```

### **Limpiar Historial**

Si quieres empezar de cero:
```bash
# Eliminar registro
del registro_publicaciones.json

# Próxima ejecución creará uno nuevo
```

### **Agregar Más Mensajes**

1. Crea nuevos archivos `.txt` en `mensajes/`
2. Nombra siguiendo el patrón: `mensaje-022.txt`, `mensaje-023.txt`, etc.
3. ¡Listo! El sistema los detectará automáticamente

### **Actualizar Mensajes Existentes**

1. Edita directamente los archivos en `mensajes/`
2. Los cambios se aplicarán en la próxima publicación

### **Backup del Sistema**

**Archivos importantes a respaldar:**
```
- mensajes/                     ← Tus mensajes
- config_global.txt            ← Tu configuración
- registro_publicaciones.json  ← Tu historial
```

**Backup rápido:**
```bash
# Crear backup con fecha
xcopy mensajes mensajes_BACKUP_%date% /E /I
copy config_global.txt config_global_BACKUP.txt
copy registro_publicaciones.json registro_BACKUP.json
```

---

## 🎓 Uso Avanzado

### **Selección Secuencial**

Si prefieres publicar en orden:
```ini
[MENSAJES]
seleccion = secuencial
```

Publicará: `mensaje-001.txt`, `mensaje-002.txt`, etc.

### **Personalizar Horarios**

Modifica las tareas programadas según tu audiencia:
- **Mañana:** 07:00 (personas leyendo antes del trabajo)
- **Almuerzo:** 12:00 (break del mediodía)
- **Tarde:** 15:00 (descanso de la tarde)
- **Noche:** 20:00 (después de la cena)

### **Usar Perfil Custom**

Si no quieres usar tu perfil de Firefox:
```ini
[NAVEGADOR]
usar_perfil_existente = no
carpeta_perfil_custom = perfiles/facebook_publicador
```

---

## 📞 Soporte

### **¿Problemas?**

1. Revisa la sección [Solución de Problemas](#-solución-de-problemas)
2. Verifica el archivo `registro_publicaciones.json` (sección `errores`)
3. Activa modo debug y revisa la salida

### **¿Sugerencias?**

Este sistema está diseñado para ser expandible. Próximas funcionalidades planeadas:
- 🎬 Publicación de prédicas desde WhatsApp
- 📊 Dashboard web con estadísticas
- 📱 Notificaciones por email
- 🌍 Soporte para múltiples redes sociales

---

## 📄 Licencia

Este proyecto es de uso personal/ministerial.

---

## 🙏 Créditos

Desarrollado para automatizar la difusión de mensajes bíblicos en redes sociales.

**Tecnologías utilizadas:**
- Python 3.8+
- Selenium WebDriver
- Firefox/Chrome

---

## 📚 Documentación Adicional

- **Selenium:** https://selenium-python.readthedocs.io/
- **Python ConfigParser:** https://docs.python.org/3/library/configparser.html
- **Tareas Programadas Windows:** https://learn.microsoft.com/es-es/windows/win32/taskschd/

---

**Última actualización:** Diciembre 2024  
**Versión:** 2.0.0 (Sistema Modular)

---

✨ **¡Que Dios bendiga tu ministerio digital!** ✨
