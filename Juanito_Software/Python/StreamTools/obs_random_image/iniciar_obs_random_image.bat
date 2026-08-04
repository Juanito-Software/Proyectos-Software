@echo off
REM =========================================================================
REM iniciar_obs_random_image.bat
REM
REM Activa el entorno virtual (venv) y lanza obs_random_image.py con los
REM parametros configurados para rotar la fuente "Shitpost" en OBS cada 30s.
REM
REM Ajusta las rutas de abajo si tu proyecto no esta en la misma carpeta
REM que este .bat, o si el venv se llama distinto.
REM =========================================================================

REM Cambia al directorio donde esta este .bat (para que las rutas relativas funcionen
REM sin importar desde donde lo ejecutes, p.ej. doble clic desde el Explorador)
cd /d "%~dp0"

REM Activar el entorno virtual
call venv\Scripts\activate.bat

REM Comprobar que la activacion funciono (si falla, avisar y detenerse)
if errorlevel 1 (
    echo ERROR: no se pudo activar el entorno virtual "venv".
    echo Verifica que existe la carpeta venv junto a este .bat.
    pause
    exit /b 1
)

REM Lanzar el script con los parametros solicitados
python obs_random_image.py ^
    --folder "C:\Users\User\Pictures\Fondo" ^
    --source "Shitpost" ^
    --interval 30 ^
    --host localhost ^
    --port 4455 ^
    --password "123456" ^
    --no-repeat

REM Si el script termina o falla, mantener la ventana abierta para ver el mensaje
echo.
echo El script ha finalizado o se ha detenido.
pause
