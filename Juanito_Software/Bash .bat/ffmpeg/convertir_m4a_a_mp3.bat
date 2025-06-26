@echo off
set ffmpeg_path="C:\Users\User\Downloads\ffmpeg\ffmpeg-2025-05-29-git-75960ac270-full_build\ffmpeg-2025-05-29-git-75960ac270-full_build\bin\ffmpeg.exe"

for %%a in (*.m4a) do (
    echo Procesando %%a...
    %ffmpeg_path% -i "%%a" "%%~na.mp3"
)
pause
