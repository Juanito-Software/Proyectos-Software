@echo off

cd /d "%~dp0"

REM Lanzar el reproductor sin dejar la consola abierta
REM Requiere que pythonw.exe esté instalado (viene con Python normal)
start "" /min pythonw.exe EnviarArchivos.py
exit

