@echo off
chcp 65001 >nul
title YoutubeToMP4 - Juanito Software
cd /d "%~dp0"
python YoutubeToMp4.py
if errorlevel 1 (
    echo.
    echo ❌ Error al ejecutar el programa.
    echo Verifica que Python esté instalado y las dependencias estén disponibles.
    pause
)
