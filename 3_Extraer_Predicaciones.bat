@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Extraer Predicaciones de WhatsApp

echo.
echo ============================================================
echo      EXTRACTOR DE PREDICACIONES
echo             Grupo WhatsApp
echo ============================================================
echo.

py extraer_predicaciones_whatsapp.py

echo.
echo ============================================================
echo           Proceso finalizado
echo ============================================================
echo.
exit
