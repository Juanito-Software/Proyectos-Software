import matplotlib.pyplot as plt
import numpy as np

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
