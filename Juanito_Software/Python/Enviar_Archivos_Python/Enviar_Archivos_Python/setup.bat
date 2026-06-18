@echo off
setlocal

echo ==========================================
echo   File Transfer App - Instalacion
echo ==========================================
echo.

REM --------------------------------------------------
REM Comprobar Python
REM --------------------------------------------------
echo Comprobando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado o no esta en PATH
    pause
    exit /b 1
)

echo [OK] Python detectado
echo.

REM --------------------------------------------------
REM Actualizar pip (silencioso)
REM --------------------------------------------------
echo Actualizando pip...
python -m pip install --upgrade pip >nul

echo.

REM --------------------------------------------------
REM Instalar dependencias del proyecto
REM --------------------------------------------------
echo Instalando dependencias...
python -m pip install -r requirements.txt

if exist requirements.txt (
    echo Instalando dependencias...
    python -m pip install -r requirements.txt

    if %errorlevel% neq 0 (
        echo [ERROR] Fallo instalando dependencias
        pause
        exit /b 1
    )
) else (
    echo [INFO] No hay requirements.txt (solo stdlib)
)

echo.
echo [OK] Dependencias instaladas
echo.

REM --------------------------------------------------
REM Verificacion de Python GUI base (Tkinter)
REM --------------------------------------------------
echo Verificando Tkinter...
python -c "import tkinter" >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Tkinter no disponible en este Python
    echo Instala Python con soporte Tcl/Tk
    pause
    exit /b 1
)

echo [OK] Tkinter disponible
echo.

REM --------------------------------------------------
REM Check opcional de sockets (solo informativo)
REM --------------------------------------------------
echo Verificando soporte de red...
python -c "import socket" >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Modulo socket no disponible (muy raro)
    pause
    exit /b 1
)

echo [OK] Red disponible
echo.

echo ==========================================
echo   Instalacion completada correctamente
echo ==========================================
echo.
pause