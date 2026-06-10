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

# Función para generar n números de Fibonacci
def fibonacci(n):
    if n <= 0:
        return np.array([])

    result = np.empty(n, dtype=int)
    result[0] = 0
    if n > 1:
        result[1] = 1

    for i in range(2, n):
        result[i] = result[i - 1] + result[i - 2]

    return result

n = 20
angle = np.radians(137.5)
r_values = fibonacci(n)
theta_values = np.arange(n) * angle

x = r_values * np.cos(theta_values)
y = r_values * np.sin(theta_values)

fig, ax = plt.subplots()
line, = ax.plot(x, y, color='green', linewidth=2)  # <- línea conectando puntos
ax.axis('equal')

# Animación: rotación
for t in range(100):
    theta_values += 0.1
    x = r_values * np.cos(theta_values)
    y = r_values * np.sin(theta_values)
    line.set_data(x, y)  # actualizar la línea
    plt.pause(0.05)
