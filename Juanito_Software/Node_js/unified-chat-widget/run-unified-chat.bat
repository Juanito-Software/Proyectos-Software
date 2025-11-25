@echo off
setlocal

:: Ruta del proyecto (usando la ruta actual del script)
set "projectPath=%~dp0"

:: Cambiar al directorio del proyecto
cd /d "%projectPath%" || (
    echo [ERROR] No se pudo acceder al directorio: %projectPath%
    pause
    exit /b
)

:: Iniciar servidor de Rumble en segundo plano (si está configurado)
echo [INFO] Iniciando servidor de Rumble en segundo plano...
start "Servidor Rumble" /B coqui_env\Scripts\python.exe rumble_server.py
timeout /t 2 /nobreak >nul

:: Arrancar servidor principal
echo [INFO] Ejecutando servidor de chat unificado...
node index.js

pause
endlocal
