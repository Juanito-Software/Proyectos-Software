## VocoderSynth - Vocoder-like en tiempo real (Python)

Pequeño proyecto en Python que aplica un efecto de **voz robotizada /
vocoder-like en tiempo real** usando tu **micrófono** como entrada y un
oscilador como portador, basado en `sounddevice` + `numpy`.

### Requisitos

- Python 3.9+ (recomendado).
- Tarjeta de sonido funcional con un micrófono configurado como entrada por defecto.
- Windows 10 o superior.

### Instalación

1. Crear entorno virtual (opcional pero recomendado):

   ```powershell
   cd D:\Proyectos\VocoderSynth
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Instalar dependencias:

   ```powershell
   pip install -r requirements.txt
   ```

   Esto instalará `sounddevice` (E/S de audio en tiempo real) y `numpy`
   (procesamiento numérico).

### Uso

Con el entorno virtual activado, ejecuta:

```powershell
python .\vocoder_realtime.py
```

Habla por el micrófono: deberías escuchar tu voz procesada con un efecto
de ring modulation tipo voz robótica/vocoder. Usa `Ctrl+C` en la consola
para salir.



