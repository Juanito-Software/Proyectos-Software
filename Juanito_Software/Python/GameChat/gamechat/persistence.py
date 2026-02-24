"""
Persistencia del mundo entre streams - SQLite
"""
import json
import sqlite3
from pathlib import Path
from typing import Any

from config import DB_PATH, DATA_DIR


def ensure_data_dir():
    """Crea el directorio data si no existe."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_connection():
    """Obtiene conexión a la base de datos."""
    ensure_data_dir()
    return sqlite3.connect(DB_PATH)


def init_db():
    """Inicializa las tablas de la base de datos."""
    conn = get_connection()
    cur = conn.cursor()
    
    # Estado del mundo (tiles, edificios, clima, etc.)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS world_state (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    
    # Historial de interacciones (opcional, para análisis)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL,
            user TEXT,
            type TEXT,
            data TEXT
        )
    """)
    
    # Uso de habilidades (para coste dinámico)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chaos_usage (
            ability TEXT PRIMARY KEY,
            use_count INTEGER DEFAULT 0,
            last_reset REAL
        )
    """)
    
    conn.commit()
    conn.close()


def save_world(world_data: dict[str, Any]) -> None:
    """Guarda el estado del mundo."""
    conn = get_connection()
    cur = conn.cursor()
    
    for key, value in world_data.items():
        cur.execute(
            "INSERT OR REPLACE INTO world_state (key, value) VALUES (?, ?)",
            (key, json.dumps(value))
        )
    
    conn.commit()
    conn.close()


def load_world() -> dict[str, Any]:
    """Carga el estado del mundo desde la BD."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT key, value FROM world_state")
    rows = cur.fetchall()
    conn.close()
    
    result = {}
    for key, value in rows:
        try:
            result[key] = json.loads(value) if value else None
        except json.JSONDecodeError:
            result[key] = value
    return result


def save_chaos_usage(usage: dict[str, int]) -> None:
    """Guarda el conteo de uso de habilidades."""
    conn = get_connection()
    cur = conn.cursor()
    import time
    now = time.time()
    for ability, count in usage.items():
        cur.execute(
            """INSERT OR REPLACE INTO chaos_usage (ability, use_count, last_reset)
               VALUES (?, ?, ?)""",
            (ability, count, now)
        )
    conn.commit()
    conn.close()


def load_chaos_usage() -> dict[str, int]:
    """Carga el conteo de uso de habilidades."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT ability, use_count FROM chaos_usage")
    rows = cur.fetchall()
    conn.close()
    return {row[0]: row[1] for row in rows}


def log_interaction(user: str, itype: str, data: Any = None) -> None:
    """Registra una interacción en el historial."""
    import time
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO interactions (timestamp, user, type, data) VALUES (?, ?, ?, ?)",
        (time.time(), user, itype, json.dumps(data) if data is not None else None)
    )
    conn.commit()
    conn.close()
