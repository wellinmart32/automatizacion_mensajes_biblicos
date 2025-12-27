@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Enviar Llamados de Oración - WhatsApp

echo.
echo ============================================================
echo      PUBLICADOR DE LLAMADOS DE ORACION
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
