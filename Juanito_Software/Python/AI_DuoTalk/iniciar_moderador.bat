@echo off
REM Script para iniciar AI_DuoTalk - Modo Moderador
REM Ejecuta el sistema con doble clic

echo ============================================================
echo   AI_DuoTalk - Modo Moderador Absoluto
echo ============================================================
echo.

REM Cambiar al directorio del script
cd /d "%~dp0"

REM Verificar que existe el entorno virtual
if not exist "iaenv\Scripts\activate.bat" (
    echo [ERROR] No se encuentra el entorno virtual 'iaenv'
    echo [AVISO] Por favor, crea el entorno virtual primero:
    echo         python -m venv iaenv
    echo.
    pause
    exit /b 1
)

REM Activar entorno virtual y ejecutar el programa
echo [INICIO] Activando entorno virtual...
call iaenv\Scripts\activate.bat

if errorlevel 1 (
    echo [ERROR] No se pudo activar el entorno virtual
    pause
    exit /b 1
)

echo [OK] Entorno virtual activado
echo.

REM Verificar que existe el archivo principal
if not exist "main_moderador.py" (
    echo [ERROR] No se encuentra el archivo 'main_moderador.py'
    echo [AVISO] Asegurate de estar en el directorio correcto
    echo.
    pause
    exit /b 1
)

echo [INICIO] Ejecutando Modo Moderador...
echo.

REM Ejecutar el programa
python main_moderador.py

REM Si hay un error, mostrar mensaje
if errorlevel 1 (
    echo.
    echo [ERROR] El programa terminó con un error
    echo.
)

REM Mantener la ventana abierta para ver mensajes
echo.
echo ============================================================
echo   Programa finalizado
echo ============================================================
pause

