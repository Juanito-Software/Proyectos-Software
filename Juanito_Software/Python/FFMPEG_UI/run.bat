@echo off
setlocal

cd /d "%~dp0"

REM --------------------------------------------------
REM Verificar entorno virtual
REM --------------------------------------------------
if not exist "env_Py3.10\Scripts\python.exe" (
    echo [ERROR] No se encuentra el entorno virtual 'env_Py3.10'
    echo [INFO] Crear con: python -m venv env_Py3.10
    pause
    exit /b 1
)

echo ==========================================
echo   FFmpeg Converter - Ejecucion
echo ==========================================
echo.

REM --------------------------------------------------
REM Ejecutar directamente desde el venv (recomendado)
REM --------------------------------------------------
echo [OK] Usando entorno virtual env_Py3.10
echo.

env_Py3.10\Scripts\python.exe FFmpegConverter.py

echo.
echo Programa finalizado.
pause