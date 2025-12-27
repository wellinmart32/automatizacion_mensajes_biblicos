@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Reiniciar Sistema

echo.
echo ============================================================
echo      REINICIADOR DEL SISTEMA
echo           Limpieza y Reset
echo ============================================================
echo.

py reiniciar_sistema.py

echo.
exit
