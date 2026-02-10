@echo off
setlocal

:: Script para iniciar todos los servicios del chat unificado
:: Inicia: TTS + Chat Unificado (que incluye Rumble automáticamente)
:: Este script llama a los otros .bat existentes para reutilizar su lógica

:: Ruta del proyecto (usando la ruta actual del script)
set "projectPath=%~dp0"

:: Cambiar al directorio del proyecto
cd /d "%projectPath%" || (
    echo [ERROR] No se pudo acceder al directorio: %projectPath%
    pause
    exit /b
)

echo ========================================
echo   INICIANDO TODOS LOS SERVICIOS
echo ========================================
echo.

:: Paso 1: Iniciar servidor TTS en segundo plano
echo [1/2] Iniciando servidor TTS...
start "Servidor TTS" cmd /c "%~dp0run-TTS.bat"
timeout /t 3 /nobreak >nul

:: Paso 2: Iniciar chat unificado (esto también inicia Rumble automáticamente)
echo [2/2] Iniciando servidor de chat unificado...
echo.
echo ========================================
echo   SERVICIOS INICIADOS
echo ========================================
echo   - Servidor TTS: Corriendo en segundo plano
echo   - Servidor Rumble: Se iniciará automáticamente
echo   - Servidor BitChute: Se iniciará automáticamente
echo   - Chat Unificado: Iniciando...
echo ========================================
echo.

:: Ejecutar chat unificado usando su .bat (esto bloquea hasta que se cierre)
call "%~dp0run-unified-chat.bat"

pause
endlocal

