@echo off
setlocal

:: Ruta del proyecto
set "projectPath=C:\Users\User\Desktop\Proyectos\Juanito_Software\Paginas\unified-chat-widget"

:: Ruta absoluta al ejecutable node (cambia esto si tu node está en otro sitio)
set "nodeExe=C:\Program Files\nodejs\node.exe"

:: Cambiar al directorio del proyecto
cd /d "%projectPath%" || (
    echo [ERROR] No se pudo acceder al directorio: %projectPath%
    pause
    exit /b
)

:: Arrancar servidor principal
echo [INFO] Ejecutando: "%nodeExe%" index.js
"%nodeExe%" index.js

pause
endlocal
