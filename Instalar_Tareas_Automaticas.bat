@echo off

:: Verificar si ya tiene permisos de administrador
net session >nul 2>&1
if %errorLevel% == 0 (
    goto :admin
)

:: Si no tiene permisos, auto-elevarse
echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"
"%temp%\getadmin.vbs"
del "%temp%\getadmin.vbs"
exit /B

:admin
chcp 65001 >nul
title Instalar Tareas Programadas - Sistema Evangelio

echo.
echo ════════════════════════════════════════════════════════════
echo        INSTALADOR DE TAREAS PROGRAMADAS
echo           Sistema Completo (Facebook + WhatsApp)
echo ════════════════════════════════════════════════════════════
echo.
echo Este script creara tareas programadas para ejecutar
echo el sistema completo automaticamente varias veces al dia.
echo.
echo TAREAS A CREAR:
echo   • 08:40 - Ejecucion matutina
echo   • 11:00 - Ejecucion media manana
echo   • 13:00 - Ejecucion tarde
echo   • 16:00 - Ejecucion media tarde
echo.
echo Cada ejecucion incluye:
echo   1. Publicacion en Facebook
echo   2. Llamados de oracion en WhatsApp
echo.
echo ════════════════════════════════════════════════════════════
echo.

set SCRIPT_DIR=%~dp0
set SCRIPT_PATH=%SCRIPT_DIR%0_Ejecutar_Todo.bat

echo 📁 Ruta del script: %SCRIPT_PATH%
echo.
pause

echo.
echo ════════════════════════════════════════════════════════════
echo Creando tareas programadas...
echo ════════════════════════════════════════════════════════════
echo.

schtasks /create /tn "Evangelio0840" /tr "\"%SCRIPT_PATH%\"" /sc daily /st 08:40 /f
if %errorlevel% equ 0 (
    echo ✅ Tarea 08:40 creada exitosamente
) else (
    echo ❌ Error creando tarea 08:40
)

schtasks /create /tn "Evangelio1100" /tr "\"%SCRIPT_PATH%\"" /sc daily /st 11:00 /f
if %errorlevel% equ 0 (
    echo ✅ Tarea 11:00 creada exitosamente
) else (
    echo ❌ Error creando tarea 11:00
)

schtasks /create /tn "Evangelio1300" /tr "\"%SCRIPT_PATH%\"" /sc daily /st 13:00 /f
if %errorlevel% equ 0 (
    echo ✅ Tarea 13:00 creada exitosamente
) else (
    echo ❌ Error creando tarea 13:00
)

schtasks /create /tn "Evangelio1600" /tr "\"%SCRIPT_PATH%\"" /sc daily /st 16:00 /f
if %errorlevel% equ 0 (
    echo ✅ Tarea 16:00 creada exitosamente
) else (
    echo ❌ Error creando tarea 16:00
)

echo.
echo ════════════════════════════════════════════════════════════
echo ✅ INSTALACIÓN COMPLETADA
echo ════════════════════════════════════════════════════════════
echo.
echo 📋 Tareas creadas:
echo    1. Evangelio0840 (08:40 - Matutina)
echo    2. Evangelio1100 (11:00 - Media manana)
echo    3. Evangelio1300 (13:00 - Tarde)
echo    4. Evangelio1600 (16:00 - Media tarde)
echo.
echo 💡 Para verificar:
echo    - Presiona Win + R
echo    - Escribe: taskschd.msc
echo    - Presiona Enter
echo    - Busca: Evangelio0840, Evangelio1100, etc.
echo.
echo 🗑️  Para eliminar las tareas:
echo    - Ejecuta "Desinstalar_Tareas_Automaticas.bat"
echo.
pause
