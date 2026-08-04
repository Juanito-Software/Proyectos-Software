#!/usr/bin/env python3
"""
obs_random_image.py

Cambia periodicamente (por defecto cada 30s) la imagen de una fuente de tipo
"Image Source" en OBS Studio, eligiendo un archivo al azar de una carpeta.

Requisitos:
    - OBS Studio 28+ (trae integrado el servidor obs-websocket v5)
    - Habilitar el servidor: Herramientas > Configuracion del servidor WebSocket
      (activar servidor, anotar puerto y contrasena si la has puesto)
    - Instalar la libreria cliente:
        pip install obsws-python

Uso basico:
    python obs_random_image.py --folder "C:/ruta/a/tus/imagenes" --source "MiFuenteDeImagen"

Uso completo (todos los parametros):
    python obs_random_image.py \
        --folder /ruta/a/imagenes \
        --source "MiFuenteDeImagen" \
        --interval 30 \
        --host localhost \
        --port 4455 \
        --password "tu_password_opcional" \
        --no-repeat

El programa se queda corriendo en un bucle infinito hasta que lo pares con
Ctrl+C, momento en el que se desconecta limpiamente de OBS.
"""

import argparse
import os
import random
import sys
import time
from pathlib import Path

try:
    import obsws_python as obs
except ImportError:
    print(
        "ERROR: falta la libreria 'obsws-python'.\n"
        "Instalala con:  pip install obsws-python"
    )
    sys.exit(1)


EXTENSIONES_VALIDAS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}


def listar_imagenes(carpeta: Path) -> list[Path]:
    """Devuelve la lista de rutas absolutas a imagenes validas dentro de la carpeta."""
    if not carpeta.is_dir():
        print(f"ERROR: la carpeta '{carpeta}' no existe o no es un directorio.")
        sys.exit(1)

    imagenes = [
        p.resolve()
        for p in carpeta.iterdir()
        if p.is_file() and p.suffix.lower() in EXTENSIONES_VALIDAS
    ]

    if not imagenes:
        print(f"ERROR: no se encontraron imagenes validas en '{carpeta}'.")
        print(f"Extensiones aceptadas: {', '.join(sorted(EXTENSIONES_VALIDAS))}")
        sys.exit(1)

    return imagenes


def conectar_obs(host: str, port: int, password: str) -> "obs.ReqClient":
    """Crea y devuelve el cliente conectado al servidor obs-websocket."""
    try:
        cliente = obs.ReqClient(host=host, port=port, password=password, timeout=5)
        version = cliente.get_version()
        print(
            f"Conectado a OBS Studio {version.obs_version} "
            f"(obs-websocket {version.obs_web_socket_version})"
        )
        return cliente
    except Exception as e:
        print(f"ERROR: no se pudo conectar a OBS en {host}:{port}")
        print(f"Detalle: {e}")
        print(
            "Comprueba que OBS esta abierto, que el servidor WebSocket esta "
            "activado (Herramientas > Configuracion del servidor WebSocket) "
            "y que el puerto/contrasena son correctos."
        )
        sys.exit(1)


def verificar_fuente(cliente: "obs.ReqClient", nombre_fuente: str) -> None:
    """Comprueba que la fuente existe y avisa si su tipo no parece ser una imagen."""
    try:
        settings = cliente.get_input_settings(nombre_fuente)
    except Exception as e:
        print(f"ERROR: la fuente '{nombre_fuente}' no existe o no es accesible.")
        print(f"Detalle: {e}")
        sys.exit(1)

    kind = getattr(settings, "input_kind", "") or ""
    if "image_source" not in kind:
        print(
            f"Aviso: la fuente '{nombre_fuente}' es de tipo '{kind}', "
            "no de tipo Image Source. El script intentara igualmente "
            "escribir la propiedad 'file', pero puede no tener efecto."
        )


def cambiar_imagen(cliente: "obs.ReqClient", nombre_fuente: str, ruta_imagen: Path) -> None:
    """Actualiza la propiedad 'file' de la fuente de imagen indicada."""
    cliente.set_input_settings(
        nombre_fuente,
        {"file": str(ruta_imagen)},
        overlay=True,
    )


def bucle_principal(args: argparse.Namespace) -> None:
    carpeta = Path(args.folder)
    imagenes = listar_imagenes(carpeta)
    print(f"Se han encontrado {len(imagenes)} imagenes en '{carpeta}'.")

    cliente = conectar_obs(args.host, args.port, args.password)
    verificar_fuente(cliente, args.source)

    ultima_imagen = None

    print(
        f"Iniciando bucle: cambiando '{args.source}' cada {args.interval}s. "
        "Pulsa Ctrl+C para detener."
    )

    try:
        while True:
            if args.no_repeat and len(imagenes) > 1:
                candidatas = [img for img in imagenes if img != ultima_imagen]
            else:
                candidatas = imagenes

            imagen_elegida = random.choice(candidatas)
            ultima_imagen = imagen_elegida

            try:
                cambiar_imagen(cliente, args.source, imagen_elegida)
                print(f"[{time.strftime('%H:%M:%S')}] Imagen actual: {imagen_elegida.name}")
            except Exception as e:
                print(f"Aviso: fallo al cambiar la imagen ({e}). Reintentando en el siguiente ciclo.")

            time.sleep(args.interval)

    except KeyboardInterrupt:
        print("\nDetenido por el usuario.")
    finally:
        try:
            cliente.disconnect()
        except Exception:
            pass
        print("Desconectado de OBS. Fin del programa.")


def parsear_argumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Cambia aleatoriamente la imagen de una fuente de OBS cada N segundos."
    )
    parser.add_argument(
        "--folder", "-f", required=True,
        help="Carpeta que contiene las imagenes a rotar."
    )
    parser.add_argument(
        "--source", "-s", required=True,
        help="Nombre exacto de la fuente 'Image Source' en OBS."
    )
    parser.add_argument(
        "--interval", "-i", type=float, default=30.0,
        help="Segundos entre cada cambio de imagen (por defecto: 30)."
    )
    parser.add_argument(
        "--host", default="localhost",
        help="Host del servidor obs-websocket (por defecto: localhost)."
    )
    parser.add_argument(
        "--port", type=int, default=4455,
        help="Puerto del servidor obs-websocket (por defecto: 4455)."
    )
    parser.add_argument(
        "--password", default="",
        help="Contrasena del servidor obs-websocket (vacia si no la has configurado)."
    )
    parser.add_argument(
        "--no-repeat", action="store_true",
        help="Evita repetir la misma imagen dos veces seguidas."
    )
    return parser.parse_args()


if __name__ == "__main__":
    argumentos = parsear_argumentos()
    bucle_principal(argumentos)
