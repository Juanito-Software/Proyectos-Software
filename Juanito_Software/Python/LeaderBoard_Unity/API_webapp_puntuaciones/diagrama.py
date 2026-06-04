# Reimport necessary libraries after reset
from matplotlib import pyplot as plt
import matplotlib.patches as mpatches

# Crear la figura y el eje
fig, ax = plt.subplots(figsize=(12, 8))

# Cliente Unity (Frontend)
ax.text(0.1, 0.9, 'Cliente Unity (Frontend)', fontsize=12, fontweight='bold')
ax.text(0.1, 0.85, 'Motor de juego: Unity', fontsize=10)
ax.text(0.1, 0.82, 'Lenguaje: C#', fontsize=10)
ax.text(0.1, 0.79, 'Manejo de JSON: SimpleJSON', fontsize=10)
ax.text(0.1, 0.76, 'Interfaz gráfica:', fontsize=10)
ax.text(0.1, 0.73, '- Pantalla de Leaderboard con opciones de filtrado', fontsize=10)
ax.text(0.1, 0.7, '- Perfil del Jugador mostrando estadísticas y logros', fontsize=10)


# Backend API (Flask)
ax.text(0.1, 0.6, 'Backend API (Flask)', fontsize=12, fontweight='bold')
ax.text(0.1, 0.55, 'Framework: Flask', fontsize=10)
ax.text(0.1, 0.52, 'Base de datos: PostgreSQL', fontsize=10)
ax.text(0.1, 0.49, 'Autenticación: JWT (JSON Web Tokens)', fontsize=10)
ax.text(0.1, 0.46, 'Seguridad: CORS', fontsize=10)

# API RESTful
ax.text(0.1, 0.41, 'API RESTful:', fontsize=10, fontweight='bold')
ax.text(0.1, 0.38, '- CRUD para puntuaciones: Crear, Leer, Actualizar, Eliminar', fontsize=10)
ax.text(0.1, 0.35, '- Endpoints principales:', fontsize=10)
ax.text(0.1, 0.32, '/puntuaciones POST para agregar puntuaciones en la base de datos', fontsize=10)
ax.text(0.1, 0.29, '/puntuaciones GET para obtener puntuaciones con paginación y filtros', fontsize=10)
ax.text(0.1, 0.26, '/puntuaciones/{nombre} GET para buscar por nombre de jugador', fontsize=10)
ax.text(0.1, 0.23, '/puntuaciones/{nombre} PUT para actualizar por nombre de jugador', fontsize=10)
ax.text(0.1, 0.20, '- Endpoints que no se usan desde la interfaz de unity, solo Admin:', fontsize=10)
ax.text(0.1, 0.17, '/puntuaciones/{nombre} DELETE para eliminar puntuaciones de la base de datos', fontsize=10)
ax.text(0.1, 0.14, '/puntuaciones DELETE para eliminar todas las puntuaciones de la base de datos', fontsize=10)


# Base de Datos (PostgreSQL)
ax.text(0.1, 0.04, 'Base de Datos (PostgreSQL)', fontsize=12, fontweight='bold')
ax.text(0.1, 0.01, 'Almacena los datos de las puntuaciones de los jugadores', fontsize=10)
ax.text(0.1, -0.02, 'Esquema de puntuaciones:', fontsize=10)
ax.text(0.1, -0.05, 'nombre: string', fontsize=10)
ax.text(0.1, -0.08, 'valor: int', fontsize=10)

# Seguridad
ax.text(0.7, 0.41, 'Seguridad', fontsize=12, fontweight='bold')
ax.text(0.7, 0.38, 'Autenticación: JWT', fontsize=10)
ax.text(0.7, 0.35, 'CORS configurado para orígenes autorizados', fontsize=10)

# Líneas que representan conexiones
ax.annotate('', xy=(0.0, 0.65), xytext=(0.0, 0.75),
            arrowprops=dict(facecolor='black', shrink=0.05))

ax.annotate('', xy=(0.0, 0.11), xytext=(0.0, 0.22),
            arrowprops=dict(facecolor='black', shrink=0.05))



# Limpiar ejes
ax.set_axis_off()

# Mostrar el diagrama
plt.show()
