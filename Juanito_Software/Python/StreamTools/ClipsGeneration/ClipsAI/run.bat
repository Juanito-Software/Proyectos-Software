@echo off
setlocal

echo Iniciando Cuenta Atras para OBS...
echo.

cd /d "%~dp0"

REM Activar entorno virtual
call ClipsAI_env\Scripts\activate.bat

REM Ejecutar script
python auto_clips.py

pause