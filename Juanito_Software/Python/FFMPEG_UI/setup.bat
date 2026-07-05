@echo off
setlocal

echo ==========================================
echo   FFmpeg Converter - Setup
echo ==========================================
echo.

REM --------------------------------------------------
REM Comprobar Python global (solo para crear venv si no existe)
REM --------------------------------------------------
echo Comprobando Python del sistema...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado o no esta en PATH
    pause
    exit /b 1
)

echo [OK] Python detectado
echo.

REM --------------------------------------------------
REM Crear entorno virtual si no existe
REM --------------------------------------------------
if not exist "env_Py3.10\Scripts\python.exe" (
    echo [INFO] Creando entorno virtual env_Py3.10...
    python -m venv env_Py3.10
) else (
    echo [OK] Entorno virtual ya existe
)

echo.

REM --------------------------------------------------
REM Actualizar pip dentro del venv
REM --------------------------------------------------
echo Actualizando pip en el entorno virtual...
env_Py3.10\Scripts\python.exe -m pip install --upgrade pip

echo.

REM --------------------------------------------------
REM Instalar dependencias en el venv
REM --------------------------------------------------
echo Instalando dependencias...
env_Py3.10\Scripts\python.exe -m pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo [ERROR] Fallo instalando dependencias
    pause
    exit /b 1
)

echo.
echo [OK] Dependencias instaladas correctamente

echo.

REM --------------------------------------------------
REM Comprobacion FFmpeg (opcional)
REM --------------------------------------------------
echo Comprobando FFmpeg...

ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo [AVISO] FFmpeg no esta en PATH
    echo El programa usara ffmpeg\ffmpeg.exe si esta incluido
) else (
    echo [OK] FFmpeg detectado en sistema
)

echo.

echo ==========================================
echo   Instalacion completada correctamente
echo ==========================================
pause