@echo off
setlocal

if not exist ClipsAI_env (
    echo Creando entorno virtual...
    python -m venv ClipsAI_env
)

if errorlevel 1 (
    echo Error al crear el entorno virtual.
    pause
    exit /b 1
)

echo Actualizando pip...
ClipsAI_env\Scripts\python -m pip install --upgrade pip

echo Instalando dependencias...
ClipsAI_env\Scripts\python -m pip install -r requirements.txt

echo Listo.
pause