# Importar el módulo random para funciones aleatorias
import random

# Estado inicial del tamagochi
energia = 100
estado_actual = {
    "energia": energia
}

# Función saludar
def saludar():
    print("¡Hola, soy un tamagochi!")

# Función estado
def estado():
    print(f"Estado actual:\n\tEnergía: {energia}")

# Función comer
def comer(cantidad):
    global energia
    energia += cantidad
    print(f"Energía incrementada en {cantidad} puntos.")

# Función dormir
def dormir(cantidad):
    global energia
    energia -= cantidad
    print(f"Energía disminuida en {cantidad} puntos.")

# Función jugar
def jugar(cantidad):
    global energia
    energia -= cantidad*2
    print(f"Energía disminuida en {cantidad*2} puntos.")

# Comandos disponibles
comandos = {
    "saludar": saludar,
    "estado": estado,
    "comer": comer,
    "dormir": dormir,
    "jugar": jugar
}

# Función menu
def menu():
    print("Bienvenido al Tamagochi!\nPara comenzar, escribe 'ayuda' para ver los comandos disponibles.")

# Función ayuda
def ayuda():
    print("Comandos disponibles:\n - comer <cantidad>: aumenta la energía del tamagochi en <cantidad> puntos.\n - dormir <cantidad>: disminuye la energía del tamagochi en <cantidad> puntos.\n - jugar <cantidad>: disminuye la energía del tamagochi en <cantidad> puntos.\n - saludar: muestra un mensaje amigable.\n - estado: muestra el estado actual del tamagochi.\n - ayuda: muestra esta ayuda.\n - exit: termina la ejecución del programa.")

# Función parse_command
def parse_command(entrada):
    """
    Parsea la entrada recibida por el usuario y devuelve una función y sus argumentos correspondientes a llamarla.
    Si no se reconoce el comando, devuelve None.
    """
    args = entrada.split()
    if len(args) == 0:
        return None
    cmd = args[0]
    if cmd not in comandos:
        return None
    else:
        return (cmd, args[1:])

# Función run
def run():
    menu()
    while True:
        entrada = input("\n>> ")
        if entrada == "exit":
            break
        cmd = parse_command(entrada)
        if cmd is None:
            print("Comando desconocido. Escribe 'ayuda' para ver los comandos disponibles.")
        else:
            cmd, args = cmd
            try:
                comandos[cmd](*args)
            except TypeError as e:
                print(e)
                print("Uso incorrecto del comando. Escribe 'ayuda' para ver los comandos disponibles.")


if __name__ == "__main__":
    run()