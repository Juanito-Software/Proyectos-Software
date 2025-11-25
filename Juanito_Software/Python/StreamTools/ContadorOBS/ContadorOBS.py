import keyboard

# Nombre del archivo que OBS leerá como fuente de texto
archivo_texto = "contador.txt"

# Inicializamos contador
contador = 0

# Guardamos el valor inicial en el archivo
with open(archivo_texto, "w", encoding="utf-8") as f:
    f.write(f"Contador macedonios x{contador}")

print("Programa iniciado. Pulsa Ctrl + P para incrementar el contador. (Ctrl + C para salir)")

# Función que incrementa y actualiza el archivo
def incrementar():
    global contador
    contador += 1
    with open(archivo_texto, "w", encoding="utf-8") as f:
        f.write(f"Contador macedonios x{contador}")
    print(f"Actualizado: Contador macedonios x{contador}")

# Escucha Ctrl + P
keyboard.add_hotkey("ctrl+p", incrementar)

# Mantener el programa en ejecución
keyboard.wait()
