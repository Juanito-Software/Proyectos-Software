@echo off
setlocal

if not exist venv (
    echo Creando entorno virtual...
    python -m venv venv
)

if errorlevel 1 (
    echo Error al crear el entorno virtual.
    pause
    exit /b 1
)

echo Actualizando pip...
venv\Scripts\python -m pip install --upgrade pip

echo Instalando dependencias...
venv\Scripts\python -m pip install -r requirements.txt

echo Listo.
pause