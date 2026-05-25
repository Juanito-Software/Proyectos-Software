@echo off
title AstroSim
cd /d "%~dp0"

pip install -r requirements.txt -q
python main.py

pause
