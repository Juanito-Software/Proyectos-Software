@echo off
setlocal

cd /d "%~dp0"

REM Activar entorno virtual
call venv\Scripts\activate.bat

REM Ejecutar script
python servidor_ftp.py

pause