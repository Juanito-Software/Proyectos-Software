@echo off
setlocal

if not exist AIClipCreator_env (
    echo Creando entorno virtual...
    python -m venv AIClipCreator_env
)

if errorlevel 1 (
    echo Error al crear el entorno virtual.
    pause
    exit /b 1
)

echo Actualizando pip...
AIClipCreator_env\Scripts\python -m pip install --upgrade pip

echo Instalando dependencias...
AIClipCreator_env\Scripts\python -m pip install -r requirements.txt

echo Listo.
pause