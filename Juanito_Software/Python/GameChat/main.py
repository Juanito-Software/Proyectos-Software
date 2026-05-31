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

"""
GameChat - Fase 1: Base interactiva y mundo dinámico
Mundo virtual que evoluciona con el chat de Twitch.
"""
import math
import random
import sys
from queue import Queue

import pygame

from config import (
    MAP_WIDTH, MAP_HEIGHT, TILE_SIZE,
    RENDER_WIDTH, RENDER_HEIGHT,
    MAP_PIXEL_HEIGHT,
    DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT,
    SIMULATION_MODE,
    BOOM_CHAIN,
)
from gamechat.chat_listener import ChatListener
from gamechat.event_system import EventSystem
from gamechat.persistence import init_db, load_world, save_world, log_interaction
from gamechat.world_engine import (
    WorldEngine,
    TILE_GRASS, TILE_DIRT, TILE_WATER, TILE_ROAD, TILE_RUIN,
    BUILDING_NONE, BUILDING_HOUSE, BUILDING_SHOP, BUILDING_TOWER, BUILDING_DESTROYED,
    WEATHER_CLEAR, WEATHER_RAIN, WEATHER_SUNNY, WEATHER_STORM,
)


# Radio de jugadores/enemigos: tamaño similar a casas pero un poco más pequeño
# Las casas usan inflate(-8,-8) → (TILE_SIZE-16), radio ~(TILE_SIZE-16)/2. Usamos 85%.
ENTITY_RADIUS = max(12, int((TILE_SIZE - 16) / 2 * 0.85))

# Colores
COLORS = {
    "grass": (76, 153, 0),
    "dirt": (139, 90, 43),
    "water": (65, 105, 225),
    "road": (100, 100, 100),
    "ruin": (80, 70, 60),
    "house": (180, 100, 80),
    "shop": (220, 180, 100),
    "tower": (120, 120, 140),
    "destroyed": (60, 50, 40),
    "ui_bg": (30, 30, 40),
    "energy_bar": (50, 200, 100),
    "energy_bg": (60, 60, 70),
    "vote_left": (255, 100, 100),
    "vote_right": (100, 100, 255),
    "player": (50, 255, 80),      # punto verde
    "enemy": (255, 50, 50),       # punto rojo
}


def tile_to_color(tile: str) -> tuple:
    m = {"grass": "grass", "dirt": "dirt", "water": "water", "road": "road", "ruin": "ruin"}
    return COLORS.get(m.get(tile, "grass"), COLORS["grass"])


def building_to_color(bld: str) -> tuple | None:
    if bld == BUILDING_NONE:
        return None
    m = {BUILDING_HOUSE: "house", BUILDING_SHOP: "shop", BUILDING_TOWER: "tower", BUILDING_DESTROYED: "destroyed"}
    return COLORS.get(m.get(bld, "house"), COLORS["house"])


