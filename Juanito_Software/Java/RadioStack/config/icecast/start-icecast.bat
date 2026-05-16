@echo off
REM Coloca este .bat en la raiz de Icecast (junto a icecast.xml, web\, admin\, log\)
REM Clic derecho -> Ejecutar como administrador

cd /d "%~dp0"

REM Cierra instancias previas (evita dos Icecast en el mismo puerto)
taskkill /F /IM icecast.exe >nul 2>&1
timeout /t 2 /nobreak >nul

if not exist "log" mkdir "log"

set ICECAST_EXE=
if exist "bin\icecast.exe" set ICECAST_EXE=bin\icecast.exe
if exist "icecast.exe" set ICECAST_EXE=icecast.exe

if "%ICECAST_EXE%"=="" (
    echo No se encuentra icecast.exe
    echo Buscado en: %CD%\bin\icecast.exe y %CD%\icecast.exe
    pause
    exit /b 1
)

echo Iniciando Icecast desde: %CD%
echo Ejecutable: %ICECAST_EXE%
echo Logs en: %CD%\log\
echo Config: %CD%\icecast.xml
echo.

"%ICECAST_EXE%" -c "%CD%\icecast.xml"

if errorlevel 1 (
    echo.
    echo Error al arrancar. Comprueba icecast.xml y permisos en log\
    pause
)
