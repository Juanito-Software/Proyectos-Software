# GameChat - Fase 1

Mundo virtual dinámico que evoluciona según la actividad del chat de Twitch.

## Requisitos

- Python 3.10+
- pygame, twitchio, aiohttp

## Instalación

```bash
cd GameChat
pip install -r requirements.txt
```

## Ejecución

```bash
python main.py
```

Por defecto corre en **modo simulación**: genera mensajes aleatorios del chat para probar sin conectar a Twitch.

## Conexión a Twitch

1. Crea un archivo `.env` en la raíz del proyecto (o define variables de entorno):

```
TWITCH_CHANNEL=tu_canal
TWITCH_OAUTH=oauth:tu_token_del_bot
GAMECHAT_SIMULATION=false
```

2. Para obtener el token OAuth: [Twitch Chat OAuth Generator](https://twitchapps.com/tmi/)

3. Ejecuta con `GAMECHAT_SIMULATION=false`

## Funcionalidades Fase 1

### 1. Mundo virtual dinámico
- Cada mensaje, bits, suscripción o donación suma puntos de influencia
- Edificios, clima y NPCs cambian según la actividad
- Emojis (🔥❤️💕⭐) generan efectos visuales en el mapa

### 2. Mini-juego colectivo (votación: movimiento + disparo)
- **Movimiento**: `!izquierda`, `!derecha`, `!arriba`, `!abajo` (o !izq, !der, !up, !down)
- **Disparo**: `!shootRight`, `!shootLeft`, `!shootUp`, `!shootDown` — dispara en esa dirección y mata al primer enemigo en la línea
- La **mayoría** tras ~8 segundos decide la acción (mover o disparar)

### 3. Director de Caos
- Cada mensaje suma energía a una barra colectiva
- Al tener suficiente energía, el chat puede usar:
  - `!lag` → el personaje se mueve con delay
  - `!swap` → invierte los controles
  - `!npc` → aparece un enemigo en el mapa
- **Coste dinámico**: cuantas más veces usan una habilidad, más cara se vuelve
- **Cooldown global** tras cada uso

### 4. Eventos encadenados (!boom)
- 5 personas `!boom` → chispa
- 10 personas → bomba (destruye edificios)
- 20 personas → mega evento (destruye varias zonas, cambia clima)

### 5. Objetivo del juego
- **Derrota enemigos**: vota `!shootRight` (etc.) para disparar en esa dirección y eliminar al primer enemigo en la línea
- **Evita a los enemigos**: se mueven hacia ti (cada 2 s normal, 4 s con lag); si te alcanzan, mueres
- **Respawn**: tras morir, reapareces en el centro tras 3 segundos

### 6. Persistencia entre streams
- El estado del mundo se guarda en `data/world_state.db`
- Ciudades destruidas, edificios, NPCs y posición del jugador persisten entre sesiones
