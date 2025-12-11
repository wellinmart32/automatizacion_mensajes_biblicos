@echo off
chcp 65001 >nul

REM ============================================================
REM VERIFICAR Y SOLICITAR PERMISOS DE ADMINISTRADOR
REM ============================================================
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"

if '%errorlevel%' NEQ '0' (
    echo.
    echo ════════════════════════════════════════════════════════════
    echo   ⚠️  PERMISOS DE ADMINISTRADOR REQUERIDOS
    echo ════════════════════════════════════════════════════════════
    echo.
    echo Este script requiere permisos de administrador.
    echo Solicitando permisos...
    echo.
    goto UACPrompt
) else ( goto gotAdmin )

:UACPrompt
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"
    "%temp%\getadmin.vbs"
    exit /B

:gotAdmin
    if exist "%temp%\getadmin.vbs" ( del "%temp%\getadmin.vbs" )
    pushd "%CD%"
    CD /D "%~dp0"

REM ============================================================
REM SCRIPT PRINCIPAL
REM ============================================================
echo.
echo ════════════════════════════════════════════════════════════
echo      INSTALADOR DE TAREAS PROGRAMADAS - FACEBOOK
echo        Mensajes Bíblicos + Predicaciones WhatsApp
echo ════════════════════════════════════════════════════════════
echo.
echo Este script creará 4 tareas programadas:
echo   - 08:40 - Publicación matutina
echo   - 11:00 - Publicación media mañana
echo   - 13:00 - Publicación tarde
echo   - 16:00 - Publicación media tarde
echo.
echo ════════════════════════════════════════════════════════════
echo.

REM Obtener la ruta del proyecto
set "PROYECTO_DIR=%~dp0"
set "PROYECTO_DIR=%PROYECTO_DIR:~0,-1%"

echo 📁 Ruta del proyecto: %PROYECTO_DIR%
echo.

REM Verificar que el archivo principal existe
if not exist "%PROYECTO_DIR%\0_Ejecutar_Todo.bat" (
    echo ❌ ERROR: No se encuentra 0_Ejecutar_Todo.bat
    echo    Verifica que estás ejecutando este script desde la carpeta del proyecto
    pause
    exit /b 1
)

echo ✅ Archivo principal encontrado
echo ✅ Permisos de administrador: ACTIVOS
echo.
pause

echo.
echo ════════════════════════════════════════════════════════════
echo Creando tareas programadas...
echo ════════════════════════════════════════════════════════════
echo.

REM Eliminar tareas existentes primero (para evitar duplicados)
echo 🔍 Eliminando tareas existentes (si hay)...
schtasks /delete /tn FacebookAuto0840 /f 2>nul
schtasks /delete /tn FacebookAuto1100 /f 2>nul
schtasks /delete /tn FacebookAuto1300 /f 2>nul
schtasks /delete /tn FacebookAuto1600 /f 2>nul
echo.

REM ============================================================
REM TAREA 1: 08:40 - Publicación matutina
REM ============================================================
echo 📌 Creando tarea: FacebookAuto0840...

schtasks /create /tn FacebookAuto0840 /tr %PROYECTO_DIR%\0_Ejecutar_Todo.bat /sc daily /st 08:40 /f

if %errorlevel% equ 0 (
    echo    ✅ Tarea 08:40 creada exitosamente
) else (
    echo    ❌ Error creando tarea 08:40 - Código: %errorlevel%
)
echo.

REM ============================================================
REM TAREA 2: 11:00 - Publicación media mañana
REM ============================================================
echo 📌 Creando tarea: FacebookAuto1100...

schtasks /create /tn FacebookAuto1100 /tr %PROYECTO_DIR%\0_Ejecutar_Todo.bat /sc daily /st 11:00 /f

if %errorlevel% equ 0 (
    echo    ✅ Tarea 11:00 creada exitosamente
) else (
    echo    ❌ Error creando tarea 11:00 - Código: %errorlevel%
)
echo.

REM ============================================================
REM TAREA 3: 13:00 - Publicación tarde
REM ============================================================
echo 📌 Creando tarea: FacebookAuto1300...

schtasks /create /tn FacebookAuto1300 /tr %PROYECTO_DIR%\0_Ejecutar_Todo.bat /sc daily /st 13:00 /f

if %errorlevel% equ 0 (
    echo    ✅ Tarea 13:00 creada exitosamente
) else (
    echo    ❌ Error creando tarea 13:00 - Código: %errorlevel%
)
echo.

REM ============================================================
REM TAREA 4: 16:00 - Publicación media tarde
REM ============================================================
echo 📌 Creando tarea: FacebookAuto1600...

schtasks /create /tn FacebookAuto1600 /tr %PROYECTO_DIR%\0_Ejecutar_Todo.bat /sc daily /st 16:00 /f

if %errorlevel% equ 0 (
    echo    ✅ Tarea 16:00 creada exitosamente
) else (
    echo    ❌ Error creando tarea 16:00 - Código: %errorlevel%
)
echo.

echo ════════════════════════════════════════════════════════════
echo ✅ INSTALACIÓN COMPLETADA
echo ════════════════════════════════════════════════════════════
echo.
echo 📋 Tareas creadas:
echo    1. FacebookAuto0840 (08:40 - Matutina)
echo    2. FacebookAuto1100 (11:00 - Media mañana)
echo    3. FacebookAuto1300 (13:00 - Tarde)
echo    4. FacebookAuto1600 (16:00 - Media tarde)
echo.
echo 💡 Para verificar:
echo    - Presiona Win + R
echo    - Escribe: taskschd.msc
echo    - Presiona Enter
echo    - Busca: FacebookAuto0840, FacebookAuto1100, etc.
echo.
echo 🗑️  Para eliminar las tareas:
echo    - Ejecuta "Desinstalar_Tareas_Automaticas.bat"
echo.
echo 🧪 Para probar manualmente:
echo    - Abre Programador de Tareas (taskschd.msc)
echo    - Clic derecho en una tarea
echo    - Selecciona "Ejecutar"
echo.
echo 📅 Las tareas se ejecutarán automáticamente todos los días
echo    a las horas configuradas (08:40, 11:00, 13:00, 16:00)
echo.
pause
