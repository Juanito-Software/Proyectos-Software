# Copyright (C) 2025 JuanitoSoftware
#
# Este programa es software libre: puedes redistribuirlo y/o modificarlo bajo
# los términos de la Licencia Pública General de GNU publicada por la Free
# Software Foundation, ya sea la versión 3 de la Licencia o (según tu elección)
# cualquier versión posterior.
#
# Este programa se distribuye con la esperanza de que sea útil, pero SIN
# NINGUNA GARANTÍA; incluso sin la garantía implícita de COMERCIALIZACIÓN o
# IDONEIDAD PARA UN PROPÓSITO PARTICULAR. Consulta la Licencia Pública General
# de GNU para más detalles.
#
# Deberías haber recibido una copia de la Licencia Pública General de GNU junto
# con este programa. Si no es así, visita <https://www.gnu.org/licenses/>.


# progress_bar_utils.py

import sys

def show_basic_progress_bar(progress, total):
    bar_length = 50
    filled_length = int(progress / total * bar_length)
    bar = "[" + "=" * filled_length + " " * (bar_length - filled_length) + "]"
    sys.stdout.write(f"\r{bar} {progress}/{total}")
    sys.stdout.flush()

def show_fancy_progress_bar(progress, total):
    bar_length = 50
    filled_length = int(progress / total * bar_length)
    percent = int(progress / total * 100)
    spinner = ['|', '/', '-', '\\']
    bar = "[" + "=" * filled_length + " " * (bar_length - filled_length) + "]"
    sys.stdout.write(f"\r{bar} {percent}% {spinner[progress % len(spinner)]}")
    sys.stdout.flush()
