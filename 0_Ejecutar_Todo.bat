@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Sistema Completo - Facebook + WhatsApp

echo.
echo ============================================================
echo           SISTEMA COMPLETO AUTOMATICO
echo      Mensajes Facebook + Llamados Oracion WhatsApp
echo ============================================================
echo.
echo Este proceso ejecutara:
echo   1. Publicar en Facebook (mensajes biblicos/predicaciones)
echo   2. Enviar llamados de oracion en WhatsApp
echo.
echo ============================================================
echo.

echo ============================================================
echo   PASO 1: PUBLICACION EN FACEBOOK
echo ============================================================
echo.

py flujo_completo_facebook.py

echo.
echo ============================================================
echo   PASO 2: LLAMADOS DE ORACION EN WHATSAPP
echo ============================================================
echo.

py publicadores\whatsapp_oracion.py

echo.
echo ============================================================
echo           Proceso completo finalizado
echo ============================================================
echo.
exit
