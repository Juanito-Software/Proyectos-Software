@echo off
setlocal

:: Script para actualizar automáticamente las variables de Rumble en .env
:: Uso: update-rumble-env.bat [--api-url URL] [--channel CANAL] [--auto-detect]

:: Ruta del proyecto
set "projectPath=%~dp0"
cd /d "%projectPath%" || (
    echo [ERROR] No se pudo acceder al directorio: %projectPath%
    pause
    exit /b
)

:: Ejecutar script de Python
echo [INFO] Actualizando configuración de Rumble en .env...
coqui_env\Scripts\python.exe utils\update_rumble_env.py %*

pause
endlocal

