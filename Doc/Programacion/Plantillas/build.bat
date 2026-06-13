##Paso 1

@echo off
setlocal

set /p APP_NAME=Nombre del ejecutable:

echo === Limpiando builds ===
rmdir /s /q dist 2>nul
rmdir /s /q build 2>nul

echo === Construyendo ===
venv\Scripts\pyinstaller --onefile --name "%APP_NAME%" src\main.py

echo === Build terminado ===
pause

---

##Paso 2

@echo off
setlocal

echo === Limpiando builds ===
rmdir /s /q dist 2>nul
rmdir /s /q build 2>nul

echo === Construyendo desde spec ===
venv\Scripts\pyinstaller MiProyecto.spec

echo === Build terminado ===
pause