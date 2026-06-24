"""
Skill de ejemplo — notificación de escritorio (Windows).
Para añadir tus propias skills: copia este archivo, define funciones @tool,
ajusta SKILL_METADATA y reinicia OmniForge.
"""
from langchain_core.tools import tool

SKILL_METADATA = {
    "agents": ["coder", "pc_controller"],
    "description": "Envía notificaciones de escritorio en Windows",
}


@tool
def notify(title: str, message: str) -> str:
    """
    Muestra una notificación de escritorio en Windows.
    title: título de la notificación.
    message: texto del cuerpo.
    """
    try:
        import subprocess
        ps_cmd = (
            f"Add-Type -AssemblyName System.Windows.Forms; "
            f"$n = New-Object System.Windows.Forms.NotifyIcon; "
            f"$n.Icon = [System.Drawing.SystemIcons]::Information; "
            f"$n.Visible = $true; "
            f"$n.ShowBalloonTip(3000, '{title}', '{message}', "
            f"[System.Windows.Forms.ToolTipIcon]::Info); "
            f"Start-Sleep 4; $n.Dispose()"
        )
        subprocess.Popen(
            ["powershell", "-NoProfile", "-Command", ps_cmd],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return f"OK: notificación enviada — '{title}'"
    except Exception as e:
        return f"ERROR notificación: {e}"