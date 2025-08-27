@echo off
REM === Cambia esta ruta a la carpeta de tu proyecto ===
cd /d "C:\Users\User\Desktop\Proyectos\Juanito_Software\Python\ClipsGeneration\AIClipCreator_EpicHL\AI-clip-creator"

echo ================================
echo  Activando entorno virtual...
echo ================================

REM Activar el entorno virtual
call ..\AIClipCreator_env\Scripts\activate

echo ================================
echo  Iniciando AI Clip Creator...
echo ================================

REM Ejecutar con Python del PATH
python main.py

echo.
echo Programa finalizado.
pause