"""
Configuración de GameChat - Fase 1
"""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Rutas
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "world_state.db"

# Twitch (obtener desde variables de entorno o .env)
TWITCH_CHANNEL = os.getenv("TWITCH_CHANNEL", "JuanitoCanuto")
TWITCH_OAUTH = os.getenv("TWITCH_OAUTH", "oauth:iu5d0jro8ut145ky8s0h7g17fioyxo")  # oauth:xxxx para bot
TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID", "li5vvfhvt969ox2r5dtqpbsmc1yzu2")
TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET", "y26w934qr3an0p6x4o7t6jr1knp6si")

# Modo simulación (sin Twitch real, para pruebas)
# Forzado a False para que nada ocurra “solo” si no hay chat real.
SIMULATION_MODE = False

# --- Mapa (1920x1080) ---
MAP_WIDTH = 32   # tiles
MAP_HEIGHT = 18
TILE_SIZE = 60   # 32*60=1920, 18*60=1080

# --- Render interno (fijo) ---
MAP_PIXEL_WIDTH = MAP_WIDTH * TILE_SIZE   # 1920
MAP_PIXEL_HEIGHT = MAP_HEIGHT * TILE_SIZE  # 1080
UI_BAR_HEIGHT = 280
RENDER_WIDTH = MAP_PIXEL_WIDTH
RENDER_HEIGHT = MAP_PIXEL_HEIGHT + UI_BAR_HEIGHT

# --- Ventana (escalable, inicia en 480p) ---
DEFAULT_WINDOW_WIDTH = 854   # 480p 16:9
DEFAULT_WINDOW_HEIGHT = 480

# --- Influencia del chat (puntos por tipo de interacción) ---
POINTS_MESSAGE = 1
POINTS_BITS = 5
POINTS_SUB = 10
POINTS_DONATION = 15
POINTS_EMOJI = 2

# --- Mini-juego colectivo (votación: movimiento + disparo) ---
VOTE_WINDOW_SECONDS = 8
COMMANDS_VOTE = [
    "!izquierda", "!izq", "!left", "!derecha", "!der", "!right",
    "!arriba", "!up", "!abajo", "!down",
    "!shootright", "!shootleft", "!shootup", "!shootdown",
]

# --- Director de Caos (energía y habilidades) ---
ENERGY_MAX = 100
ENERGY_PER_MESSAGE = 2
ENERGY_COOLDOWN_SECONDS = 30  # Cooldown global tras usar habilidad

# Habilidades y costes base (aumentan con uso)
CHAOS_ABILITIES = {
    "!lag": {"base_cost": 25, "effect": "lag"},
    "!swap": {"base_cost": 35, "effect": "swap"},
    "!npc": {"base_cost": 40, "effect": "npc"},
}

# Coste dinámico: cada uso +X al coste siguiente
CHAOS_COST_INCREASE = 5
CHAOS_RESET_AFTER_USES = 5  # Tras N usos sin usar, el coste baja

# --- Eventos encadenados (!boom) ---
BOOM_CHAIN = {
    5: {"name": "chispa", "effect": "spark"},
    10: {"name": "bomba", "effect": "bomb"},
    20: {"name": "mega_evento", "effect": "mega"},
}

BOOM_COOLDOWN_SECONDS = 15
BOOM_WINDOW_SECONDS = 10  # Ventana para acumular !boom

# --- Emojis → efectos en el mundo ---
EMOJI_EFFECTS = {
    "fire": ["🔥", "flame"],
    "heart": ["❤️", "💕", "💖", "♥️"],
    "rain": ["🌧️", "💧", "🌧"],
    "sun": ["☀️", "🌞", "😎"],
    "star": ["⭐", "🌟", "✨"],
}
