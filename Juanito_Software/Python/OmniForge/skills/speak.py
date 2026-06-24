"""
Skill: texto a voz — Windows SAPI vía PowerShell (sin dependencias externas).
Útil para feedback de audio al usuario, accesibilidad, o confirmar acciones.
Basado en el patrón de output multimodal de Hermes.
"""
from langchain_core.tools import tool
import subprocess

SKILL_METADATA = {
    "agents": ["*"],
    "description": "Convierte texto a voz usando Windows SAPI",
}


@tool
def speak_text(text: str, rate: int = 0) -> str:
    """
    Lee en voz alta el texto dado usando el sintetizador de voz de Windows.
    text: texto a leer (máx 500 caracteres).
    rate: velocidad de habla (-10 lento … 0 normal … 10 rápido).
    """
    text = text[:500].replace("'", " ").replace('"', " ")
    rate = max(-10, min(10, rate))
    ps_cmd = (
        "Add-Type -AssemblyName System.Speech; "
        "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        f"$s.Rate = {rate}; "
        f"$s.Speak('{text}');"
    )
    try:
        subprocess.Popen(
            ["powershell", "-NoProfile", "-Command", ps_cmd],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return f"OK: reproduciendo '{text[:60]}{'...' if len(text) > 60 else ''}'"
    except Exception as e:
        return f"ERROR speak_text: {e}"