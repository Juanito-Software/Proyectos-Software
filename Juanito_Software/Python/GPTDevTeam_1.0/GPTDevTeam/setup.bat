@echo off
setlocal

echo Creando entorno virtual...
python -m venv venv

echo Actualizando pip...
venv\Scripts\python -m pip install --upgrade pip

echo Instalando dependencias...
venv\Scripts\python -m pip install -r requirements.txt

echo Listo.
pause