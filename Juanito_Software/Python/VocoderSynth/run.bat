@echo off
REM Cambia al directorio donde está este archivo .bat
cd /d "%~dp0"

echo Iniciando vocoder en tiempo real...
echo Cierra esta ventana o pulsa Ctrl+C para detener.
echo.

REM Ejecuta el script de Python
py vocoder_realtime.py

echo.
echo El programa ha finalizado.
pause
