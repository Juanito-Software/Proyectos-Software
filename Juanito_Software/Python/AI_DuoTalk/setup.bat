@echo off
setlocal

echo Creando entorno virtual...
python -m venv iaenv

echo Actualizando pip...
iaenv\Scripts\python -m pip install --upgrade pip

echo Instalando dependencias...
iaenv\Scripts\python -m pip install -r requirements.txt

echo Listo.
pause