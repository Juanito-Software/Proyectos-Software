"""Ancla la raiz del proyecto en sys.path para que los tests importen los
modulos sueltos (generar_sprite, generar_spritesheet) sin instalar el paquete.

Sin esto, pytest solo anade `tests/` al path y `import generar_spritesheet`
fallaria con ModuleNotFoundError.
"""

import sys
from pathlib import Path

RAIZ = Path(__file__).parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))
