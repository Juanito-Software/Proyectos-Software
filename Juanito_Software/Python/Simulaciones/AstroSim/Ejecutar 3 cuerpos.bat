@echo off
title AstroSim — 3 cuerpos
cd /d "%~dp0"

REM Activar entorno virtual
call venv\Scripts\activate.bat

REM Ejecutar script
python main.py --scenario three_body

pause
