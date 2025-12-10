@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Publicador Automático Facebook - Mensajes Bíblicos

echo.
echo ============================================================
echo      PUBLICADOR AUTOMATICO DE FACEBOOK
echo           Mensajes Biblicos
echo ============================================================
echo.

py automatizacion_mensajes_biblicos.py

echo.
echo ============================================================
echo           Proceso finalizado
echo ============================================================
echo.
pause
