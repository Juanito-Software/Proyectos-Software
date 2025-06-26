# ----------------------------
# 👤 persona_modelo.py (ejemplo que el usuario puede copiar)
# ----------------------------

from dataclasses import dataclass

@dataclass
class Persona:
    ID: int
    Nombre: str
    Apellido: str
    Edad: int
    Email: str
    Teléfono: int
    Ciudad: str
    País: str
    Dirección: str
    Fecha_Registro: str