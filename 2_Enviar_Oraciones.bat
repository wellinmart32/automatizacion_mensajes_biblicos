@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Enviar Solo Llamados de Oración

echo.
echo ============================================================
echo      PUBLICADOR SOLO ORACIONES
echo             WhatsApp Web - Grupos
echo ============================================================
echo.

py publicadores\whatsapp_oracion.py

echo.
echo ============================================================
echo           Proceso finalizado
echo ============================================================
echo.
exit
