@echo off

set /p PROJECT_NAME=Nombre del proyecto: 

echo Creando estructura...

mkdir %PROJECT_NAME%
cd %PROJECT_NAME%

mkdir src
mkdir scripts

echo print("Hello World") > src\main.py

echo # Proyecto %PROJECT_NAME% > README.md

echo venv/ > .gitignore
echo __pycache__/ >> .gitignore
echo dist/ >> .gitignore
echo build/ >> .gitignore

echo requirements.txt creado
type nul > requirements.txt

echo scripts creados...

copy setup.bat scripts\
copy run.bat scripts
copy build.bat scripts

echo Proyecto creado correctamente
pause