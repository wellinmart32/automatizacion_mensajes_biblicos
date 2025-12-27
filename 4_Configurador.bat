@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Configurador del Sistema

echo.
echo ============================================================
echo      CONFIGURADOR INTERACTIVO
echo           Sistema de Automatizacion
echo ============================================================
echo.

py configurador_interactivo.py

echo.
echo ============================================================
echo           Configuracion finalizada
echo ============================================================
echo.
exit
