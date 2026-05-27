@echo off
cd /d "%~dp0"

echo Iniciando Matrix... (pulsa ESPACIO o ENTER para saltar)

REM Lanzamos matrix_effect.exe en una ventana separada
start "" matrix_effect.exe

REM Detectar tecla (ENTER o ESPACIO) para cerrar Matrix
powershell -NoProfile -Command ^
  "Add-Type -AssemblyName System.Windows.Forms; ^
   while ($true) { ^
     if ([System.Windows.Forms.Control]::ModifierKeys) {} ^
     if ($Host.UI.RawUI.KeyAvailable) { ^
        $k = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown'); ^
        if ($k.VirtualKeyCode -eq 13 -or $k.VirtualKeyCode -eq 32) { exit } ^
     } ^
     Start-Sleep -Milliseconds 50 ^
   }"

REM Cerramos Matrix si sigue abierto
taskkill /IM matrix.exe /F >nul 2>&1

echo Lanzando MP3Player...
start "" /min pythonw.exe MP3Player.py

exit

