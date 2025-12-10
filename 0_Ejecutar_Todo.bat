@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Flujo Completo Automático - Facebook

echo.
echo ============================================================
echo           FLUJO COMPLETO AUTOMATICO
echo        Mensajes Biblicos + Predicaciones WhatsApp
echo ============================================================
echo.
echo Este proceso ejecutara automaticamente:
echo   1. Verificar predicaciones pendientes
echo   2. Extraer mas predicaciones SI es necesario
echo   3. Publicar en Facebook (alternancia 1:1)
echo.
echo ============================================================
echo.

py flujo_completo_facebook.py

echo.
echo ============================================================
echo           Proceso finalizado
echo ============================================================
echo.
exit
