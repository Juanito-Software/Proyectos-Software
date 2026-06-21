@echo off
title AstroSim — Órbita simple
cd /d "%~dp0"

REM Activar entorno virtual
call venv\Scripts\activate.bat

REM Ejecutar script
python main.py --scenario orbit

pause
