"""
Motor del mundo virtual: tiles, edificios, clima, NPCs.
Evoluciona según la actividad del chat.
"""
import random
import time
from typing import Any

from config import (
    MAP_WIDTH, MAP_HEIGHT,
    POINTS_MESSAGE, POINTS_BITS, POINTS_SUB, POINTS_DONATION, POINTS_EMOJI,
    EMOJI_EFFECTS,
    VOTE_WINDOW_SECONDS,
)
from gamechat.persistence import load_world, save_world


# Tipos de tile
TILE_GRASS = "grass"
TILE_DIRT = "dirt"
TILE_WATER = "water"
TILE_ROAD = "road"
TILE_RUIN = "ruin"

# Estados de edificios
BUILDING_NONE = "none"
BUILDING_HOUSE = "house"
BUILDING_SHOP = "shop"
BUILDING_TOWER = "tower"
BUILDING_DESTROYED = "destroyed"

# Clima
WEATHER_CLEAR = "clear"
WEATHER_RAIN = "rain"
WEATHER_SUNNY = "sunny"
WEATHER_STORM = "storm"


class WorldEngine:
    def __init__(self):
        self.tiles: list[list[str]] = []
        self.buildings: list[list[str]] = []
        self.climate = WEATHER_CLEAR
        self.npcs: list[dict] = []
        self.influence_points = 0  # Acumulados esta sesión
        self.total_influence = 0  # Histórico
        
        # Decaimiento: tras 3 min sin chat, -1 punto cada 60 s de silencio
        self._last_activity_time = time.time()
        self._decay_accumulator = 0.0
        
        # Efectos activos (para la vista)
        self.active_effects: list[dict] = []
        self.spawn_queue: list[dict] = []  # Efectos pendientes de mostrar
        
        self._init_grid()
    
    def _init_grid(self):
        """Inicializa la cuadrícula del mapa."""
        self.tiles = [[TILE_GRASS for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
        self.buildings = [[BUILDING_NONE for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
        
        # Algunas calles y agua inicial
        for y in range(MAP_HEIGHT):
            if y == MAP_HEIGHT // 2:
                for x in range(MAP_WIDTH):
                    self.tiles[y][x] = TILE_ROAD
            if y < 2:
                self.tiles[y][MAP_WIDTH // 2] = TILE_WATER
        
        # Edificios iniciales
        self.buildings[2][3] = BUILDING_HOUSE
        self.buildings[2][6] = BUILDING_SHOP
        self.buildings[2][9] = BUILDING_TOWER
        self.buildings[10][5] = BUILDING_HOUSE
        self.buildings[10][12] = BUILDING_SHOP
    
    def apply_chat_interaction(self, itype: str, user: str = "", bits: int = 0, 
                               emoji: str = None) -> dict[str, Any]:
        """
        Aplica una interacción del chat al mundo.
        Retorna el efecto generado para mostrarlo.
        """
        points = 0
        effect = None
        
        if itype == "message":
            points = POINTS_MESSAGE
            effect = self._effect_from_message()
        elif itype == "bits":
            points = POINTS_BITS * min(bits, 100)
            effect = self._effect_big("bits", user)
        elif itype == "sub":
            points = POINTS_SUB
            effect = self._effect_big("sub", user)
        elif itype == "donation":
            points = POINTS_DONATION
            effect = self._effect_big("donation", user)
        elif itype == "emoji":
            points = POINTS_EMOJI
            effect = self._effect_from_emoji(emoji or "")
        
        if points > 0:
            self.influence_points += points
            self.total_influence += points
            self._last_activity_time = time.time()
            self._decay_accumulator = 0.0
            self._apply_influence(points)
        
        if effect:
            self.active_effects.append(effect)
            self.spawn_queue.append(effect)
        
        return effect or {}
    
    def _effect_from_message(self) -> dict:
        """Efecto menor por mensaje: pequeña partícula o cambio sutil."""
        x = random.randint(2, MAP_WIDTH - 3)
        y = random.randint(2, MAP_HEIGHT - 3)
        return {
            "type": "particle",
            "x": x, "y": y,
            "subtype": random.choice(["spark", "bubble", "leaf"]),
            "duration": 1.0,
        }
    
    def _effect_big(self, subtype: str, user: str) -> dict:
        """Efecto grande por bits/sub/donation."""
        x = random.randint(3, MAP_WIDTH - 4)
        y = random.randint(3, MAP_HEIGHT - 4)
        return {
            "type": "celebration",
            "x": x, "y": y,
            "subtype": subtype,
            "user": user,
            "duration": 2.5,
        }
    
    def _effect_from_emoji(self, emoji: str) -> dict | None:
        """Traduce emoji a efecto visible."""
        for effect_name, emojis in EMOJI_EFFECTS.items():
            if emoji in emojis:
                x = random.randint(2, MAP_WIDTH - 3)
                y = random.randint(2, MAP_HEIGHT - 3)
                return {
                    "type": "emoji_effect",
                    "x": x, "y": y,
                    "subtype": effect_name,
                    "emoji": emoji,
                    "duration": 2.0,
                }
        return None
    
    def _apply_influence(self, points: int):
        """El mundo cambia según puntos de influencia acumulados."""
        # Cada X puntos: posibilidad de construir/destruir/cambiar clima
        threshold = 50
        if self.total_influence > 0 and self.total_influence % threshold < points:
            roll = random.random()
            if roll < 0.3:
                self._maybe_build()
            elif roll < 0.5:
                self._maybe_climate_change()
            elif roll < 0.7:
                self._maybe_spawn_npc()
    
    def _maybe_build(self):
        """Intenta construir en un tile vacío."""
        candidates = [
            (y, x) for y in range(MAP_HEIGHT) for x in range(MAP_WIDTH)
            if self.buildings[y][x] == BUILDING_NONE and self.tiles[y][x] == TILE_GRASS
        ]
        if not candidates:
            return
        y, x = random.choice(candidates)
        self.buildings[y][x] = random.choice([BUILDING_HOUSE, BUILDING_SHOP])
    
    def _maybe_climate_change(self):
        """Cambia el clima según influencia."""
        opts = [WEATHER_CLEAR, WEATHER_RAIN, WEATHER_SUNNY, WEATHER_STORM]
        self.climate = random.choice(opts)
    
    def _maybe_spawn_npc(self):
        """Añade un NPC amigable (por influencia del chat)."""
        self.spawn_villager()

    def spawn_villager(self):
        """Spawnea un aldeano o comerciante en posición aleatoria."""
        x = random.randint(1, MAP_WIDTH - 2)
        y = random.randint(1, MAP_HEIGHT - 2)
        self.npcs.append({
            "x": x, "y": y,
            "type": random.choice(["villager", "merchant"]),
            "id": len(self.npcs) + 1,
        })
    
    def apply_boom_event(self, level: str) -> dict:
        """Aplica evento encadenado !boom (chispa, bomba, mega)."""
        if level == "spark":
            return self._boom_spark()
        elif level == "bomb":
            return self._boom_bomb()
        elif level == "mega":
            return self._boom_mega()
        return {}
    
    def _boom_spark(self) -> dict:
        x, y = random.randint(2, MAP_WIDTH-3), random.randint(2, MAP_HEIGHT-3)
        eff = {"type": "boom", "subtype": "spark", "x": x, "y": y, "duration": 1.5}
        self.spawn_queue.append(eff)
        self.active_effects.append(eff)
        return {"type": "boom", "subtype": "spark", "x": x, "y": y}
    
    def _boom_bomb(self) -> dict:
        cx, cy = MAP_WIDTH // 2, MAP_HEIGHT // 2
        # Destruye edificios en radio 2
        destroyed = []
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                x, y = cx + dx, cy + dy
                if 0 <= x < MAP_WIDTH and 0 <= y < MAP_HEIGHT:
                    if self.buildings[y][x] != BUILDING_NONE:
                        self.buildings[y][x] = BUILDING_DESTROYED
                        self.tiles[y][x] = TILE_RUIN
                        destroyed.append((x, y))
        eff = {"type": "boom", "subtype": "bomb", "x": cx, "y": cy, "duration": 2.5}
        self.spawn_queue.append(eff)
        self.active_effects.append(eff)
        return {"type": "boom", "subtype": "bomb", "x": cx, "y": cy, "destroyed": destroyed}
    
    def _boom_mega(self) -> dict:
        # Mega evento: cambia clima, destruye varias zonas, gran explosión visual
        self.climate = WEATHER_STORM if self.climate != WEATHER_STORM else WEATHER_RAIN
        for _ in range(3):
            self._boom_bomb()
        cx, cy = MAP_WIDTH // 2, MAP_HEIGHT // 2
        eff = {"type": "boom", "subtype": "mega", "x": cx, "y": cy, "duration": 4.0}
        self.spawn_queue.append(eff)
        self.active_effects.append(eff)
        return {"type": "boom", "subtype": "mega", "x": cx, "y": cy}
    
    def remove_npc_at(self, x: int, y: int):
        """Elimina NPC en posición (vencer enemigo al moverse sobre él)."""
        self.npcs = [n for n in self.npcs if (n["x"], n["y"]) != (x, y)]
    
    def get_enemy_at(self, x: int, y: int) -> dict | None:
        """Devuelve el enemigo en esa posición, o None."""
        for n in self.npcs:
            if n.get("type") == "enemy" and n["x"] == x and n["y"] == y:
                return n
        return None

    def get_hostile_npc_at(self, x: int, y: int) -> dict | None:
        """Devuelve enemigo o aldeano/comerciante hostil en esa posición (matan y pueden ser eliminados)."""
        for n in self.npcs:
            if n["x"] == x and n["y"] == y:
                t = n.get("type")
                if t in ("enemy", "villager", "merchant"):
                    return n
        return None
    
    def is_building_safe(self, x: int, y: int) -> bool:
        """True si en esa posición hay edificio (casa/tienda/torre) = zona segura e inmortal."""
        if not (0 <= x < MAP_WIDTH and 0 <= y < MAP_HEIGHT):
            return False
        b = self.buildings[y][x]
        return b != BUILDING_NONE and b != BUILDING_DESTROYED

    def get_first_enemy_in_line(self, start_x: int, start_y: int, dx: int, dy: int) -> tuple[int, int] | None:
        """Primer enemigo en la línea que pueda morir (no en edificio)."""
        x, y = start_x, start_y
        for _ in range(max(MAP_WIDTH, MAP_HEIGHT)):
            x += dx
            y += dy
            if not (0 <= x < MAP_WIDTH and 0 <= y < MAP_HEIGHT):
                return None
            if self.get_hostile_npc_at(x, y) and not self.is_building_safe(x, y):
                return (x, y)
        return None

    def update_enemies(self, player_x: float, player_y: float, dt: float,
                       lag_active: bool = False, defeated_count: int = 0) -> bool:
        """
        Mueve los enemigos hacia el jugador.
        El jugador solo se mueve cuando hay votación (~VOTE_WINDOW_SECONDS), así que esa es
        la velocidad efectiva de referencia.
        80% probabilidad: 5x más lento que jugador (margen para cuando hay lag).
        20% probabilidad: 2x más lento que jugador.
        Además, la velocidad de ambos tipos de enemigos aumenta de forma exponencial:
        por cada 10 enemigos derrotados, su velocidad se duplica (intervalos / 2).
        Retorna True si algún enemigo alcanzó al jugador (jugador muere).
        """
        # Jugador efectivo: ~1 casilla por ventana de votación (8-10 s)
        player_sec_per_tile = VOTE_WINDOW_SECONDS
        # Escalado exponencial suave por derrotas:
        # cada bloque de 10 derrotas aumenta la velocidad un ~10% (factor 1.1),
        # de forma que tras muchas bajas el juego se vuelve desafiante pero no
        # se dispara tan bruscamente como con duplicaciones.
        tiers = max(0, defeated_count // 10)
        speed_factor = 1.1 ** tiers if tiers > 0 else 1
        interval_slow = (player_sec_per_tile * 5) / speed_factor   # 80%: 5x más lento (~40 s/casilla inicial)
        interval_faster = (player_sec_per_tile * 2) / speed_factor  # 20%: 2x más lento (~16 s/casilla inicial)

        px, py = int(round(player_x)), int(round(player_y))
        for n in self.npcs:
            if n.get("type") != "enemy":
                continue
            n["move_timer"] = n.get("move_timer", 0) + dt
            interval = n.get("next_interval")
            if interval is None:
                interval = interval_slow if random.random() < 0.80 else interval_faster
                n["next_interval"] = interval
            if n["move_timer"] >= interval:
                n["move_timer"] = 0
                n["next_interval"] = interval_slow if random.random() < 0.80 else interval_faster
                ex, ey = n["x"], n["y"]
                dx = 0 if ex == px else (1 if px > ex else -1)
                dy = 0 if ey == py else (1 if py > ey else -1)
                nx, ny = ex, ey
                if dx != 0:
                    nx = ex + dx
                elif dy != 0:
                    ny = ey + dy

                # No permitir entrar en un edificio ya ocupado (jugador u otro NPC)
                if self.is_building_safe(nx, ny):
                    occupied = False
                    if (nx, ny) == (px, py):
                        occupied = True
                    else:
                        for other in self.npcs:
                            if other is n:
                                continue
                            if other.get("x") == nx and other.get("y") == ny:
                                occupied = True
                                break
                    if occupied:
                        continue  # salto de este tick, no se mueve

                if (nx, ny) == (px, py):
                    # Jugador fuera de edificio seguro: muerte
                    if not self.is_building_safe(px, py):
                        return True
                if 0 <= nx < MAP_WIDTH and 0 <= ny < MAP_HEIGHT:
                    n["x"], n["y"] = nx, ny
        # Aldeanos/comerciantes: se mueven en dirección aleatoria cada 90 s, matan al jugador
        VILLAGER_MOVE_INTERVAL = 90.0
        for n in self.npcs:
            if n.get("type") not in ("villager", "merchant"):
                continue
            n["move_timer"] = n.get("move_timer", 0) + dt
            if n["move_timer"] >= VILLAGER_MOVE_INTERVAL:
                n["move_timer"] = 0
                ex, ey = n["x"], n["y"]
                dx, dy = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
                nx, ny = ex + dx, ey + dy

                # No permitir entrar en un edificio ya ocupado (jugador u otro NPC)
                if self.is_building_safe(nx, ny):
                    occupied = False
                    if (nx, ny) == (px, py):
                        occupied = True
                    else:
                        for other in self.npcs:
                            if other is n:
                                continue
                            if other.get("x") == nx and other.get("y") == ny:
                                occupied = True
                                break
                    if occupied:
                        continue

                if (nx, ny) == (px, py):
                    # Jugador fuera de edificio seguro: muerte
                    if not self.is_building_safe(px, py):
                        return True
                if 0 <= nx < MAP_WIDTH and 0 <= ny < MAP_HEIGHT:
                    n["x"], n["y"] = nx, ny
        return False
    
    def spawn_enemy_npc(self) -> dict:
        """Spawn de enemigo (habilidad !npc)."""
        x = random.randint(1, MAP_WIDTH - 2)
        y = random.randint(1, MAP_HEIGHT - 2)
        enemy = {"x": x, "y": y, "type": "enemy", "id": len(self.npcs) + 100}
        self.npcs.append(enemy)
        self.spawn_queue.append({"type": "spawn_enemy", "x": x, "y": y, "duration": 2.0})
        return {"type": "spawn_enemy", "x": x, "y": y}
    
    def to_save_dict(self) -> dict:
        """Serializa el estado para persistencia."""
        return {
            "tiles": self.tiles,
            "buildings": self.buildings,
            "climate": self.climate,
            "npcs": self.npcs,
            "total_influence": self.total_influence,
        }
    
    def load_from_dict(self, data: dict):
        """Carga estado desde persistencia."""
        if "tiles" in data:
            loaded = data["tiles"]
            if len(loaded) == MAP_HEIGHT and len(loaded[0]) == MAP_WIDTH:
                self.tiles = loaded
        if "buildings" in data:
            loaded = data["buildings"]
            if len(loaded) == MAP_HEIGHT and len(loaded[0]) == MAP_WIDTH:
                self.buildings = loaded
        if "climate" in data:
            self.climate = data["climate"]
        if "npcs" in data:
            self.npcs = [
                n for n in data["npcs"]
                if 0 <= n.get("x", 0) < MAP_WIDTH and 0 <= n.get("y", 0) < MAP_HEIGHT
            ]
        if "total_influence" in data:
            self.total_influence = data["total_influence"]
        self._last_activity_time = time.time()
        self._decay_accumulator = 0.0
    
    def update_influence_decay(self, dt: float):
        """Tras 3 min sin actividad, pierde 1 punto cada 60 s de silencio."""
        now = time.time()
        elapsed = now - self._last_activity_time
        if elapsed <= 180:
            self._decay_accumulator = 0.0
            return
        self._decay_accumulator += dt
        while self._decay_accumulator >= 60 and self.total_influence > 0:
            self.total_influence = max(0, self.total_influence - 1)
            self._decay_accumulator -= 60

    def update_effects(self, dt: float):
        """Actualiza y elimina efectos caducados."""
        for e in self.active_effects[:]:
            e["duration"] = e.get("duration", 1) - dt
            if e["duration"] <= 0:
                self.active_effects.remove(e)
