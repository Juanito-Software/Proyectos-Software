@echo off
setlocal

REM ============================================================
REM Ir al directorio del proyecto
REM ============================================================
cd /d "%~dp0"

REM ============================================================
REM Activar entorno virtual
REM ============================================================
call venv\Scripts\activate.bat

REM ============================================================
REM (Opcional pero recomendable) evitar problemas de encoding
REM ============================================================
chcp 65001 >nul

REM ============================================================
REM Ejecutar app principal
REM ============================================================
venv\Scripts\python.exe MultifuncionFPS.py

REM ============================================================
REM Mantener consola abierta para debug
REM ============================================================
pause