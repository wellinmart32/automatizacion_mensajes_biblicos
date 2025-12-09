@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Configurador del Sistema

echo.
echo ============================================================
echo              CONFIGURADOR DEL SISTEMA
echo           Publicador Automatico de Facebook
echo ============================================================
echo.

python configurador_interactivo.py

pause
