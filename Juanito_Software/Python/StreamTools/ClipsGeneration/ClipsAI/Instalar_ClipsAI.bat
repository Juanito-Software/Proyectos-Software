@echo off
setlocal

:: ===========================
:: Crear y activar entorno virtual
:: ===========================
py -3.11 -m venv ClipsAI_env
call ClipsAI_env\Scripts\activate

:: ===========================
:: Actualizar pip
:: ===========================
pip install --upgrade pip

:: ===========================
:: Instalar dependencias base
:: ===========================
pip install "numpy>=2.0.2"
pip install "torch>=2.5.1" torchvision torchaudio

:: ===========================
:: Instalar WhisperX
:: ===========================
pip install git+https://github.com/m-bain/whisperx.git

:: ===========================
:: Instalar ClipsAI sin dependencias
:: ===========================
pip install --no-deps clipsai

:: ===========================
:: Instalar libmagic para Windows
:: ===========================
pip install python-magic-bin

:: ===========================
:: Instalar FFmpeg automáticamente y añadir al PATH del entorno
:: ===========================
set FFMPEG_URL=https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip
set TEMP_DIR=%TEMP%\ffmpeg_tmp

mkdir "%TEMP_DIR%"
powershell -Command "Invoke-WebRequest -Uri '%FFMPEG_URL%' -OutFile '%TEMP_DIR%\ffmpeg.zip'"
powershell -Command "Add-Type -AssemblyName System.IO.Compression.FileSystem; [System.IO.Compression.ZipFile]::ExtractToDirectory('%TEMP_DIR%\ffmpeg.zip', '%TEMP_DIR%')"

:: Copiar binarios de FFmpeg al entorno
for /d %%D in ("%TEMP_DIR%\ffmpeg-*\bin") do (
    xcopy "%%D\ffmpeg.exe" "ClipsAI_env\Scripts\" /y /i
    xcopy "%%D\ffprobe.exe" "ClipsAI_env\Scripts\" /y /i
)

:: Limpiar
rmdir /s /q "%TEMP_DIR%"

:: ===========================
:: Clonar repositorio ClipsAI dentro del entorno
:: ===========================
git clone https://github.com/tu_usuario/clipsai.git

endlocal
