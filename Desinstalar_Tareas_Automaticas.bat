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
echo ============================================================
echo   DESINSTALADOR DE TAREAS PROGRAMADAS - FACEBOOK
echo ============================================================
echo.
echo Este script eliminará todas las tareas programadas de Facebook
echo.
echo ⚠️  ¿Estás seguro que quieres continuar?
echo.
pause

echo.
echo ============================================================
echo Eliminando tareas programadas...
echo ============================================================
echo.

echo 🔍 Buscando tareas instaladas...
echo.

REM Listar tareas antes de eliminar
schtasks /query /fo list | findstr /C:"FacebookAuto"

echo.
echo ────────────────────────────────────────────────────────────
echo.

REM Eliminar tareas con nombres simplificados
echo 📌 Eliminando FacebookAuto0840...
schtasks /delete /tn FacebookAuto0840 /f
if %errorlevel% equ 0 (
    echo    ✅ FacebookAuto0840 eliminada
) else (
    echo    ⚠️  FacebookAuto0840 no encontrada
)
echo.

echo 📌 Eliminando FacebookAuto1100...
schtasks /delete /tn FacebookAuto1100 /f
if %errorlevel% equ 0 (
    echo    ✅ FacebookAuto1100 eliminada
) else (
    echo    ⚠️  FacebookAuto1100 no encontrada
)
echo.

echo 📌 Eliminando FacebookAuto1300...
schtasks /delete /tn FacebookAuto1300 /f
if %errorlevel% equ 0 (
    echo    ✅ FacebookAuto1300 eliminada
) else (
    echo    ⚠️  FacebookAuto1300 no encontrada
)
echo.

echo 📌 Eliminando FacebookAuto1600...
schtasks /delete /tn FacebookAuto1600 /f
if %errorlevel% equ 0 (
    echo    ✅ FacebookAuto1600 eliminada
) else (
    echo    ⚠️  FacebookAuto1600 no encontrada
)
echo.

REM Eliminar tareas con nombres antiguos (si existen)
echo 🔍 Buscando tareas con nombres antiguos...
schtasks /delete /tn "Facebook Auto - 08:40 Matutina" /f 2>nul
schtasks /delete /tn "Facebook Auto - 11:00 Media Manana" /f 2>nul
schtasks /delete /tn "Facebook Auto - 11:00 Media Mañana" /f 2>nul
schtasks /delete /tn "Facebook Auto - 13:00 Tarde" /f 2>nul
schtasks /delete /tn "Facebook Auto - 16:00 Media Tarde" /f 2>nul
schtasks /delete /tn "Facebook Test - Metodo 1" /f 2>nul
schtasks /delete /tn "Facebook Test - Metodo 2" /f 2>nul
schtasks /delete /tn "Facebook Test - Metodo 3" /f 2>nul
schtasks /delete /tn "Facebook Test - Metodo 4" /f 2>nul
schtasks /delete /tn "Facebook Test - Metodo 5" /f 2>nul

echo.
echo ────────────────────────────────────────────────────────────
echo.
echo 🔍 Verificando que se eliminaron...
schtasks /query /fo list | findstr /C:"FacebookAuto" /C:"Facebook Auto" /C:"Facebook Test"

if %errorlevel% equ 0 (
    echo.
    echo ⚠️  Algunas tareas aún existen
) else (
    echo.
    echo ✅ Todas las tareas fueron eliminadas
)

echo.
echo ============================================================
echo ✅ DESINSTALACIÓN COMPLETADA
echo ============================================================
echo.
echo 💡 Verifica en Programador de Tareas (taskschd.msc)
echo.
pause
