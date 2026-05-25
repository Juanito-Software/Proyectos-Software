@echo off
title AstroSim — 3 cuerpos
cd /d "%~dp0"

pip install -r requirements.txt -q
python main.py --scenario three_body

pause
