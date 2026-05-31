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

import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import make_interp_spline

# Función para generar n números de Fibonacci
def fibonacci(n):
    fib = [0, 1]
    for i in range(2, n+1):
        fib.append(fib[-1] + fib[-2])
    return np.array(fib[1:])

n = 20
angle = np.radians(137.5)
r_values = fibonacci(n)
theta_values = np.arange(n) * angle

x = r_values * np.cos(theta_values)
y = r_values * np.sin(theta_values)

# Interpolación para suavizar la espiral
t = np.linspace(0, n-1, n)
t_new = np.linspace(0, n-1, 500)  # más puntos para suavizar
spl_x = make_interp_spline(t, x)(t_new)
spl_y = make_interp_spline(t, y)(t_new)

fig, ax = plt.subplots()
line, = ax.plot(spl_x, spl_y, color='green', linewidth=2)
ax.axis('equal')

# Animación: rotación
for _ in range(200):
    theta_values += 0.02  # rotación suave
    x = r_values * np.cos(theta_values)
    y = r_values * np.sin(theta_values)
    spl_x = make_interp_spline(t, x)(t_new)
    spl_y = make_interp_spline(t, y)(t_new)
    line.set_data(spl_x, spl_y)
    plt.pause(0.05)
