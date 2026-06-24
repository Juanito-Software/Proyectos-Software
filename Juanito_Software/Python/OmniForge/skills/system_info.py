"""
Skill: información del sistema y procesos — patrón de Hermes (system awareness).
Permite al agente conocer el estado del PC antes de tomar decisiones.
Usa psutil si está disponible; fallback a wmic/tasklist para evitar dependencias duras.
"""
from langchain_core.tools import tool

SKILL_METADATA = {
    "agents": ["coder", "pc_controller"],
    "description": "Consulta CPU, RAM, disco y procesos del sistema",
}


@tool
def get_system_info() -> str:
    """
    Devuelve uso actual de CPU, RAM y disco.
    No requiere argumentos.
    """
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=0.5)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        return (
            f"CPU: {cpu}%\n"
            f"RAM: {mem.percent}% usado ({mem.used // 1024**2} MB / {mem.total // 1024**2} MB)\n"
            f"Disco C: {disk.percent}% usado ({disk.used // 1024**3} GB / {disk.total // 1024**3} GB)"
        )
    except ImportError:
        pass

    # Fallback sin psutil
    import subprocess
    try:
        out = subprocess.check_output(
            ["wmic", "cpu", "get", "LoadPercentage", "/value"],
            text=True, timeout=5
        )
        cpu_line = next((l for l in out.splitlines() if "LoadPercentage" in l), "")
        cpu_val = cpu_line.split("=")[-1].strip() if "=" in cpu_line else "?"

        mem_out = subprocess.check_output(
            ["wmic", "OS", "get", "FreePhysicalMemory,TotalVisibleMemorySize", "/value"],
            text=True, timeout=5
        )
        vals = {l.split("=")[0]: l.split("=")[1] for l in mem_out.splitlines() if "=" in l}
        total_kb = int(vals.get("TotalVisibleMemorySize", 0))
        free_kb = int(vals.get("FreePhysicalMemory", 0))
        used_pct = round((total_kb - free_kb) / total_kb * 100, 1) if total_kb else "?"
        return f"CPU: {cpu_val}%\nRAM: {used_pct}% usado"
    except Exception as e:
        return f"ERROR get_system_info: {e}"


@tool
def get_running_processes(filter_name: str = "") -> str:
    """
    Lista los procesos en ejecución.
    filter_name: filtrar por nombre de proceso (opcional, case-insensitive).
    """
    try:
        import psutil
        procs = []
        for p in psutil.process_iter(["pid", "name", "memory_percent"]):
            try:
                info = p.info
                if filter_name and filter_name.lower() not in info["name"].lower():
                    continue
                procs.append(f"  {info['pid']:6d}  {info['name']:<30}  {info['memory_percent']:.1f}%")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        if not procs:
            return f"No se encontraron procesos{' con nombre ' + filter_name if filter_name else ''}."
        header = f"{'PID':>6}  {'Nombre':<30}  {'RAM%'}"
        return header + "\n" + "\n".join(procs[:40])
    except ImportError:
        pass

    import subprocess
    try:
        cmd = ["tasklist", "/FO", "CSV", "/NH"]
        out = subprocess.check_output(cmd, text=True, timeout=10)
        lines = []
        for line in out.splitlines():
            parts = line.strip('"').split('","')
            if len(parts) >= 2 and (not filter_name or filter_name.lower() in parts[0].lower()):
                lines.append(f"  {parts[1]:>6}  {parts[0]}")
        return "\n".join(lines[:40]) if lines else "No se encontraron procesos."
    except Exception as e:
        return f"ERROR get_running_processes: {e}"