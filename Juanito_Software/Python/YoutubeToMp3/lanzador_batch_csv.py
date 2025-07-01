import csv
import subprocess
import os
import sys

def lanzar_descarga(nombre_exe, nombre, url):
    try:
        subprocess.run([nombre_exe, url, nombre], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al procesar {nombre} ({url}): {e}")
    except Exception as e:
        print(f"⚠️ Excepción inesperada en {nombre}: {e}")

if __name__ == "__main__":
    ruta_csv = "descargas.csv"  # Debe tener columnas: nombre,url
    nombre_exe = "YoutubeToMp3.exe"  # Nombre del ejecutable

    if not os.path.exists(nombre_exe):
        print(f"❌ No se encontró el ejecutable: {nombre_exe}")
        sys.exit(1)

    if not os.path.exists(ruta_csv):
        print(f"❌ No se encontró el archivo CSV: {ruta_csv}")
        sys.exit(1)

    with open(ruta_csv, newline='', encoding='utf-8') as csvfile:
        lector = csv.DictReader(csvfile)
        for fila in lector:
            nombre = fila["nombre"].strip()
            url = fila["url"].strip()
            if nombre and url:
                print(f"▶️ Descargando: {nombre} desde {url}")
                lanzar_descarga(nombre_exe, nombre, url)
            else:
                print(f"⚠️ Línea inválida (faltan datos): {fila}")
