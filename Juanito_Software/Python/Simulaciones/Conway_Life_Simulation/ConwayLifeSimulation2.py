import numpy as np
import matplotlib.pyplot as plt
import time

# Tamaño del tablero
N = 120
grid = np.random.choice([0, 1], N*N, p=[0.8, 0.2]).reshape(N, N)

def update(grid):
    new_grid = grid.copy()
    for i in range(1, N-1):
        for j in range(1, N-1):
            total = np.sum(grid[i-1:i+2, j-1:j+2]) - grid[i, j]
            if grid[i, j] == 1 and (total < 2 or total > 3):
                new_grid[i, j] = 0
            elif grid[i, j] == 0 and total == 3:
                new_grid[i, j] = 1
    return new_grid

plt.ion()
for _ in range(100):
    plt.imshow(grid, cmap='binary')
    plt.draw()
    plt.pause(0.1)
    plt.clf()
    grid = update(grid)
