"""
Listener de Twitch chat - conecta al IRC y emite eventos.
También soporta modo simulación para pruebas sin Twitch real.
"""
import asyncio
import random
import threading
import time
from queue import Queue
from typing import Callable

from config import TWITCH_CHANNEL, TWITCH_OAUTH, SIMULATION_MODE


class ChatListener:
    """Escucha el chat de Twitch y envía mensajes a una cola."""
    
    def __init__(self, message_queue: Queue):
        self.message_queue = message_queue
        self.running = False
        self._thread = None
        self._loop = None
    
    def start(self):
        """Inicia el listener (en hilo separado si es Twitch real)."""
        self.running = True
        
        if SIMULATION_MODE or not TWITCH_OAUTH:
            self._thread = threading.Thread(target=self._simulation_loop, daemon=True)
            self._thread.start()
            return
        
        # Twitch real
        self._thread = threading.Thread(target=self._twitch_loop, daemon=True)
        self._thread.start()
    
    def stop(self):
        self.running = False
        if self._thread:
            self._thread.join(timeout=2)
    
    def _simulation_loop(self):
        """Simula mensajes del chat para pruebas."""
        sim_messages = [
            ("user1", "!izquierda"),
            ("user2", "!derecha"),
            ("user3", "!shootRight"),
            ("user4", "!shootLeft"),
            ("user5", "Hola!"),
            ("user6", "!boom"),
            ("user7", "!lag"),
            ("user8", "!fuego"),
            ("user9", "❤️"),
        ]
        idx = 0
        while self.running:
            time.sleep(random.uniform(2, 6))
            if not self.running:
                break
            msg = sim_messages[idx % len(sim_messages)]
            self.message_queue.put({
                "user": msg[0] + str(idx % 5),
                "message": msg[1],
                "bits": 0,
                "is_sub": random.random() < 0.1,
                "is_donation": False,
                "emojis": [msg[1]] if msg[1] in "🔥❤️💕⭐" else [],
            })
            idx += 1
    
    def _twitch_loop(self):
        """Loop asyncio para Twitch."""
        try:
            from twitchio.ext import commands
        except ImportError:
            return
        
        class Bot(commands.Bot):
            def __init__(bot_self, token, prefix, initial_channels, queue):
                super().__init__(token=token, prefix=prefix, initial_channels=initial_channels)
                bot_self.msg_queue = queue
            
            async def event_message(bot_self, msg):
                if msg.echo:
                    return
                # Detectar bits, sub, etc. según la API de twitchio
                bits = 0
                if hasattr(msg, "bits") and msg.bits:
                    bits = msg.bits
                bot_self.msg_queue.put({
                    "user": msg.author.name,
                    "message": msg.content,
                    "bits": bits,
                    "is_sub": msg.author.is_subscriber if hasattr(msg.author, "is_subscriber") else False,
                    "is_donation": False,
                    "emojis": [],  # Extraer de tags si está disponible
                })
        
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        
        bot = Bot(
            token=TWITCH_OAUTH,
            prefix="!",
            initial_channels=[TWITCH_CHANNEL],
            queue=self.message_queue,
        )
        
        self._loop.run_until_complete(bot.start())
    
    @staticmethod
    def extract_emojis(text: str) -> list[str]:
        """Extrae emojis conocidos del texto."""
        from config import EMOJI_EFFECTS
        found = []
        for emojis in EMOJI_EFFECTS.values():
            for e in emojis:
                if e in text:
                    found.append(e)
        return found
