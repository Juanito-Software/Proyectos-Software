"""
Sistema de eventos: votación colectiva, Director de Caos, eventos encadenados.
"""
import time
from collections import defaultdict
from queue import Queue
from typing import Callable

from config import (
    VOTE_WINDOW_SECONDS,
    COMMANDS_VOTE,
    ENERGY_MAX, ENERGY_PER_MESSAGE, ENERGY_COOLDOWN_SECONDS,
    CHAOS_ABILITIES, CHAOS_COST_INCREASE, CHAOS_RESET_AFTER_USES,
    BOOM_CHAIN, BOOM_COOLDOWN_SECONDS, BOOM_WINDOW_SECONDS,
)
from gamechat.persistence import load_chaos_usage, save_chaos_usage


class EventSystem:
    """Gestiona votaciones, energía, habilidades y eventos encadenados."""
    
    def __init__(self, event_callback: Callable[[str, dict], None]):
        self.event_callback = event_callback  # (event_type, data) -> None
        self.event_queue: Queue = Queue()
        
        # --- Votación colectiva ---
        self.votes: dict[str, int] = defaultdict(int)  # "left" -> count, "right" -> count, etc.
        self.vote_window_end = 0.0
        self.vote_active = False
        self.last_vote_result = None
        
        # --- Director de Caos ---
        self.energy = 0
        self.chaos_cooldown_until = 0.0
        self.chaos_usage = load_chaos_usage()
        self.chaos_uses_since_reset: dict[str, int] = defaultdict(int)
        
        # --- Eventos encadenados !boom ---
        self.boom_count = 0
        self.boom_window_end = 0.0
        self.boom_cooldown_until = 0.0
        self.boom_last_level = None
    
    def process_message(self, username: str, message: str, bits: int = 0, 
                        is_sub: bool = False, is_donation: bool = False):
        """Procesa un mensaje del chat y emite eventos."""
        msg_lower = message.strip().lower()
        
        # 1. Cualquier mensaje suma energía
        if bits > 0:
            self._add_energy(ENERGY_PER_MESSAGE * 2)  # bits dan más
        else:
            self._add_energy(ENERGY_PER_MESSAGE)
        
        # 2. Comandos de votación
        if self._is_vote_command(msg_lower):
            self._handle_vote(username, msg_lower)
            return
        
        # 3. Habilidades Director de Caos
        for cmd, cfg in CHAOS_ABILITIES.items():
            if msg_lower == cmd or msg_lower.startswith(cmd + " "):
                self._try_chaos_ability(username, cmd)
                return
        
        # 4. Evento encadenado !boom
        if msg_lower == "!boom":
            self._handle_boom(username)
    
    def _add_energy(self, amount: int):
        self.energy = min(ENERGY_MAX, self.energy + amount)
        self.event_callback("energy_update", {"energy": self.energy})
    
    def _is_vote_command(self, msg: str) -> bool:
        return msg in COMMANDS_VOTE
    
    def _normalize_vote(self, msg: str) -> str:
        """Convierte variantes a dirección única. shoot_* para disparos."""
        move_left = ["!izquierda", "!izq", "!left"]
        move_right = ["!derecha", "!der", "!right"]
        move_up = ["!arriba", "!up"]
        move_down = ["!abajo", "!down"]
        shoot_left = ["!shootleft"]
        shoot_right = ["!shootright"]
        shoot_up = ["!shootup"]
        shoot_down = ["!shootdown"]
        if msg in move_left:
            return "move_left"
        if msg in move_right:
            return "move_right"
        if msg in move_up:
            return "move_up"
        if msg in move_down:
            return "move_down"
        if msg in shoot_left:
            return "shoot_left"
        if msg in shoot_right:
            return "shoot_right"
        if msg in shoot_up:
            return "shoot_up"
        if msg in shoot_down:
            return "shoot_down"
        return msg
    
    def _handle_vote(self, user: str, msg: str):
        now = time.time()
        direction = self._normalize_vote(msg)
        
        if not self.vote_active or now > self.vote_window_end:
            self.vote_active = True
            self.vote_window_end = now + VOTE_WINDOW_SECONDS
            self.votes.clear()
        
        self.votes[direction] += 1
        self.event_callback("vote_update", {
            "votes": dict(self.votes),
            "window_ends": self.vote_window_end,
        })
        
        # Resolver si la ventana acabó (se hace en update)
    
    def update(self, dt: float) -> dict | None:
        """Llamar cada frame. Resuelve votaciones y ventanas."""
        now = time.time()
        
        # Resolver votación al final de ventana
        if self.vote_active and now >= self.vote_window_end:
            self.vote_active = False
            winner = max(self.votes, key=self.votes.get) if self.votes else None
            if winner:
                self.last_vote_result = winner
                is_shoot = winner.startswith("shoot_")
                direction = winner.replace("shoot_", "").replace("move_", "")
                self.event_callback("vote_result", {
                    "action": "shoot" if is_shoot else "move",
                    "direction": direction,
                    "votes": dict(self.votes),
                })
                return {"type": "vote_result", "action": "shoot" if is_shoot else "move", "direction": direction}
            self.votes.clear()
        
        # Reducir cooldown chaos
        if now >= self.chaos_cooldown_until and self.chaos_cooldown_until > 0:
            self.chaos_cooldown_until = 0
        
        # Ventana !boom: al terminar, ejecutar evento según count alcanzado
        if self.boom_window_end > 0 and now >= self.boom_window_end:
            level_triggered = None
            for threshold, cfg in sorted(BOOM_CHAIN.items(), reverse=True):
                if self.boom_count >= threshold:
                    level_triggered = cfg["effect"]
                    break
            if level_triggered:
                self.boom_last_level = level_triggered
                self.boom_cooldown_until = now + BOOM_COOLDOWN_SECONDS
                self.event_callback("boom_event", {"level": level_triggered, "count": self.boom_count})
            self.boom_count = 0
            self.boom_window_end = 0
        
        return None
    
    def _try_chaos_ability(self, user: str, cmd: str):
        now = time.time()
        
        if now < self.chaos_cooldown_until:
            self.event_callback("chaos_blocked", {"reason": "cooldown"})
            return
        
        cfg = CHAOS_ABILITIES[cmd]
        base_cost = cfg["base_cost"]
        extra = self.chaos_usage.get(cmd, 0) * CHAOS_COST_INCREASE
        cost = base_cost + extra
        
        if self.energy < cost:
            self.event_callback("chaos_blocked", {"reason": "insufficient_energy", "cost": cost})
            return
        
        self.energy -= cost
        self.chaos_cooldown_until = now + ENERGY_COOLDOWN_SECONDS
        self.chaos_usage[cmd] = self.chaos_usage.get(cmd, 0) + 1
        self.chaos_uses_since_reset[cmd] += 1
        
        if self.chaos_uses_since_reset[cmd] >= CHAOS_RESET_AFTER_USES:
            self.chaos_usage[cmd] = max(0, self.chaos_usage.get(cmd, 0) - 1)
            self.chaos_uses_since_reset[cmd] = 0
        
        save_chaos_usage(dict(self.chaos_usage))
        
        self.event_callback("chaos_ability", {
            "ability": cmd,
            "effect": cfg["effect"],
            "user": user,
        })
    
    def _handle_boom(self, user: str):
        now = time.time()
        
        if now < self.boom_cooldown_until:
            return
        
        if self.boom_window_end == 0 or now > self.boom_window_end:
            self.boom_window_end = now + BOOM_WINDOW_SECONDS
            self.boom_count = 0
        
        self.boom_count += 1
        self.event_callback("boom_count_update", {"count": self.boom_count, "user": user})
        # No activar aquí: solo al final de la ventana (en update) para poder llegar a 10 o 20
    
    def get_energy(self) -> int:
        return self.energy
    
    def get_chaos_costs(self) -> dict[str, int]:
        """Coste actual de cada habilidad (dinámico)."""
        costs = {}
        for cmd, cfg in CHAOS_ABILITIES.items():
            extra = self.chaos_usage.get(cmd, 0) * CHAOS_COST_INCREASE
            costs[cmd] = cfg["base_cost"] + extra
        return costs
