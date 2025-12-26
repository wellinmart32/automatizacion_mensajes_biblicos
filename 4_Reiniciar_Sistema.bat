@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Reiniciar Sistema - Mensajes Bíblicos

py reiniciar_sistema.py

exit
