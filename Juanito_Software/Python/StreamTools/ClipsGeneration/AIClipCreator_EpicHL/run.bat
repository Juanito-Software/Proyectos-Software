@echo off
setlocal

cd /d "%~dp0"

REM Activar entorno virtual
call AIClipCreator_env\Scripts\activate.bat

REM Ejecutar script
python AI-clip-creator\main.py

pause