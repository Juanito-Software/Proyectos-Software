"""Utilidad de un solo uso: borra del results.csv las filas de kind=tile de
un backend dado, para que el siguiente `drag bench run` las regenere con el
prompt corregido (BACKGROUND_HINT ya no se aplica a tiles) en vez de saltarlas
por creer que ya estan hechas.

Uso:
    python bench/_fix_tile_rows.py [ruta_csv] [backend]

Por defecto: bench/out/results.csv, backend sdxl-pixelart.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("bench/out/results.csv")
backend = sys.argv[2] if len(sys.argv) > 2 else "sdxl-pixelart"

with csv_path.open(encoding="utf-8", newline="") as fh:
    rows = list(csv.DictReader(fh))

before = len(rows)
kept = [r for r in rows if not (r["backend"] == backend and r["kind"] == "tile")]
removed = before - len(kept)

if removed == 0:
    print(f"Nada que quitar: no habia filas de backend={backend} kind=tile en {csv_path}.")
    sys.exit(0)

with csv_path.open("w", encoding="utf-8", newline="") as fh:
    writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(kept)

print(f"Quitadas {removed} filas de tile ({backend}) de {csv_path}.")
print(f"Filas restantes: {len(kept)}/{before}.")
print("Ahora puedes volver a correr: drag bench run -b " + backend)
