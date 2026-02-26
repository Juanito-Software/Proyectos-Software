@echo off
title AstroSim — Órbita simple
cd /d "%~dp0"

pip install -r requirements.txt -q
python main.py --scenario orbit

pause
