@echo off
REM Cambiar al directorio donde está este BAT
cd /d "%~dp0"

REM Ejecutar el visualizador de audio en espacio
py EfectoAudioEspacio.py

REM Mantener la ventana abierta al finalizar
pause

