@echo off
REM Cambiar al directorio donde está este .bat / MP3Player.py
cd /d "%~dp0.."

REM Lanzar el reproductor sin dejar la consola abierta
REM Requiere que pythonw.exe esté instalado (viene con Python normal)
start "" /min pythonw.exe MP3Player.py
exit