class GameChatApp:
    def __init__(self):
        pygame.init()
        self.window_w = DEFAULT_WINDOW_WIDTH
        self.window_h = DEFAULT_WINDOW_HEIGHT
        self.screen = pygame.display.set_mode((self.window_w, self.window_h), pygame.RESIZABLE)
        pygame.display.set_caption("GameChat - Mundo influenciado por el chat")
        self.render_surface = pygame.Surface((RENDER_WIDTH, RENDER_HEIGHT))
        self.clock = pygame.time.Clock()
        
        init_db()
        
        self.message_queue: Queue = Queue()
        self.chat_listener = ChatListener(self.message_queue)
        
        self.world = WorldEngine()
        self._load_persisted_world()
        
        self.event_system = EventSystem(event_callback=self._on_event)
        
        # Personaje controlado por votación
        self.player_x = MAP_WIDTH // 2
        self.player_y = MAP_HEIGHT // 2
        self.player_target_x = self.player_x
        self.player_target_y = self.player_y
        self.move_speed = 0.08
        
        # Efectos activos del Director de Caos
        self.chaos_effects = {
            "lag": False,
            "lag_delay": 0.0,
            "swap": False,
            "npc": False,
        }
        
        # Efectos climáticos (partículas)
        self.weather_particles: list[dict] = []
        self.weather_timer = 0.0

        # Spawn automático de aldeano cada 400 s
        self.villager_spawn_timer = 0.0
        
        # Estado del jugador: muerto = respawn pendiente
        self.player_dead = False
        self.death_timer = 0.0
        self.enemigos_derrotados = 0
        self.puntos = 0  # +1 por enemigo, +20 por evento; se resetea al morir
        self.input_buffer: list[str] = []
        self.lag_buffer_delay = 0.15
        
        # Proyectiles activos (balas visibles)
        self.projectiles: list[dict] = []
        self.projectile_speed = 12.0  # casillas por segundo

        # Overlay de mensajes
        self.overlay_messages: list[dict] = []
        self.font = pygame.font.Font(None, 55)
        self.font_large = pygame.font.Font(None, 55)
        self.font_ui = pygame.font.Font(None, 55)
        
        self.chat_listener.start()
    
    def _load_persisted_world(self):
        data = load_world()
        if data:
            if "world" in data:
                self.world.load_from_dict(data["world"])
            if "player" in data:
                p = data["player"]
                self.player_x = p.get("x", MAP_WIDTH // 2)
                self.player_y = p.get("y", MAP_HEIGHT // 2)
                # Mantener también el destino para que no se mueva solo al cargar
                self.player_target_x = p.get("tx", self.player_x)
                self.player_target_y = p.get("ty", self.player_y)
            if "enemigos_derrotados" in data:
                self.enemigos_derrotados = data.get("enemigos_derrotados", 0)
    
    def _save_world(self):
        save_world({
            "world": self.world.to_save_dict(),
            "player": {
                "x": self.player_x,
                "y": self.player_y,
                "tx": self.player_target_x,
                "ty": self.player_target_y,
            },
            "enemigos_derrotados": self.enemigos_derrotados,
        })
    
    def _on_event(self, event_type: str, data: dict):
        """Callback del EventSystem."""
        if event_type == "vote_result":
            self._apply_vote_result(data["action"], data["direction"])
        elif event_type == "chaos_ability":
            self._apply_chaos(data["effect"])
        elif event_type == "boom_event":
            try:
                self.world.apply_boom_event(data["level"])
            except Exception as e:
                # Evitar cierre del juego si algo falla en el manejo del boom
                self._show_overlay("Error al aplicar evento !boom", 3.0)
                return
            self.puntos += 20
            self._show_overlay(f"¡BOOM! Nivel {data['level']} ({data['count']} personas) +20 pts", 3.0)
        elif event_type == "chaos_blocked":
            pass
        elif event_type == "energy_update":
            pass
    
    def _apply_vote_result(self, action: str, direction: str):
        if self.player_dead:
            return
        if action == "shoot":
            self._fire_projectile(direction)
            dir_names = {"left": "izq", "right": "der", "up": "arriba", "down": "abajo"}
            self._show_overlay(f"¡Disparo {dir_names.get(direction, direction)}!", 1.2)
        else:
            dx, dy = 0, 0
            if direction == "left":
                dx = -1
            elif direction == "right":
                dx = 1
            elif direction == "up":
                dy = -1
            elif direction == "down":
                dy = 1
            tx = max(0, min(MAP_WIDTH - 1, int(self.player_x) + dx))
            ty = max(0, min(MAP_HEIGHT - 1, int(self.player_y) + dy))
            self.player_target_x = tx
            self.player_target_y = ty
            dir_names = {"left": "izquierda", "right": "derecha", "up": "arriba", "down": "abajo"}
            self._show_overlay(f"Votación: {dir_names.get(direction, direction)}", 1.5)
    
    def _fire_projectile(self, direction: str):
        """Dispara un proyectil visible en la dirección indicada."""
        dx, dy = 0, 0
        if direction == "right":
            dx = 1
        elif direction == "left":
            dx = -1
        elif direction == "up":
            dy = -1
        elif direction == "down":
            dy = 1
        if dx == 0 and dy == 0:
            return
        self.projectiles.append({
            "x": float(self.player_x),
            "y": float(self.player_y),
            "dx": dx, "dy": dy,
        })

    def _update_projectiles(self, dt: float):
        """Actualiza proyectiles: movimiento, colisión con enemigos (fuera de edificios)."""
        for p in self.projectiles[:]:
            old_x, old_y = p["x"], p["y"]
            p["x"] += p["dx"] * self.projectile_speed * dt
            p["y"] += p["dy"] * self.projectile_speed * dt
            new_x, new_y = p["x"], p["y"]
            # Revisar todos los tiles en el trayecto para no saltarnos enemigos
            steps = max(1, int(abs(new_x - old_x) + abs(new_y - old_y)) + 1)
            hit_tile = None
            for i in range(steps + 1):
                t = i / steps
                tx = int(round(old_x + t * (new_x - old_x)))
                ty = int(round(old_y + t * (new_y - old_y)))
                if not (0 <= tx < MAP_WIDTH and 0 <= ty < MAP_HEIGHT):
                    break
                if self.world.get_hostile_npc_at(tx, ty) and not self.world.is_building_safe(tx, ty):
                    hit_tile = (tx, ty)
                    break
            if hit_tile:
                self.world.remove_npc_at(hit_tile[0], hit_tile[1])
                self.enemigos_derrotados += 1
                self.puntos += 1
                self.world.active_effects.append({
                    "type": "projectile_hit", "x": hit_tile[0], "y": hit_tile[1], "duration": 0.8,
                })
                self.projectiles.remove(p)
            elif not (0 <= int(round(new_x)) < MAP_WIDTH and 0 <= int(round(new_y)) < MAP_HEIGHT):
                self.projectiles.remove(p)
    
    def _apply_chaos(self, effect: str):
        if effect == "lag":
            self.chaos_effects["lag"] = True
            self.chaos_effects["lag_delay"] = 2.0
            self._show_overlay("¡LAG! Movimiento con delay", 2.0)
        elif effect == "swap":
            self.chaos_effects["swap"] = not self.chaos_effects["swap"]
            self._show_overlay("¡SWAP! Controles invertidos", 2.0)
        elif effect == "npc":
            self.world.spawn_enemy_npc()
            self._show_overlay("¡Apareció un enemigo!", 2.0)
    
    def _show_overlay(self, text: str, duration: float = 2.0):
        self.overlay_messages.append({"text": text, "timer": duration})
    
    def _is_on_building(self, x: float, y: float) -> bool:
        """True si estamos en un edificio (casa, tienda, torre) = zona segura."""
        from gamechat.world_engine import BUILDING_NONE, BUILDING_DESTROYED
        ix, iy = int(round(x)), int(round(y))
        if not (0 <= ix < MAP_WIDTH and 0 <= iy < MAP_HEIGHT):
            return False
        b = self.world.buildings[iy][ix]
        return b != BUILDING_NONE and b != BUILDING_DESTROYED
    
    def _respawn_random(self):
        """Respawn en posición aleatoria del mapa (evitando agua)."""
        for _ in range(50):
            x = random.randint(0, MAP_WIDTH - 1)
            y = random.randint(0, MAP_HEIGHT - 1)
            if self.world.tiles[y][x] != TILE_WATER:
                self.player_x = x
                self.player_y = y
                self.player_target_x = x
                self.player_target_y = y
                return
        self.player_x = MAP_WIDTH // 2
        self.player_y = MAP_HEIGHT // 2
        self.player_target_x = self.player_x
        self.player_target_y = self.player_y
    
    def _process_messages(self):
        """Procesa mensajes de la cola del chat."""
        while not self.message_queue.empty():
            try:
                msg = self.message_queue.get_nowait()
            except Exception:
                break
            
            user = msg.get("user", "unknown")
            text = msg.get("message", "")
            bits = msg.get("bits", 0)
            is_sub = msg.get("is_sub", False)
            is_donation = msg.get("is_donation", False)
            emojis = msg.get("emojis", [])
            
            # Detectar tipo de interacción
            if bits > 0:
                itype = "bits"
            elif is_sub:
                itype = "sub"
            elif is_donation:
                itype = "donation"
            elif emojis:
                itype = "emoji"
                self.world.apply_chat_interaction(itype, user, emoji=emojis[0] if emojis else None)
                self.event_system.process_message(user, text, bits, is_sub, is_donation)
                continue
            else:
                itype = "message"
            
            self.world.apply_chat_interaction(itype, user, bits=bits)
            self.event_system.process_message(user, text, bits, is_sub, is_donation)
    
    def _update_player(self, dt: float):
        if self.player_dead:
            return
        if self.chaos_effects["lag"]:
            self.chaos_effects["lag_delay"] -= dt
            if self.chaos_effects["lag_delay"] <= 0:
                self.chaos_effects["lag"] = False
            dt = dt * 0.3
        
        dx = self.player_target_x - self.player_x
        dy = self.player_target_y - self.player_y
        
        if self.chaos_effects["swap"]:
            dx, dy = -dx, -dy
        
        step = self.move_speed * dt * 60
        if abs(dx) > 0.01:
            self.player_x += max(-step, min(step, dx))
        if abs(dy) > 0.01:
            self.player_y += max(-step, min(step, dy))
        
        self.player_x = max(0, min(MAP_WIDTH - 1, self.player_x))
        self.player_y = max(0, min(MAP_HEIGHT - 1, self.player_y))
    
    def _update_weather(self, dt: float):
        """Actualiza partículas del clima según el tipo actual."""
        climate = self.world.climate
        self.weather_timer += dt
        
        if climate == WEATHER_RAIN or climate == WEATHER_STORM:
            if self.weather_timer >= 0.03:
                self.weather_timer = 0
                count = 12 if climate == WEATHER_STORM else 6
                for _ in range(count):
                    self.weather_particles.append({
                        "x": random.randint(0, RENDER_WIDTH),
                        "y": -5,
                        "speed_y": random.uniform(400, 700) if climate == WEATHER_STORM else random.uniform(250, 450),
                        "len": random.randint(6, 12),
                    })
        elif climate == WEATHER_SUNNY:
            if self.weather_timer >= 0.08:
                self.weather_timer = 0
                self.weather_particles.append({
                    "x": random.randint(0, RENDER_WIDTH),
                    "y": random.randint(0, MAP_PIXEL_HEIGHT),
                    "alpha": random.uniform(0.3, 0.7),
                    "size": random.randint(2, 5),
                    "duration": 1.0,
                })
        
        if climate == WEATHER_CLEAR and self.weather_particles:
            self.weather_particles.clear()
        
        for p in self.weather_particles[:]:
            if climate in (WEATHER_RAIN, WEATHER_STORM):
                p["y"] += p["speed_y"] * dt
                if p["y"] > RENDER_HEIGHT:
                    self.weather_particles.remove(p)
            elif climate == WEATHER_SUNNY:
                p["duration"] -= dt
                if p["duration"] <= 0:
                    self.weather_particles.remove(p)
    
    def _draw_weather(self):
        """Dibuja efectos visuales del clima."""
        climate = self.world.climate
        
        if climate == WEATHER_RAIN or climate == WEATHER_STORM:
            color = (60, 120, 255) if climate == WEATHER_STORM else (100, 160, 255)
            for p in self.weather_particles:
                end_y = min(RENDER_HEIGHT, p["y"] + p["len"])
                pygame.draw.line(self.render_surface, color, (p["x"], p["y"]), (p["x"], end_y), 2)
        elif climate == WEATHER_SUNNY:
            for p in self.weather_particles:
                s = pygame.Surface((p["size"] * 2, p["size"] * 2))
                s.set_alpha(int(80 * p.get("alpha", 0.5)))
                pygame.draw.circle(s, (255, 255, 200), (p["size"], p["size"]), p["size"])
                self.render_surface.blit(s, (p["x"] - p["size"], p["y"] - p["size"]))
    
    def run(self):
        running = True
        last_save = 0
        
        while running:
            dt = self.clock.tick(60) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    self.window_w = max(320, event.w)
                    self.window_h = max(200, event.h)
                    self.screen = pygame.display.set_mode((self.window_w, self.window_h), pygame.RESIZABLE)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            self._process_messages()
            self.event_system.update(dt)
            
            if self.player_dead:
                self.death_timer -= dt
                if self.death_timer <= 0:
                    self.player_dead = False
                    self._respawn_random()
            else:
                lag_active = self.chaos_effects.get("lag", False)
                if self.world.update_enemies(
                    self.player_x, self.player_y, dt,
                    lag_active=lag_active,
                    defeated_count=self.enemigos_derrotados,
                ):
                    if not self._is_on_building(self.player_x, self.player_y):
                        self.player_dead = True
                    self.death_timer = 3.0
                    self.puntos = 0
                    self.world.total_influence = max(0, self.world.total_influence - 5)
                    self._show_overlay("¡HAS MUERTO! El enemigo te alcanzó. Puntos reseteados.", 3.0)
            
            self._update_player(dt)
            self._update_projectiles(dt)
            self.world.update_influence_decay(dt)
            self.world.update_effects(dt)
            self._update_weather(dt)

            # Spawn de aldeano cada 400 s
            self.villager_spawn_timer += dt
            if self.villager_spawn_timer >= 400.0:
                self.villager_spawn_timer = 0.0
                self.world.spawn_villager()
                self._show_overlay("¡Apareció un aldeano!", 2.0)

            # Persistencia periódica
            last_save += dt
            if last_save > 30:
                self._save_world()
                last_save = 0
            
            self._draw()
            pygame.display.flip()
        
        self._save_world()
        self.chat_listener.stop()
        pygame.quit()
        sys.exit(0)
    
    def _draw(self):
        surf = self.render_surface
        surf.fill((20, 20, 30))
        
        # Mapa
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                tile = self.world.tiles[y][x]
                surf.fill(tile_to_color(tile), rect)
                
                bld = self.world.buildings[y][x]
                if bld != BUILDING_NONE:
                    col = building_to_color(bld)
                    if col:
                        pygame.draw.rect(surf, col, rect.inflate(-8, -8))
                        pygame.draw.rect(surf, (0, 0, 0), rect.inflate(-8, -8), 1)
        
        # NPCs: enemigos = punto rojo, otros = punto amarillo
        for npc in self.world.npcs:
            nx, ny = npc["x"], npc["y"]
            cx = nx * TILE_SIZE + TILE_SIZE // 2
            cy = ny * TILE_SIZE + TILE_SIZE // 2
            color = COLORS["enemy"] if npc.get("type") == "enemy" else (200, 200, 100)
            pygame.draw.circle(surf, color, (cx, cy), ENTITY_RADIUS)
        
        # Proyectiles (balas)
        for p in self.projectiles:
            px = int(p["x"] * TILE_SIZE + TILE_SIZE // 2)
            py = int(p["y"] * TILE_SIZE + TILE_SIZE // 2)
            pygame.draw.circle(surf, (255, 255, 100), (px, py), 8)
            pygame.draw.circle(surf, (255, 200, 50), (px, py), 6)
        # Efectos activos (partículas, explosiones)
        for eff in self.world.active_effects:
            self._draw_effect(eff)
        
        # Efectos climáticos
        self._draw_weather()
        
        # Player: punto verde (no dibujar si está muerto)
        if not self.player_dead:
            px = int(self.player_x * TILE_SIZE + TILE_SIZE // 2)
            py = int(self.player_y * TILE_SIZE + TILE_SIZE // 2)
            pygame.draw.circle(surf, COLORS["player"], (px, py), ENTITY_RADIUS)
            pygame.draw.circle(surf, (20, 80, 20), (px, py), ENTITY_RADIUS, 1)
        
        # UI inferior
        ui_y = MAP_PIXEL_HEIGHT
        pygame.draw.rect(surf, COLORS["ui_bg"], (0, ui_y, RENDER_WIDTH, RENDER_HEIGHT - ui_y))
        
        # Columna izquierda: energía, votación, boom, comandos
        bar_x = 30
        col2_x = RENDER_WIDTH - 380
        line_h = 58
        y = ui_y + 8
        
        # Barra de energía
        energy = self.event_system.get_energy()
        bar_w = 250
        bar_h = 28
        pygame.draw.rect(surf, COLORS["energy_bg"], (bar_x, y, bar_w, bar_h))
        fill_w = int(bar_w * energy / 100)
        pygame.draw.rect(surf, COLORS["energy_bar"], (bar_x, y, fill_w, bar_h))
        pygame.draw.rect(surf, (200, 200, 200), (bar_x, y, bar_w, bar_h), 1)
        txt = self.font.render(f"Energía: {energy}/100", True, (255, 255, 255))
        txt_x = bar_x + bar_w + 12
        surf.blit(txt, (txt_x, y - 2))
        # Indicador SAFE cuando el jugador está en una casa segura
        if self._is_on_building(self.player_x, self.player_y):
            safe_txt = self.font.render("SAFE", True, (50, 255, 80))
            surf.blit(safe_txt, (txt_x + txt.get_width() + 20, y - 2))
        y += line_h
        
        # Votación (siempre visible): Mv ←→↑↓ | Sh ←→↑↓
        votes = self.event_system.votes or {}
        vtxt = self.font.render(
            f"Mv: {votes.get('move_left',0)}← {votes.get('move_right',0)}→ {votes.get('move_up',0)}↑ {votes.get('move_down',0)}↓  |  Sh: {votes.get('shoot_left',0)}← {votes.get('shoot_right',0)}→ {votes.get('shoot_up',0)}↑ {votes.get('shoot_down',0)}↓",
            True, (255, 255, 255)
        )
        surf.blit(vtxt, (bar_x, y))
        y += line_h
        
        # Boom count
        if self.event_system.boom_count > 0:
            chain_info = " | ".join(f"{k}→{v['name']}" for k, v in sorted(BOOM_CHAIN.items()))
            btxt = self.font.render(f"!boom: {self.event_system.boom_count} ({chain_info})", True, (255, 200, 100))
            surf.blit(btxt, (bar_x, y))
            y += line_h
        
        # Comandos
        cmd_lines = [
            "Mov: !izq !der !up !down  |  Disparo: !shootLeft !shootRight !shootUp !shootDown",
            "Caos: !lag !swap !npc  |  Evento: !boom",
        ]
        for line in cmd_lines:
            ctxt = self.font_ui.render(line, True, (180, 180, 200))
            surf.blit(ctxt, (bar_x, y))
            y += line_h
        
        # Columna 2 (izquierda): contadores
        y2 = ui_y + 8
        ctxt = self.font_ui.render(f"Clima: {self.world.climate}", True, (200, 200, 255))
        surf.blit(ctxt, (col2_x, y2))
        y2 += line_h
        itxt = self.font_ui.render(f"Influencia: {self.world.total_influence}", True, (200, 255, 200))
        surf.blit(itxt, (col2_x, y2))
        y2 += line_h
        ptxt = self.font_ui.render(f"Puntos: {self.puntos}", True, (255, 220, 100))
        surf.blit(ptxt, (col2_x, y2))
        y2 += line_h
        killtxt = self.font_ui.render(f"Derrotados: {self.enemigos_derrotados}", True, (255, 150, 100))
        surf.blit(killtxt, (col2_x, y2))
        
        # Overlay messages
        for msg in self.overlay_messages[:]:
            msg["timer"] -= 0.016
            if msg["timer"] <= 0:
                self.overlay_messages.remove(msg)
            else:
                surf_overlay = self.font_large.render(msg["text"], True, (255, 255, 255))
                r = surf_overlay.get_rect(center=(RENDER_WIDTH // 2, 80))
                pygame.draw.rect(surf, (0, 0, 0), r.inflate(20, 10))
                surf.blit(surf_overlay, r)
        
        # Modo simulación
        if SIMULATION_MODE:
            sim_txt = self.font.render("[Modo simulación - mensajes aleatorios]", True, (150, 150, 150))
            surf.blit(sim_txt, (bar_x, RENDER_HEIGHT - 38))
        
        # Escalar a la ventana actual
        scaled = pygame.transform.smoothscale(surf, (self.window_w, self.window_h))
        self.screen.fill((0, 0, 0))
        self.screen.blit(scaled, (0, 0))
    
    def _draw_effect(self, eff: dict):
        surf = self.render_surface
        eff_type = eff.get("type", "")
        x = eff.get("x", 0) * TILE_SIZE + TILE_SIZE // 2
        y = eff.get("y", 0) * TILE_SIZE + TILE_SIZE // 2
        
        if eff_type == "particle":
            size = 4
            color = (255, 200, 100) if eff.get("subtype") == "spark" else (100, 200, 255)
            pygame.draw.circle(surf, color, (x, y), size)
        elif eff_type == "celebration":
            for i in range(6):
                angle = (eff.get("duration", 1) * 360 + i * 60) % 360
                rx = x + int(15 * math.cos(math.radians(angle)))
                ry = y + int(15 * math.sin(math.radians(angle)))
                pygame.draw.circle(surf, (255, 255, 0), (rx, ry), 3)
        elif eff_type == "emoji_effect":
            color = (255, 100, 100) if eff.get("subtype") == "fire" else (255, 180, 200)
            pygame.draw.circle(surf, color, (x, y), 8)
        elif eff_type == "projectile_hit":
            r = int(8 * (1 - eff.get("duration", 0) / 0.8))
            if r > 0:
                pygame.draw.circle(surf, (255, 200, 50), (x, y), r)
                pygame.draw.circle(surf, (255, 255, 200), (x, y), r, 1)
        elif eff_type == "boom":
            subtype = eff.get("subtype", "spark")
            max_r = 10 if subtype == "spark" else (25 if subtype == "bomb" else 50)
            orig_dur = 1.5 if subtype == "spark" else (2.5 if subtype == "bomb" else 4.0)
            remaining = eff.get("duration", 0)
            progress = 1 - (remaining / orig_dur)
            r = int(max_r * min(1, progress * 1.5))
            alpha = min(255, int(255 * remaining / orig_dur))
            if r > 0 and alpha > 0:
                s = pygame.Surface((r * 2 + 4, r * 2 + 4))
                s.set_colorkey((0, 0, 0))
                col = (255, 150, 0) if subtype != "mega" else (255, 50, 50)
                pygame.draw.circle(s, col, (r + 2, r + 2), r)
                s.set_alpha(alpha)
                surf.blit(s, (x - r - 2, y - r - 2))


if __name__ == "__main__":
    app = GameChatApp()
    app.run()
