import subprocess
import sys
import os

def run(cmd):
    subprocess.check_call(cmd, shell=True)

print("Creando venv...")
run("python -m venv venv")

if os.name == "nt":
    pip = r"venv\Scripts\pip"
else:
    pip = "venv/bin/pip"

print("Actualizando pip...")
run(f"{pip} install --upgrade pip")

print("Instalando dependencias...")
run(f"{pip} install -r requirements.txt")

print("OK listo")