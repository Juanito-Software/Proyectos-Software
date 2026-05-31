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

import random
import time
import os
import time
import subprocess
import sys

def run_matrix_effect():
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    exe_path = os.path.join(base_path, "matrix_effect.exe")

    # Ejecutamos el .exe y esperamos a que termine (sin ventana de consola si usas noconsole)
    # creationflags para abrir sin ventana, opcional si usas --noconsole en PyInstaller
    # Aquí dejamos que se abra la consola porque es el efecto matrix
    subprocess.run([exe_path], check=True)

# Tamaño de la cuadrícula
FILAS = 88
COLUMNAS = 188
TURNOS = 1000
DELAY = 0.2  # segundos entre turnos

# Inicializar cuadrícula con un patrón conocido pero de forma aleatoria
def inicializar_cuadricula(filas, columnas):
    cuadricula = [[0]*COLUMNAS for _ in range(FILAS)]

    # Definir patrones como listas de coordenadas relativas
    block = [(0,0),(0,1),(1,0),(1,1)]
    beehive = [(0,1),(0,2),(1,0),(1,3),(2,1),(2,2)]
    blinker = [(0,0),(0,1),(0,2)]
    toad = [(0,1),(0,2),(0,3),(1,0),(1,1),(1,2)]
    glider = [(0,1),(1,2),(2,0),(2,1),(2,2)]

    patrones = [block, beehive, blinker, toad, glider]

    for patron in patrones:
        # generar entre 48 y 192 repeticiones de cada patrón
        repeticiones = random.randint(48,192)
        for _ in range(repeticiones):
            # elegir posición aleatoria dentro de los bordes
            x_offset = random.randint(0, FILAS - max([c[0] for c in patron]) - 1)
            y_offset = random.randint(0, COLUMNAS - max([c[1] for c in patron]) - 1)
            # colocar patrón
            for dx, dy in patron:
                cuadricula[x_offset + dx][y_offset + dy] = 1

    return cuadricula




# Contar vecinos vivos
def contar_vecinos(cuadricula, x, y):
    vecinos = 0
    for i in range(x-1, x+2):
        for j in range(y-1, y+2):
            if (i == x and j == y):
                continue
            if 0 <= i < FILAS and 0 <= j < COLUMNAS:
                vecinos += cuadricula[i][j]
    return vecinos

# Generar siguiente turno aplicando las 4 reglas clásicas
def siguiente_turno(cuadricula):
    nueva = [[0 for _ in range(COLUMNAS)] for _ in range(FILAS)]
    for i in range(FILAS):
        for j in range(COLUMNAS):
            vecinos = contar_vecinos(cuadricula, i, j)
            if cuadricula[i][j] == 1:
                # Supervivencia
                if vecinos == 2 or vecinos == 3:
                    nueva[i][j] = 1
                # Muerte por soledad o sobrepoblación implícita
                # else: queda muerta (0)
                # Explicación: si tiene menos de 2 vecinos vivos → muere de soledad
                # si tiene más de 3 vecinos vivos → muere por sobrepoblación
            else:
                # Nacimiento
                if vecinos == 3:
                    nueva[i][j] = 1
    return nueva

# Mostrar la cuadrícula
def mostrar_cuadricula(cuadricula):
    os.system('cls' if os.name == 'nt' else 'clear')
    for fila in cuadricula:
        print("".join(['O' if celda else '.' for celda in fila]))



try:
    run_matrix_effect() 
except subprocess.CalledProcessError as e:
        print(f"matrix_effect.exe terminó con error (probablemente cerrado con la X): {e}")
except Exception as e:
        print(f"Error inesperado ejecutando matrix_effect.exe: {e}")

# Ejecutar simulación
cuadricula = inicializar_cuadricula(FILAS, COLUMNAS)
for _ in range(TURNOS):
    mostrar_cuadricula(cuadricula)
    cuadricula = siguiente_turno(cuadricula)
    time.sleep(DELAY)
