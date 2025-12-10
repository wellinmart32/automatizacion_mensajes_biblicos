@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Extractor de Predicaciones WhatsApp

echo.
echo ============================================================
echo      EXTRACTOR DE PREDICACIONES DE WHATSAPP
echo           Sistema de Predicaciones Automaticas
echo ============================================================
echo.

py extraer_predicaciones_whatsapp.py

echo.
echo ============================================================
echo           Proceso finalizado
echo ============================================================
echo.
exit
