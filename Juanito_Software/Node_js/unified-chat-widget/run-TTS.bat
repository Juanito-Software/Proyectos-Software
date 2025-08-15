@echo off
setlocal

:: Ruta del proyecto
set "projectPath=C:\Users\User\Desktop\Proyectos\Juanito_Software\Paginas\unified-chat-widget"

:: Cambiar al directorio del proyecto
cd /d "%projectPath%" || (
    echo [ERROR] No se pudo acceder al directorio: %projectPath%
    pause
    exit /b
)

:: Ejecutar python del entorno virtual directamente
echo [INFO] Ejecutando servidor TTS usando python del entorno virtual...
coqui_env\Scripts\python.exe tts_server.py

pause
endlocal
