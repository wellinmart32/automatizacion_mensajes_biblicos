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
title Desinstalar Tareas Programadas - Sistema Evangelio

echo.
echo ════════════════════════════════════════════════════════════
echo        DESINSTALADOR DE TAREAS PROGRAMADAS
echo           Sistema Completo (Facebook + WhatsApp)
echo ════════════════════════════════════════════════════════════
echo.
echo Este script eliminara todas las tareas programadas del sistema.
echo.
echo TAREAS A ELIMINAR:
echo   • Evangelio0840 (08:40)
echo   • Evangelio1100 (11:00)
echo   • Evangelio1300 (13:00)
echo   • Evangelio1600 (16:00)
echo.
echo ════════════════════════════════════════════════════════════
echo.
pause

echo.
echo ════════════════════════════════════════════════════════════
echo Eliminando tareas programadas...
echo ════════════════════════════════════════════════════════════
echo.

schtasks /delete /tn "Evangelio0840" /f
if %errorlevel% equ 0 (
    echo ✅ Tarea 08:40 eliminada
) else (
    echo ⚠️  Tarea 08:40 no encontrada o ya eliminada
)

schtasks /delete /tn "Evangelio1100" /f
if %errorlevel% equ 0 (
    echo ✅ Tarea 11:00 eliminada
) else (
    echo ⚠️  Tarea 11:00 no encontrada o ya eliminada
)

schtasks /delete /tn "Evangelio1300" /f
if %errorlevel% equ 0 (
    echo ✅ Tarea 13:00 eliminada
) else (
    echo ⚠️  Tarea 13:00 no encontrada o ya eliminada
)

schtasks /delete /tn "Evangelio1600" /f
if %errorlevel% equ 0 (
    echo ✅ Tarea 16:00 eliminada
) else (
    echo ⚠️  Tarea 16:00 no encontrada o ya eliminada
)

echo.
echo ════════════════════════════════════════════════════════════
echo ✅ DESINSTALACIÓN COMPLETADA
echo ════════════════════════════════════════════════════════════
echo.
pause
